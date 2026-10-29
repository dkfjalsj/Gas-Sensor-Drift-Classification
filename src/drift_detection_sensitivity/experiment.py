# 저장 감지기로 창 재배열·가스 구성 통제의 민감도 계산
# 라벨 기반 진단과 무라벨 점수 입력 분리 및 기존 파일 보존

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from ..data import ROOT, FEATURES, GASES, parse_line, read_config

OUT = ROOT / "outputs/drift_detection_sensitivity"
OLD = ROOT / "outputs/drift_detection"
DETECTOR = ROOT / "models/drift_detection/rff_mmd_v1.joblib"
OFFICIAL = ROOT / "models/temporal_expansion/B_SVM_balanced.joblib"
SEEDS = [42, 43, 44, 45, 46]
THRESHOLD = 0.00825701197565701
CAUTION = ("고정 감지기의 사후 민감도 진단이며 실제 센서 드리프트 탐지 정확도 검증 아님. "
           "라벨 기반 구성 통제는 운영용 무라벨 평가가 아님. 반복 개발 자료이며 독립 Test 없음. "
           "Batch9~10 원본 읽기·평가 없음. 모델·임계값 변경 없음.")


# 새 결과만 UTF-8로 저장
def write(name, value):
    def convert(item):
        if isinstance(item, np.generic):
            return item.item()
        if isinstance(item, np.ndarray):
            return item.tolist()
        raise TypeError(type(item).__name__)
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False,
                                      default=convert), encoding="utf-8")


def save(name, rows):
    table = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows)
    table.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8")
    return table


# 신규 분석 결과를 제외한 파일 지문 수집


# 새 점수 산출 전 분석 조건과 판정 규칙 고정


# 기존 형식 파서로 허용된8개 Batch만 불러오기
def load_allowed():
    rows = []
    raw = Path(read_config()["data_dir"])
    for batch in range(1, 9):
        for source_line, line in enumerate((raw / f"batch{batch}.dat").read_text(encoding="utf-8").splitlines(), 1):
            gas, values = parse_line(line)
            rows.append([f"b{batch:02d}_r{source_line:05d}", batch, source_line, gas, *values])
    return pd.DataFrame(rows, columns=["row_id", "batch", "source_line", "gas", *FEATURES])


# 기준 가스 비율을100개 정수 할당량으로 변환
def quotas_from_reference(proportions):
    if len(proportions) != 6 or not np.isfinite(proportions).all() or not np.isclose(np.sum(proportions), 1):
        raise ValueError("유효한6종 비율 필요")
    ideal = np.asarray(proportions, dtype=float) * 100
    counts = np.floor(ideal).astype(int)
    remaining = 100 - counts.sum()
    order = sorted(range(6), key=lambda i: (-(ideal[i] - counts[i]), i))
    for i in order[:remaining]:
        counts[i] += 1
    if counts.sum() != 100 or (counts < 1).any():
        raise ValueError("6종을 포함한100행 할당 불가")
    return counts


# 동일 행 집합 재배열과 전체 Batch 재배열 구분
def shuffle_rows(sub, seed, fixed_rows=False):
    used = len(sub) // 100 * 100 if fixed_rows else len(sub)
    order = np.random.default_rng(np.random.SeedSequence([seed, int(sub.batch.iloc[0])])).permutation(used)
    return pd.concat([sub.iloc[order], sub.iloc[used:]])


# 가스별 표본을 복제 없이 뽑아 같은 구성의 창 생성
def controlled_rows(sub, quota, n_windows, seed, target, source_code):
    selected = []
    for i, gas in enumerate(GASES):
        ids = sub.index[sub.gas == gas].to_numpy()
        order = np.random.default_rng(np.random.SeedSequence([seed, target, source_code, gas])).permutation(ids)
        if len(order) < n_windows * quota[i]:
            raise ValueError("구성 통제 표본 부족")
        selected.append(order[:n_windows * quota[i]].reshape(n_windows, quota[i]))
    ids = np.concatenate([np.concatenate([g[w] for g in selected]) for w in range(n_windows)])
    if len(ids) != len(set(ids)):
        raise AssertionError("구성 통제 표본 중복")
    return sub.loc[ids]


# 기존 파일·모델·계획 보존 확인 (원본9~10 열지 않음)


