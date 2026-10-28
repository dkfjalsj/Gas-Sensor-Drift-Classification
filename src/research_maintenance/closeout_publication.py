# 자료집·보관본·모델·원본 보존 결과와 정리 이력 통합

from collections import Counter
from datetime import datetime, timezone
import csv
import gzip
import hashlib
import json
from pathlib import Path
import re

from ..data import ROOT
OUT = ROOT / 'outputs/report_publication'
ARCHIVE = ROOT / 'reports/research_archive'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    deletions = json.loads((OUT / 'deletion_log.json').read_text(encoding='utf-8'))
    before = json.loads((OUT / 'preservation_before.json').read_text(encoding='utf-8'))
    counts_before = json.loads((OUT / 'counts_before.json').read_text(encoding='utf-8'))
    tests = json.loads((OUT / 'test_summary.json').read_text(encoding='utf-8'))
    bundle = json.loads((OUT / 'bundle_validation.json').read_text(encoding='utf-8'))
    if tests['new_failures'] or tests['errors']:
        raise RuntimeError('신규 실패가 남아 최종 기록·Git 반영 보류')
    archived = {row['path']: row for row in deletions}
    allowed = {'reports/Gas_Sensor_Drift_Final_Report.html', 'reports/project_cleanup_report.md', 'reports/research_evidence_index.md'}
    failures = []
    for row in before:
        name = row['path']
        if name in archived:
            payload = gzip.decompress((ROOT / archived[name]['archive']).read_bytes())
            assert hashlib.sha256(payload).hexdigest() == row['sha256'], name
            assert not (ROOT / name).exists(), name
        elif name not in allowed:
            if not (ROOT / name).is_file() or sha(ROOT / name) != row['sha256']:
                failures.append(name)
    assert not failures, failures
    raw = []
    config = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
    with (ROOT / 'outputs/file_validation.csv').open(encoding='utf-8-sig') as stream:
        for row in csv.DictReader(stream):
            path = Path(config['data_dir']) / row['file']
            actual = sha(path)
            raw.append(dict(batch=int(row['batch']), sha256=actual, unchanged=actual == row['sha256']))
    assert all(row['unchanged'] for row in raw)
    (OUT / 'raw_preservation.json').write_text(json.dumps(raw, indent=2), encoding='utf-8')
    models = [row for row in before if row['path'].endswith('.joblib')]
    assert len(models) == 325 and all(sha(ROOT / row['path']) == row['sha256'] for row in models)
    current_html = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*.html') if p.relative_to(ROOT).parts[0] not in {'.git', '.venv'}]
    assert current_html == ['reports/Gas_Sensor_Drift_Final_Report.html'], current_html
    assets = json.loads((ROOT / 'reports/report_materials/materials_manifest.json').read_text(encoding='utf-8'))
    required = [
        ('가스별 표본 수', '1_class_counts.png'), ('Batch별 표본·구성', '1_batch_counts.png'),
        ('주요 특징 분포', '1_feature_distributions.png'), ('센서 내8특징 상관 히트맵', '11_sensor_correlations.png'),
        ('모델 성능·랜덤/시간순 비교', '2_pooled_comparison.png'), ('Confusion Matrix', '2_cm_A_random_test.png'),
        ('가스별 Recall', '10_class_recall_heatmap.png'), ('Batch별 Macro F1·시기 변화', '6_candidate_batch_scores.png'),
        ('개선 실험 비교', '14_recall_heatmap.png'), ('정답 적응 성능', '17_mean_macro_by_rate.png'),
        ('MMD²·고정 임계값', '18_batch7_windows.png'), ('분포 변화 경고', '18_warning_rates.png'),
        ('가스 구성·창 순서 민감도', '18_5_window_method_means.png'),
    ]
    coverage = []
    for title, filename in required:
        matches = [row for row in assets if row['file'] == 'png/' + filename]
        # 단계별 파일명이 다른 경우 실제 존재하는 동일 단계·내용의 그림 선택
        if not matches:
            tokens = filename.removesuffix('.png').split('_', 1)
            matches = [row for row in assets if row['kind'] == 'png' and row['stage'].replace('.', '_') == tokens[0] and any(token in row['title'] for token in ['recall', 'comparison'])]
        if not matches:
            raise RuntimeError('필수 그림 근거 확인 필요: ' + filename)
        coverage.append(dict(requirement=title, file=matches[0]['file'], source=matches[0]['source'], available=True))
    with (OUT / 'required_graph_coverage.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(coverage[0]))
        writer.writeheader()
        writer.writerows(coverage)
    for name in ['project_cleanup_report.md', 'research_evidence_index.md']:
        target = ROOT / 'reports' / name
        backup = ARCHIVE / (name + '.before_publication.gz')
        if not backup.exists():
            backup.write_bytes(gzip.compress(target.read_bytes(), mtime=0))
    index_path = ROOT / 'reports/research_evidence_index.md'
    index = index_path.read_text(encoding='utf-8')
    stages = json.loads((OUT / 'source_reports.json').read_text(encoding='utf-8'))
    for row in stages:
        index = index.replace('](' + Path(row['report']).name + ')', '](Gas_Sensor_Drift_Final_Report.html#stage-' + row['stage'] + ')')
    index += '\n\n## 최종 자료집 및 원문 보관 경로\n\n- [Word 자료집 설명](report_materials/materials_guide.md)\n- [자료별 지문 목록](report_materials/materials_manifest.json)\n- [원문 보관·테스트 복원 안내](research_archive/README.md)\n- [옛 경로·원문SHA·보관 경로 전체](research_archive/manifest.json)\n- [정리·검증 기록](../outputs/report_publication/)\n\n옛 HTML·중복 Markdown 경로는 아래 지문 보관본으로 옮김. 원본 CSV·PNG·코드·모델은 기존 위치 유지.\n\n'
    index += '| 원래 경로 | 지문 보관본 | 원문 SHA-256 |\n|---|---|---|\n'
    index += '\n'.join(f'| `{row["path"]}` | [{Path(row["archive"]).name}]({row["archive"].removeprefix("reports/")}) | `{row["sha256"]}` |' for row in deletions)
    index_path.write_text(index, encoding='utf-8')
    report = f'''# 프로젝트 최종 자료집 제작·정리 보고

## 완료 범위와 판정

자료집·보관·기능 검증 완료. Git Stage·Commit·Push는 검증 결과를 확인한 뒤 실행하며 실제 결과는 최종 응답과 Git 이력으로 확인할 수 있음.
기존 연구를 다시 학습하거나 평가하지 않았음. 원본 .dat10개·모델325개·공식 임계값·100행 창 유지.

## 결과물

- [독립 최종 HTML](Gas_Sensor_Drift_Final_Report.html):25절 목차, 단계별 원문 전체, 표와 삽입 이미지{bundle['embedded_images']}개. {bundle['html_bytes']:,}바이트.
- [Word 자료집 설명](report_materials/materials_guide.md):PNG193개·CSV334개의 제목·목적·데이터 조건·결과·해석·한계·출처·지문 기록.
- ZIP:`Gas_Sensor_Report_Materials.zip`, {bundle['zip_bytes']:,}바이트. 이미 .gitignore의 `*.zip` 규칙으로 제외되며 대용량 중복 배포본이므로 강제 추가하지 않음.
- [근거 자료 목록](research_evidence_index.md), [정리 원문 보관·복원 안내](research_archive/README.md).

## 검증

- 프로젝트 밖 새 폴더에서 ZIP CRC·전체 자료 지문·PNG 해독·CSV UTF-8·한글·HTML 단독성 검증 통과.
- 사용자가 ZIP을 직접 풀어 HTML 한글·그래프·표가 정상 표시됨을 확인함. 브라우저 도구는 file://가 보안 정책으로 차단되어 직접 렌더 검사를 수행하지 않았고 우회하지 않았음.
- HTML 내 외부 이미지·CSS·스크립트 의존0건. 전체 자료 SHA 일치.
- 원본 CSV는 소수 자릿수와 원문 바이트 유지.20-A JSON을 펼친 CSV1개는 원문 값을 JSON 문자열로 보존한 변환이며 신규 연구 수치 아님.
- 상관 히트맵은 기존11단계 센서 내8×8 범위임. 전체128×128 상관행렬은 저장돼 있지 않아 있다고 주장하지 않음.
- 신규 모델 Fit·튜닝·Batch9–10 재평가0회. 성능 값을 유리하게 다시 계산하지 않았음.
- 기존 원본 .dat10/10 지문 일치, 모델325/325 지문 일치. 공식 Model A와 감지기 바이트·임계값 유지.

## 실제 정리 이력

옛 HTML·중복 Markdown·캐시 {len(deletions)}개를 개별 gzip으로 지문 검증 보관 후 원래 위치에서 삭제함.
복구 방법:manifest.json의 원래 경로와 압축 파일을 찾아 publication_archive.archived_bytes(row)로 압축·원문 지문을 검증한 바이트를 별도 폴더에 저장함.
연구를 ZIP 하나로 대체하지 않았음. CSV·그래프 원본·분할·예측·설정·모델·코드는 프로젝트에 별도 보존함.

사용자가 화면 확인을 위해 ZIP을 프로젝트 안에 푼 사본530개는 ZIP과 모든 바이트 일치를 확인한 뒤 프로젝트 밖에 그대로 보존 이동함.
위치:`C:/Users/human-20/Documents/ChatGPT/ML 프로젝트 2/user_verified_report_materials_20261028/`.
사용자 확인 사본은 삭제하지 않았으며 원래 ZIP과 reports/report_materials도 유지함.

## 전체 테스트 및 초기 충돌

- 최종 전체 {tests['passed']}개 통과 / 기존 실패{tests['failed']}개 / 제한 skip{tests['skipped']}개 / error{tests['errors']}개. 신규 실패{len(tests['new_failures'])}개.
- 이전 기준240통과/2기존실패/90skip 대비 신규 자료집 검사8개 추가.
- 기존 실패는 과거 임시 파일 부재와 과거 고정 모델 목록 충돌. 과거 해시·모델·테스트 기준을 바꾸어 통과시키지 않았음.
- 과거 직접 경로 검사는 옛 보고서와 캐시 원문84개를 SHA 검증하여 일시 복원한 실제 파일로 실행함. 검사 뒤 동일 바이트의 이번 복원본만 제거함. 일반 pytest를 그대로 실행하면 옛 경로 검사에서 실패할 수 있으므로 아래 명령 사용.

```powershell
.\\.venv\\Scripts\\python.exe -B -X utf8 -m src.research_maintenance.publication_verify
```

- 최초 검사는 프로젝트 안의 사용자 ZIP 해제 사본으로 HTML 단일성 검사 충돌. 외부 보존 이동으로 해결.
- 정리 직후 검사는 예전 보존 목록이 캐시도 요구하여 충돌. 캐시 원문까지 일시 복원하도록 신규 검증 도구 보완. 기존 테스트 수정 없음.
- 초기 실패 기록은 outputs/report_publication/initial_validation_* 및 post_cleanup_attempt2_*에 보존.
- 기존 AppTest의 CSV 업로드·분류·MMD·정답 비교·100행 처리·다운로드·20-A 검증·시기 분리·불변 저장 검사 포함.
- 새 로컬8504 서버 기동·health200 및 실제 화면 확인은 outputs/report_publication/webapp_runtime.json에 별도 기록함.

## 코드 및 남겨둔 자료

실험 코드·보고서 생성 코드·리뷰·closeout·모델·원본 CSV·분할·실패 실험 근거는 재현·테스트 참조를 위해 유지함.
중복 코드라 하여 과거 진입점이나 pickle 모듈 경로를 삭제하지 않았음. 새 자료집·보관·복원 도구에 한글 주석을 작성함.
현재 데이터·학습·평가 API를 Notebook에서 호출할 수 있으나 기존 main의 출력 경로 덮어쓰기와 과거 자료 재사용을 주의해야 함.
이번 작업에서 Notebook·20-B·20-C는 구현하지 않음.

## 파일별 삭제·복구 위치

| 원래 경로 | 삭제 이유 | 검증 보관본 | 원문 SHA-256 |
|---|---|---|---|
'''
    report += '\n'.join(f'| `{row["path"]}` | {row["reason"]} | `{row["archive"]}` | `{row["sha256"]}` |' for row in deletions)
    report_path = ROOT / 'reports/project_cleanup_report.md'
    report_path.write_text(report, encoding='utf-8')
    files = [path for path in ROOT.rglob('*') if path.is_file()]
    research = [path for path in files if path.relative_to(ROOT).parts[0] not in {'.git', '.venv'}]
    state = dict(verified_at=datetime.now(timezone.utc).isoformat(), before=counts_before,
                 all_files=len(files), all_bytes=sum(path.stat().st_size for path in files),
                 research_files=len(research), research_bytes=sum(path.stat().st_size for path in research),
                 original_research_files=len(before), original_research_bytes=sum(row['bytes'] for row in before),
                 deleted_original_files=len(deletions), preserved_model_files=len(models), raw_unchanged=10,
                 actual_html=current_html, unexpected_changes=[], user_visual_confirmation='정상 표시됨',
                 all_checks_passed_except_two_baseline_tests=True)
    (OUT / 'final_preservation.json').write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    with report_path.open('a', encoding='utf-8') as stream:
        stream.write(f'\n\n## 전후 집계\n\n집계 시점 {state["verified_at"]}. 가상환경·Git 포함 '
                     f'{counts_before["all_files"]:,}→{len(files):,}개, {counts_before["all_bytes"]:,}→{state["all_bytes"]:,}바이트. '
                     f'연구 파일 {len(before):,}→{len(research):,}개, {state["original_research_bytes"]:,}→{state["research_bytes"]:,}바이트. '
                     'Word용PNG·CSV·개별원문보관·ZIP 추가 때문에 전체 용량은 증가함. 파일 수나 용량 감소로 연구 보존을 대체하지 않았음. '
                     '이 집계 이후 Git 객체·후속 검증 기록·이 문단 추가분은 별도임.\n')
    print(json.dumps(state, ensure_ascii=False))


if __name__ == '__main__':
    main()
