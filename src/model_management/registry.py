# 수동 승인·원자적 운영 포인터·누적 버전 이력·복구 관리
# 합성 후보의 운영 적용과 검증 자료의 학습 유입 차단

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import uuid

import joblib
import numpy as np
import pandas as pd

from ..common.hashing import sha256_bytes
from ..data import ROOT, FEATURES, GASES
from ..retraining.candidates import (
    STORE, candidate_directory, json_bytes, json_value, pipeline_settings,
    read_candidate, verify_official,
)
from ..retraining.datasets import load_training_data, official_training_frame
from ..retraining.evaluation import evaluate_model
from ..webapp.data_preparation import LOCAL_ROOT
from ..webapp.service import MODEL_PATH, MODEL_SHA

REGISTRY = ROOT / 'data/model_registry'


def now():
    return datetime.now(timezone.utc).isoformat()


# 승인자는 인증된 계정이 아닌 로컬 사용자 확인으로 기록
def evidence_check(evidence):
    required = ['source', 'truth', 'independence']
    if not isinstance(evidence, dict) or any(
        not isinstance(evidence.get(key), str) or len(evidence[key].strip()) < 10
        for key in required
    ):
        raise ValueError('출처·정답·검증 세션 독립성의 확인 근거를 각각 작성해야 합니다.')
    return {key: evidence[key].strip() for key in required}


