# 원본 파일의 형식과 검증 결과가 맞는지 확인합니다.
# 중요한 처리 순서를 짧은 한글 주석으로 설명합니다.
import json
import numpy as np
import pandas as pd
import pytest
from src.data import ROOT, FEATURES, GASES, parse_line, read_config, load_dataset, duplicate_summary
from src.analysis import audit_split, build_split_audits

# 형식 검사용 예제 한 줄을 만듭니다.
def valid_line():
    return '1 ' + ' '.join(f'{i}:{i*.5}' for i in range(1,129))

# 예상한 결과가 나오는지 확인합니다.
def test_parser_preserves_values_and_whitespace():
    label, values = parse_line(valid_line().replace(' ', '\t')+'  ')
    assert label == 1 and len(values) == 128
    assert values[0] == .5 and values[-1] == 64

@pytest.mark.parametrize('line', [
    '', '1 1:0', valid_line().replace('128:64.0', '127:64.0'),
    valid_line().replace('1 1:', '7 1:'), valid_line().replace('1 1:', '1;10 1:'),
    valid_line().replace('12:6.0', '12:bad'), valid_line().replace('1:0.5 2:1.0', '2:1.0 1:0.5')
])
# 예상한 결과가 나오는지 확인합니다.
def test_malformed_rows_fail_explicitly(line):
    with pytest.raises(ValueError):
        parse_line(line)

# 예상한 결과가 나오는지 확인합니다.
def test_nonfinite_values_not_silently_converted_to_zero():
    _, values = parse_line(valid_line().replace('1:0.5', '1:nan').replace('2:1.0', '2:inf'))
    assert np.isnan(values[0]) and np.isinf(values[1])

# 예상한 결과가 나오는지 확인합니다.
def test_missing_file_is_explicit(tmp_path):
    with pytest.raises(FileNotFoundError, match='batch1.dat'):
        load_dataset({'data_dir':str(tmp_path),'n_features':128})

@pytest.fixture(scope='session')
# 테스트에 사용할 원본 자료를 읽습니다.
def dataset():
    return load_dataset(read_config())

# 예상한 결과가 나오는지 확인합니다.
def test_real_structure_and_expected_totals(dataset):
    frame, files = dataset
    assert len(frame) == 13910
    assert len(FEATURES) == 128
    assert set(frame.gas) == set(GASES)
    assert files.samples.tolist() == [445,1244,1586,161,197,2300,3613,294,470,3600]
    assert np.isfinite(frame[FEATURES].to_numpy()).all()
    assert frame.row_id.is_unique
    for batch, group in frame.groupby('batch'):
        assert group.source_line.tolist() == list(range(1,len(group)+1))

# 예상한 결과가 나오는지 확인합니다.
def test_duplicates_and_split_detection():
    frame = pd.DataFrame(np.zeros((4,128)),columns=FEATURES)
    frame['batch'] = [1,1,2,2]
    frame['gas'] = [1,1,1,2]
    groups, result = duplicate_summary(frame)
    assert result['feature_duplicate_extra'] == 3
    assert result['conflicting_label_groups'] == 1
    assert result['cross_batch_duplicate_groups'] == 1
    split = audit_split(frame, np.array([0,1]), np.array([2,3]), 'fixture', groups)
    assert split['duplicate_feature_groups'] == 1
    assert split['test_rows_matching_train'] == 2
    assert split['missing_train'] == [2,3,4,5,6]

# 예상한 결과가 나오는지 확인합니다.
def test_report_numbers_and_source_integrity(dataset):
    frame, files = dataset
    summary = json.loads((ROOT/'outputs/validation_summary.json').read_text(encoding='utf-8'))
    assert summary['samples'] == len(frame)
    counts = pd.read_csv(ROOT/'outputs/batch_class_counts.csv',index_col=0)
    assert counts.to_numpy().sum() == len(frame)
    assert counts.loc[[3,4,5], 'Toluene'].eq(0).all()
    recorded = pd.read_csv(ROOT/'outputs/file_validation.csv')
    assert recorded.sha256.tolist() == files.sha256.tolist()

# 예상한 결과가 나오는지 확인합니다.
def test_saved_splits_reproducible_and_temporal(dataset):
    frame, _ = dataset
    groups = pd.util.hash_pandas_object(frame[FEATURES], index=False).astype(str)
    computed, assignments = build_split_audits(frame,groups,42)
    saved = json.loads((ROOT/'outputs/split_audit.json').read_text(encoding='utf-8'))
    assert computed == saved
    manifest = pd.read_csv(ROOT/'outputs/split_manifest.csv', dtype={'feature_group':str})
    assert manifest.equals(assignments)
    assert all(row['row_overlap'] == 0 for row in saved)
    for split in saved:
        if split['name'].startswith('B_'):
            assert max(split['train_batches']) < min(split['test_batches'])
    assert saved[0]['missing_train'] == [] and saved[0]['missing_test'] == []
