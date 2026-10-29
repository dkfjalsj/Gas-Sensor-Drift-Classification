# 연구용 모델의 실제 재로딩 의존성과 정리 전 예측 지문 회귀 검사
# 3개 기존 입력에 대한 동일성 확인이며 새 성능 실험이 아님
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from src.data import ROOT, FEATURES, read_config, parse_line


def test_all_preserved_models_reload_and_reproduce_original_predictions():
    baseline = json.loads((ROOT / 'research/model_replay.json').read_text(encoding='utf-8'))
    path = Path(read_config()['data_dir']) / 'batch7.dat'
    rows = [parse_line(line)[1] for line in path.read_text().splitlines()[:3]]
    features = pd.DataFrame(rows, columns=FEATURES)
    assert set(baseline) == {p.relative_to(ROOT).as_posix() for p in (ROOT / 'models').rglob('*.joblib')}
    with threadpool_limits(limits=1):
        for relative, expected in baseline.items():
            model = joblib.load(ROOT / relative)
            if hasattr(model, 'predict'):
                output = dict(predicted=np.asarray(model.predict(features)).tolist())
            elif hasattr(model, 'evaluate'):
                output = model.evaluate(pd.concat([features] * 34, ignore_index=True))
            else:
                output = dict(type=type(model).__module__ + '.' + type(model).__name__,
                              object_hash=joblib.hash(model))
            assert expected['ok'] and output == expected['output'], relative