class ModelRegistry:
    def __init__(self, root=REGISTRY, candidate_store=STORE,
                 dataset_store=LOCAL_ROOT, *, testing=False):
        self.root = Path(root)
        self.candidates = Path(candidate_store)
        self.datasets = Path(dataset_store)
        self.testing = testing
        if testing:
            temporary = Path(tempfile.gettempdir()).resolve()
            for path in [self.root, self.candidates, self.datasets]:
                if not path.resolve().is_relative_to(temporary):
                    raise ValueError('테스트 모드는 시스템 임시 경로 안에서만 허용됩니다.')
        if self.root.is_symlink():
            raise ValueError('연결된 운영 저장소는 허용하지 않습니다.')
        self.path = self.root / 'registry.json'

    @staticmethod
    def official():
        return dict(kind='official', name='Model A / B_SVM_balanced',
                    model_sha256=MODEL_SHA, candidate_id=None, dataset_id=None)

    # 잠금은 이번 요청이 만든 경우에만 해제
    @contextmanager
    def locked(self):
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / 'registry.lock'
        token = uuid.uuid4().hex
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise ValueError('다른 운영 변경이 진행 중이거나 잠금 확인이 필요합니다.') from exc
        with os.fdopen(descriptor, 'w', encoding='ascii') as stream:
            stream.write(token)
        try:
            yield
        finally:
            if path.exists() and path.read_text(encoding='ascii') == token:
                path.unlink()

    # 상태와 전체 이력을 하나의 파일로 함께 확정
    def save(self, state):
        raw = json_bytes(dict(payload=state, sha256=sha256_bytes(json_bytes(state))))
        descriptor, name = tempfile.mkstemp(prefix='.pending_', dir=self.root)
        temporary = Path(name)
        try:
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary.exists():
                temporary.unlink()

    def initialize(self):
        with self.locked():
            if self.path.exists():
                return self.read()
            verify_official()
            state = dict(schema=1, test_environment=self.testing, events=[])
            self.append(state, 'initialize', self.official(), None, None)
            self.save(state)
            return state

    # 이력 해시 연결과 현재 포인터 대응을 확인하며 손상 시 자동 대체하지 않음
    def read(self):
        envelope = json.loads(self.path.read_bytes())
        state = envelope['payload']
        if sha256_bytes(json_bytes(state)) != envelope['sha256']:
            raise ValueError('운영 매니페스트 지문이 다릅니다.')
        if (state['schema'] != 1 or state['test_environment'] is not self.testing
                or not state['events']):
            raise ValueError('운영 매니페스트 환경·버전이 다릅니다.')
        previous = None
        for event in state['events']:
            copy = dict(event)
            digest = copy.pop('sha256')
            if copy['previous_event_sha256'] != previous or sha256_bytes(json_bytes(copy)) != digest:
                raise ValueError('운영 모델 이력이 손상됐습니다.')
            previous = digest
        if state['active'] != state['events'][-1]['version']:
            raise ValueError('운영 포인터와 마지막 이력이 다릅니다.')
        return state

    def append(self, state, action, descriptor, previous, details):
        event_id = 'version_' + uuid.uuid4().hex
        version = dict(version_id=event_id, applied_at_utc=now(), model=descriptor)
        event = dict(action=action, version=version, previous_version_id=previous,
                     details=details, actor='local_user_not_authenticated',
                     previous_event_sha256=(state['events'][-1]['sha256'] if state['events'] else None))
        event['sha256'] = sha256_bytes(json_bytes(event))
        state['events'].append(event)
        state['active'] = version
        return version

    # 후보 경로는 사용자 입력 경로 대신 검증된 ID에서 결정
    def model_path(self, descriptor):
        if descriptor['kind'] == 'official':
            if descriptor != self.official():
                raise ValueError('Model A 설명 정보가 다릅니다.')
            return MODEL_PATH
        if descriptor['kind'] != 'candidate':
            raise ValueError('알 수 없는 운영 모델 종류입니다.')
        item = read_candidate(descriptor['candidate_id'], self.candidates)
        meta = item['metadata']
        if (meta['candidate_model_sha256'] != descriptor['model_sha256']
                or sha256_bytes((item['directory'] / 'manifest.json').read_bytes())
                != descriptor['candidate_manifest_sha256']
                or meta['dataset_id'] != descriptor['dataset_id']):
            raise ValueError('운영 후보의 기록 지문이 다릅니다.')
        if meta['synthetic_only'] and not self.testing:
            raise ValueError('합성 후보는 운영에서 사용할 수 없습니다.')
        return item['directory'] / 'model.joblib'

    # 버전별 캐시를 사용하더라도 새 분석 전에 파일 지문 재검사
    def validate_version(self, version):
        path = self.model_path(version['model'])
        if not path.is_file() or path.is_symlink() or sha256_bytes(path.read_bytes()) != version['model']['model_sha256']:
            raise ValueError('운영 모델 파일이 없거나 지문이 다릅니다.')
        return path

    def load_version(self, version):
        path = self.validate_version(version)
        model = joblib.load(path)
        pipeline_settings(model)
        probe = pd.DataFrame(np.zeros((1, 128)), columns=FEATURES)
        predicted = model.predict(probe)
        if len(predicted) != 1 or int(predicted[0]) not in GASES:
            raise ValueError('128개 특징 입력·6종 가스 출력 검사를 통과하지 못했습니다.')
        return model

    def current(self):
        version = self.read()['active']
        self.validate_version(version)
        return version

    # 20-B 학습 기록과 실제 전처리 통계를 결합 Train에서 대조
    def training_audit(self, item, data):
        meta, model = item['metadata'], item['model']
        base, _ = official_training_frame(data.reference)
        train = pd.concat([base, data.train_x], ignore_index=True)
        audit = meta['preprocessing_audit']
        if (meta['dataset_manifest_sha256'] != data.manifest_sha
                or meta['dataset_file_hashes'] != data.manifest['files']
                or meta['validation_fitted'] is not False
                or meta['hyperparameter_search'] is not False
                or meta['feature_contract_confirmed'] is not True
                or meta['fitted_rows'] != len(train)
                or audit['combined_feature_sha256'] != sha256_bytes(train.to_numpy(dtype='<f8').tobytes())
                or audit['validation_row_ids'] != data.assignments.loc[
                    data.assignments.partition.eq('validation'), 'row_id'].tolist()):
            raise ValueError('후보의 데이터셋·학습·검증 분리 기록이 다릅니다.')
        imputer, scaler = model.named_steps['imputer'], model.named_steps['scaler']
        np.testing.assert_allclose(imputer.statistics_, np.nanmedian(train, axis=0))
        values = imputer.transform(train)
        np.testing.assert_allclose(scaler.mean_, values.mean(axis=0), rtol=1e-10, atol=1e-10)
        np.testing.assert_allclose(scaler.var_, values.var(axis=0), rtol=1e-10, atol=1e-10)
        if scaler.n_samples_seen_ != len(train):
            raise ValueError('Train 외 전처리 학습 가능성이 있습니다.')

    # 같은 신규 Validation에서 현재 모델과 후보를 다시 비교
    def review(self, candidate_id, evidence=None):
        version = self.current()
        item = read_candidate(candidate_id, self.candidates, load_model=True)
        meta = item['metadata']
        data = load_training_data(meta['dataset_id'], self.datasets)
        self.training_audit(item, data)
        current = evaluate_model(self.load_version(version), data.validation_x, data.validation_y)
        candidate = evaluate_model(item['model'], data.validation_x, data.validation_y)
        original = meta['metrics']['candidate']
        for metric in ['accuracy', 'macro_f1', 'weighted_f1']:
            if not np.isclose(candidate[0][metric], original[metric], rtol=0, atol=1e-12):
                raise ValueError('저장된 후보 평가값이 재계산 결과와 다릅니다.')
        if not np.array_equal(candidate[3], pd.read_csv(item['directory'] / 'predictions.csv').candidate):
            raise ValueError('저장된 후보 예측을 재현하지 못했습니다.')
        reasons = []
        text = json.dumps(meta['dataset_provenance'], ensure_ascii=False).lower()
        synthetic = meta['synthetic_only'] or any(word in text for word in ['synthetic', 'known_generator', '합성'])
        if synthetic and not self.testing:
            reasons.append('합성 후보는 실제 운영 모델로 적용할 수 없음')
        if candidate[0]['macro_f1'] < current[0]['macro_f1']:
            reasons.append('동일 Validation에서 후보 Macro F1이 현재 운영 모델보다 낮음')
        if candidate[0]['macro_f1'] < meta['metrics']['official']['macro_f1']:
            reasons.append('20-B 기준 Model A 대비 Macro F1 개선 조건 미달')
        try:
            confirmed_evidence = evidence_check(evidence)
        except ValueError as exc:
            confirmed_evidence = None
            reasons.append(str(exc))
        changes = candidate[1][['gas', 'support', 'recall']].rename(columns={'recall': 'candidate_recall'})
        changes['current_recall'] = current[1].recall.to_numpy()
        changes['recall_delta'] = changes.candidate_recall - changes.current_recall
        descriptor = dict(kind='candidate', name=candidate_id,
                          model_sha256=meta['candidate_model_sha256'], candidate_id=candidate_id,
                          dataset_id=meta['dataset_id'],
                          candidate_manifest_sha256=sha256_bytes((item['directory'] / 'manifest.json').read_bytes()))
        token = sha256_bytes(json_bytes(dict(active=version, candidate=descriptor,
                                            dataset=data.manifest_sha,
                                            evidence=confirmed_evidence,
                                            current_macro=current[0]['macro_f1'],
                                            candidate_macro=candidate[0]['macro_f1'])))
        return dict(eligible=not reasons, reasons=reasons, token=token, active=version,
                    descriptor=descriptor, dataset_manifest_sha256=data.manifest_sha,
                    current=current, candidate=candidate, changes=changes,
                    evidence=confirmed_evidence, synthetic=bool(synthetic))

    # 확인한 현재 버전과 비교 결과가 그대로일 때만 한 번 적용
    def activate(self, candidate_id, *, confirmed, evidence, expected_version,
                 comparison_token, preflight=None):
        if confirmed is not True:
            raise ValueError('운영 모델 변경 확인이 필요합니다.')
        with self.locked():
            state = self.read()
            if state['active']['version_id'] != expected_version:
                raise ValueError('현재 모델이 변경됐습니다. 다시 비교해 주세요.')
            result = self.review(candidate_id, evidence)
            if not result['eligible']:
                raise ValueError(' / '.join(result['reasons']))
            if result['token'] != comparison_token:
                raise ValueError('비교 정보가 변경됐습니다. 다시 비교해 주세요.')
            if state['active']['model']['model_sha256'] == result['descriptor']['model_sha256']:
                raise ValueError('이미 같은 모델이 적용돼 있습니다.')
            details = dict(candidate_id=candidate_id,
                           dataset_manifest_sha256=result['dataset_manifest_sha256'],
                           confirmation_evidence=result['evidence'],
                           evidence_status='local_operator_declaration_not_external_certification',
                           comparison_token=result['token'],
                           current_metrics=result['current'][0], candidate_metrics=result['candidate'][0],
                           recall_changes=result['changes'].to_dict('records'),
                           independent_final_test=False, synthetic_test_only=result['synthetic'])
            version = self.append(state, 'activate', result['descriptor'], expected_version, details)
            self.load_version(version)
            if preflight:
                preflight(version)
            self.save(state)
            return version

    # 과거 적용된 버전만 선택하며 복구도 새 이벤트로 누적
    def rollback(self, target_version, *, confirmed, expected_version, preflight=None):
        if confirmed is not True:
            raise ValueError('이전 모델 복구 확인이 필요합니다.')
        with self.locked():
            state = self.read()
            if state['active']['version_id'] != expected_version:
                raise ValueError('현재 모델이 변경됐습니다. 다시 확인해 주세요.')
            matches = [event['version'] for event in state['events']
                       if event['version']['version_id'] == target_version]
            if not matches:
                raise ValueError('복구 대상은 기존 적용 이력에서 선택해야 합니다.')
            target = matches[0]
            if target['model'] == state['active']['model']:
                raise ValueError('이미 현재 사용 중인 모델입니다.')
            version = self.append(state, 'rollback', target['model'], expected_version,
                                  dict(restored_from_version=target_version))
            self.load_version(version)
            if preflight:
                preflight(version)
            self.save(state)
            return version
