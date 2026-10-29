# 비선형 특징 변환의 누수·보호 기준·모델 재현 및 보존 검사


import numpy as np
import pytest

from src.nonlinear_feature_transformation import TrainTransform, digest


# 이번 단계 결과와 실제 학습 행 공유






# 음수·영·양수 부호와 특징 순서 유지
@pytest.mark.parametrize('method', ['signed_log', 'yeo_johnson'])
def test_signed_zero_positive_and_order(method):
    values = np.array([[-4., 0., -2.], [-1., 0., 0.], [0., 0., 1.], [5., 0., 7.]])
    transformer = TrainTransform(method).fit(values)
    result = transformer.transform(values)
    assert result.shape == values.shape and np.isfinite(result).all()
    assert (np.diff(result[:, 0]) > 0).all()
    assert result[0, 0] < 0 and result[2, 0] == 0 and result[3, 0] > 0
    np.testing.assert_array_equal(transformer.get_feature_names_out(['a', 'b', 'c']), ['a', 'b', 'c'])
    np.testing.assert_array_equal(result[:, 1], np.zeros(4))


def test_constant_and_tiny_scale_rules():
    values = np.array([[0., 3., 1e-300], [0., 3., -1e-300], [0., 3., 0.]])
    log = TrainTransform('signed_log').fit(values)
    assert (log.scale_ >= 1e-12).all()
    np.testing.assert_allclose(log.transform(values), np.sign(values)*np.log1p(np.abs(values)/log.scale_))
    yj = TrainTransform('yeo_johnson').fit(values)
    assert yj.status_[:2] == ['constant_identity', 'constant_identity']
    assert np.isfinite(yj.transform(values)).all()


def test_transform_does_not_update_on_future_values():
    values = np.arange(48., dtype=float).reshape(12, 4)-12
    for method in ['signed_log', 'yeo_johnson']:
        transformer = TrainTransform(method).fit(values)
        before = (transformer.fit_input_sha256_, transformer.scale_.copy(), transformer.lambdas_.copy())
        transformer.transform(values * 10)
        assert transformer.fit_input_sha256_ == before[0] == digest(values)
        np.testing.assert_array_equal(transformer.scale_, before[1])
        np.testing.assert_array_equal(transformer.lambdas_, before[2])


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError):
        TrainTransform().fit([[np.nan, 2.]])
    transformer = TrainTransform().fit([[0., 2.], [1., 3.]])
    with pytest.raises(ValueError):
        transformer.transform([[1., 2., 3.]])
    with pytest.raises(ValueError):
        transformer.transform([[np.inf, 1.]])
