# 조건별 창 요약과 가스 구성 기록
def evaluate_condition(detector, sub, method, seed, target, source, reference_proportions):
    result = detector.evaluate(sub[FEATURES])
    assert result["valid_windows"] == len(sub) // 100 and result["invalid_windows"] == 0
    windows, members, gas_rows, means = [], [], [], []
    for pos, row in enumerate(sub.itertuples(), 1):
        members.append(dict(method=method, seed=seed, target=target, source=source,
                            row_id=row.row_id, batch=int(row.batch), source_line=int(row.source_line),
                            gas_id=int(row.gas), position=pos,
                            window=(pos - 1) // 100 + 1 if pos <= result["valid_windows"] * 100 else 0))
    for item in result["windows"]:
        piece = sub.iloc[item["start_position"] - 1:item["end_position"]]
        proportions = piece.gas.value_counts(normalize=True).reindex(GASES, fill_value=0)
        tv = float(np.abs(proportions.to_numpy() - reference_proportions).sum() / 2)
        meta = dict(method=method, seed=seed, target=target, source=source, window=item["window"])
        windows.append(dict(**meta, score=item["score"], alert=item["alert"], n=100,
                            gas_classes=int(piece.gas.nunique()), mixture_tv=tv))
        gas_rows.extend(dict(**meta, gas_id=g, n=int((piece.gas == g).sum()), proportion=float(proportions[g])) for g in GASES)
        values = detector.scaler.transform(detector.imputer.transform(piece[FEATURES]))
        means.append(detector.rff.transform(values).mean(axis=0))
    embedding_means = np.asarray(means)
    global_mean = embedding_means.mean(axis=0)
    global_score = float(np.square(global_mean - detector.reference_mean_).sum())
    between = float(np.square(embedding_means - global_mean).sum(axis=1).mean())
    scores = np.asarray([w["score"] for w in windows])
    np.testing.assert_allclose(scores.mean(), global_score + between, rtol=1e-10, atol=1e-14)
    summary = dict(method=method, seed=seed, target=target, source=source,
        input_rows=len(sub), used_rows=len(windows) * 100, windows=len(windows),
        excluded_tail_rows=result["excluded_tail_rows"], mean_score=float(scores.mean()),
        median_score=float(np.median(scores)), min_score=float(scores.min()), max_score=float(scores.max()),
        alert_windows=result["alert_windows"], alert_rate=result["alert_rate"],
        mean_tv=float(np.mean([w["mixture_tv"] for w in windows])),
        mean_gas_classes=float(np.mean([w["gas_classes"] for w in windows])),
        global_mean_distance_squared=global_score, between_window_variation=between)
    return summary, windows, members, gas_rows


# 저장된 원본 창 점수에만 정답 구성·오류 정보를 결합
def analyze_existing(reference_proportions):
    old = pd.read_csv(OLD / "window_error_analysis.csv")
    supports = pd.read_csv(OLD / "window_gas_support.csv")
    supports = supports[supports.partition.isin(["batch7", "batch8"])].copy()
    supports["proportion"] = supports.n / 100
    rows = []
    for row in old.itertuples():
        sub = supports[(supports.partition == row.partition) & (supports.window == row.window)].set_index("gas_id").loc[list(GASES)]
        tv = float(np.abs(sub.proportion.to_numpy() - reference_proportions).sum() / 2)
        assert np.isclose(tv, row.mixture_total_variation)
        rows.append(dict(partition=row.partition, window=row.window, score=row.score, alert=row.alert,
                         gas_classes=int((sub.n > 0).sum()), mixture_tv=tv, error_n=row.error_n,
                         error_rate=row.error_rate, **{f"gas{g}_proportion": float(sub.loc[g, "proportion"]) for g in GASES}))
    table = save("existing_window_analysis", rows)
    associations = []
    for scope, sub in [("pooled_7_8", table), ("batch7", table[table.partition == "batch7"]),
                       ("batch8", table[table.partition == "batch8"])]:
        for variable in ["mixture_tv", "gas_classes", "error_rate"]:
            enough = len(sub) >= 3 and sub.score.nunique() > 1 and sub[variable].nunique() > 1
            associations.append(dict(scope=scope, variable=variable, windows=len(sub),
                spearman=float(spearmanr(sub.score, sub[variable]).statistic) if enough else None,
                inferential=False, note="descriptive" if enough else "insufficient/constant"))
    save("existing_associations", associations)


# 정해진 조건과 모든 시드 한 번 실행


# 이번 제한으로 건너뛴 검사와 역사적 실패 구분




