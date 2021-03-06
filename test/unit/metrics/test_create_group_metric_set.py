# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import numpy as np
import pytest

from fairlearn.metrics import group_accuracy_score, group_roc_auc_score
from fairlearn.metrics import create_group_metric_set

from test.unit.input_convertors import conversions_for_1d


def test_bad_model_type():
    with pytest.raises(ValueError) as exception_context:
        create_group_metric_set("Something Random", None, None, None)
    expected = "model_type 'Something Random' not in ['binary_classification', 'regression']"
    assert exception_context.value.args[0] == expected


def test_smoke():
    # Single model, single sensitive feature vector, no names
    Y_true = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0]
    Y_pred = [[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1]]
    sensitive_feature = [['a', 'b', 'b', 'a', 'b', 'b', 'b', 'a', 'b', 'b', 'b']]
    sf_int = [int(x == 'b') for x in sensitive_feature[0]]

    result = create_group_metric_set('binary_classification', Y_true, Y_pred, sensitive_feature)
    assert result['predictionType'] == 'binaryClassification'
    assert result['schemaType'] == 'groupMetricSet'
    assert result['schemaVersion'] == 0

    assert isinstance(result['trueY'], list)
    assert np.array_equal(result['trueY'], Y_true)

    assert isinstance(result['precomputedFeatureBins'], list)
    assert len(result['precomputedFeatureBins']) == 1
    bin_dict = result['precomputedFeatureBins'][0]
    assert isinstance(bin_dict, dict)
    assert np.array_equal(bin_dict['binVector'], sf_int)
    assert np.array_equal(bin_dict['binLabels'], ['a', 'b'])

    assert isinstance(result['predictedY'], list)
    assert len(result['predictedY']) == 1
    y_p = result['predictedY'][0]
    assert isinstance(y_p, list)
    assert np.array_equal(y_p, Y_pred[0])

    assert isinstance(result['precomputedMetrics'], list)
    assert len(result['precomputedMetrics']) == 1
    metrics_group_0 = result['precomputedMetrics'][0]
    assert isinstance(metrics_group_0, list)
    assert len(metrics_group_0) == 1
    metrics_g0_m0 = metrics_group_0[0]
    assert isinstance(metrics_g0_m0, dict)
    assert len(metrics_g0_m0) == 10

    accuracy = metrics_g0_m0['accuracy_score']
    assert isinstance(accuracy, dict)
    gmr = group_accuracy_score(Y_true, Y_pred[0], sensitive_feature[0])
    assert gmr.overall == pytest.approx(accuracy['global'])
    assert isinstance(accuracy['bins'], list)
    assert len(accuracy['bins']) == 2
    assert gmr.by_group['a'] == pytest.approx(accuracy['bins'][0])
    assert gmr.by_group['b'] == pytest.approx(accuracy['bins'][1])

    roc_auc = metrics_g0_m0['balanced_accuracy_score']
    assert isinstance(roc_auc, dict)
    gmr = group_roc_auc_score(Y_true, Y_pred[0], sensitive_feature[0])
    assert gmr.overall == pytest.approx(roc_auc['global'])
    assert isinstance(roc_auc['bins'], list)
    assert len(roc_auc['bins']) == 2
    assert gmr.by_group['a'] == pytest.approx(roc_auc['bins'][0])
    assert gmr.by_group['b'] == pytest.approx(roc_auc['bins'][1])


def test_two_models():
    # Two models, single sensitive feature vector, no names
    Y_true = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1]
    Y_pred = [[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1],
              [1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0]]
    a, b = 'a', 'b'
    sensitive_features = [[b, a, a, b, b, a, a, b, b, a, b, a, b, a, b]]
    sf_int = [int(x == 'b') for x in sensitive_features[0]]

    result = create_group_metric_set('binary_classification', Y_true, Y_pred, sensitive_features)
    assert result['predictionType'] == 'binaryClassification'
    assert result['schemaType'] == 'groupMetricSet'
    assert result['schemaVersion'] == 0

    assert isinstance(result['trueY'], list)
    assert np.array_equal(result['trueY'], Y_true)

    assert isinstance(result['precomputedFeatureBins'], list)
    assert len(result['precomputedFeatureBins']) == 1
    bin_dict = result['precomputedFeatureBins'][0]
    assert isinstance(bin_dict, dict)
    assert np.array_equal(bin_dict['binVector'], sf_int)
    assert np.array_equal(bin_dict['binLabels'], ['a', 'b'])

    assert isinstance(result['predictedY'], list)
    assert len(result['predictedY']) == 2
    for i in range(2):
        y_p = result['predictedY'][i]
        assert isinstance(y_p, list)
        assert np.array_equal(y_p, Y_pred[i])

    assert isinstance(result['precomputedMetrics'], list)
    assert len(result['precomputedMetrics']) == 1
    metrics_group_0 = result['precomputedMetrics'][0]
    assert isinstance(metrics_group_0, list)
    assert len(metrics_group_0) == 2
    for i in range(2):
        metrics_g0_m0 = metrics_group_0[i]
        assert isinstance(metrics_g0_m0, dict)
        assert len(metrics_g0_m0) == 10

        accuracy = metrics_g0_m0['accuracy_score']
        assert isinstance(accuracy, dict)
        gmr = group_accuracy_score(Y_true, Y_pred[i], sensitive_features[0])
        assert gmr.overall == pytest.approx(accuracy['global'])
        assert isinstance(accuracy['bins'], list)
        assert len(accuracy['bins']) == 2
        assert gmr.by_group['a'] == pytest.approx(accuracy['bins'][0])
        assert gmr.by_group['b'] == pytest.approx(accuracy['bins'][1])

        roc_auc = metrics_g0_m0['balanced_accuracy_score']
        assert isinstance(roc_auc, dict)
        gmr = group_roc_auc_score(Y_true, Y_pred[i], sensitive_features[0])
        assert gmr.overall == pytest.approx(roc_auc['global'])
        assert isinstance(roc_auc['bins'], list)
        assert len(roc_auc['bins']) == 2
        assert gmr.by_group['a'] == pytest.approx(roc_auc['bins'][0])
        assert gmr.by_group['b'] == pytest.approx(roc_auc['bins'][1])


def test_two_sensitive_features():
    # Single model, two sensitive feature vectors, no names
    Y_true = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0]
    Y_pred = [[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1]]
    # First sensitive feature is just 'a' and 'b'. Second is 4, 5 and 6
    sensitive_features = [['b', 'a', 'a', 'a', 'b', 'b', 'b', 'a', 'b', 'b', 'b'],
                          [4, 5, 6, 6, 5, 4, 4, 5, 5, 6, 6]]
    sf_int = [int(x == 'b') for x in sensitive_features[0]]

    result = create_group_metric_set('binary_classification', Y_true, Y_pred, sensitive_features)
    assert result['predictionType'] == 'binaryClassification'
    assert result['schemaType'] == 'groupMetricSet'
    assert result['schemaVersion'] == 0

    assert isinstance(result['trueY'], list)
    assert np.array_equal(result['trueY'], Y_true)

    assert isinstance(result['precomputedFeatureBins'], list)
    assert len(result['precomputedFeatureBins']) == 2
    bin_dict0 = result['precomputedFeatureBins'][0]
    assert isinstance(bin_dict0, dict)
    assert np.array_equal(bin_dict0['binVector'], sf_int)
    assert np.array_equal(bin_dict0['binLabels'], ['a', 'b'])
    bin_dict1 = result['precomputedFeatureBins'][1]
    assert isinstance(bin_dict1, dict)
    assert np.array_equal(bin_dict1['binVector'], [x-4 for x in sensitive_features[1]])
    assert np.array_equal(bin_dict1['binLabels'], ['4', '5', '6'])

    assert isinstance(result['predictedY'], list)
    assert len(result['predictedY']) == 1
    y_p = result['predictedY'][0]
    assert isinstance(y_p, list)
    assert np.array_equal(y_p, Y_pred[0])

    assert isinstance(result['precomputedMetrics'], list)
    assert len(result['precomputedMetrics']) == 2

    # Check the first grouping (with alphabetical labels)
    metrics_group_0 = result['precomputedMetrics'][0]
    assert isinstance(metrics_group_0, list)
    assert len(metrics_group_0) == 1
    metrics_g0_m0 = metrics_group_0[0]
    assert isinstance(metrics_g0_m0, dict)
    assert len(metrics_g0_m0) == 10

    accuracy = metrics_g0_m0['accuracy_score']
    assert isinstance(accuracy, dict)
    gmr = group_accuracy_score(Y_true, Y_pred[0], sensitive_features[0])
    assert gmr.overall == pytest.approx(accuracy['global'])
    assert isinstance(accuracy['bins'], list)
    assert len(accuracy['bins']) == 2
    assert gmr.by_group['a'] == pytest.approx(accuracy['bins'][0])
    assert gmr.by_group['b'] == pytest.approx(accuracy['bins'][1])

    roc_auc = metrics_g0_m0['balanced_accuracy_score']
    assert isinstance(roc_auc, dict)
    gmr = group_roc_auc_score(Y_true, Y_pred[0], sensitive_features[0])
    assert gmr.overall == pytest.approx(roc_auc['global'])
    assert isinstance(roc_auc['bins'], list)
    assert len(roc_auc['bins']) == 2
    assert gmr.by_group['a'] == pytest.approx(roc_auc['bins'][0])
    assert gmr.by_group['b'] == pytest.approx(roc_auc['bins'][1])

    # Check the second grouping (three unique numeric labels)
    metrics_group_1 = result['precomputedMetrics'][1]
    assert isinstance(metrics_group_1, list)
    assert len(metrics_group_1) == 1
    metrics_g1_m0 = metrics_group_1[0]
    assert isinstance(metrics_g1_m0, dict)
    assert len(metrics_g1_m0) == 10

    accuracy = metrics_g1_m0['accuracy_score']
    assert isinstance(accuracy, dict)
    gmr = group_accuracy_score(Y_true, Y_pred[0], sensitive_features[1])
    assert gmr.overall == pytest.approx(accuracy['global'])
    assert isinstance(accuracy['bins'], list)
    assert len(accuracy['bins']) == 3
    for i in range(3):
        assert gmr.by_group[i+4] == pytest.approx(accuracy['bins'][i])

    roc_auc = metrics_g1_m0['balanced_accuracy_score']
    assert isinstance(roc_auc, dict)
    gmr = group_roc_auc_score(Y_true, Y_pred[0], sensitive_features[1])
    assert gmr.overall == pytest.approx(roc_auc['global'])
    assert isinstance(roc_auc['bins'], list)
    assert len(roc_auc['bins']) == 3
    for i in range(3):
        assert gmr.by_group[i+4] == pytest.approx(roc_auc['bins'][i])


def test_two_named_sensitive_features():
    # Single model, two sensitive feature vectors, no names
    Y_true = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0]
    Y_pred = [[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1]]
    # First sensitive feature is just 'a' and 'b'. Second is 4, 5 and 6
    sensitive_features = [['a', 'b', 'b', 'a', 'b', 'b', 'b', 'a', 'b', 'b', 'b'],
                          [4, 5, 6, 6, 5, 4, 4, 5, 5, 6, 6]]
    sf_int = [int(x == 'b') for x in sensitive_features[0]]
    sensitive_feature_titles = ['alpha', 'num']

    result = create_group_metric_set('binary_classification',
                                     Y_true, Y_pred, sensitive_features,
                                     sensitive_feature_names=sensitive_feature_titles)
    assert result['predictionType'] == 'binaryClassification'
    assert result['schemaType'] == 'groupMetricSet'
    assert result['schemaVersion'] == 0

    assert isinstance(result['trueY'], list)
    assert np.array_equal(result['trueY'], Y_true)

    assert isinstance(result['precomputedFeatureBins'], list)
    assert len(result['precomputedFeatureBins']) == 2
    bin_dict0 = result['precomputedFeatureBins'][0]
    assert isinstance(bin_dict0, dict)
    assert np.array_equal(bin_dict0['binVector'], sf_int)
    assert np.array_equal(bin_dict0['binLabels'], ['a', 'b'])
    assert sensitive_feature_titles[0] == bin_dict0['featureBinName']
    bin_dict1 = result['precomputedFeatureBins'][1]
    assert isinstance(bin_dict1, dict)
    assert np.array_equal(bin_dict1['binVector'], [x-4 for x in sensitive_features[1]])
    assert np.array_equal(bin_dict1['binLabels'], ['4', '5', '6'])
    assert sensitive_feature_titles[1] == bin_dict1['featureBinName']


def test_two_named_models():
    # Two models, single sensitive feature vector, no names
    Y_true = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0]
    Y_pred = [[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
              [1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0]]
    sensitive_features = [['b', 'a', 'a', 'b', 'b', 'b', 'b', 'a', 'b', 'b', 'b']]
    sf_int = [int(x == 'b') for x in sensitive_features[0]]
    model_names = ['firstModel', 'secondModel']

    result = create_group_metric_set('binary_classification',
                                     Y_true, Y_pred, sensitive_features,
                                     model_titles=model_names)
    assert result['predictionType'] == 'binaryClassification'
    assert result['schemaType'] == 'groupMetricSet'
    assert result['schemaVersion'] == 0

    assert isinstance(result['trueY'], list)
    assert np.array_equal(result['trueY'], Y_true)

    assert isinstance(result['precomputedFeatureBins'], list)
    assert len(result['precomputedFeatureBins']) == 1
    bin_dict = result['precomputedFeatureBins'][0]
    assert isinstance(bin_dict, dict)
    assert np.array_equal(bin_dict['binVector'], sf_int)
    assert np.array_equal(bin_dict['binLabels'], ['a', 'b'])

    assert isinstance(result['modelNames'], list)
    assert np.array_equal(result['modelNames'], model_names)


def test_multiple_models_multiple_sensitive_features():
    # Three models, two sensitive feature vectors, no names
    Y_true = [0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0]
    Y_pred = [[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
              [1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1],
              [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0]]
    # First group is just 'a' and 'b'. Second is 4, 5 and 6
    sensitive_features = [['a', 'b', 'b', 'a', 'b', 'b', 'b', 'a', 'b', 'b', 'b'],
                          [4, 5, 6, 6, 5, 4, 4, 5, 5, 6, 6]]
    sf_int = [int(x == 'b') for x in sensitive_features[0]]

    result = create_group_metric_set('binary_classification', Y_true, Y_pred, sensitive_features)
    assert result['predictionType'] == 'binaryClassification'
    assert result['schemaType'] == 'groupMetricSet'
    assert result['schemaVersion'] == 0

    assert isinstance(result['trueY'], list)
    assert np.array_equal(result['trueY'], Y_true)

    assert isinstance(result['precomputedFeatureBins'], list)
    assert len(result['precomputedFeatureBins']) == 2
    bin_dict0 = result['precomputedFeatureBins'][0]
    assert isinstance(bin_dict0, dict)
    assert np.array_equal(bin_dict0['binVector'], sf_int)
    assert np.array_equal(bin_dict0['binLabels'], ['a', 'b'])
    bin_dict1 = result['precomputedFeatureBins'][1]
    assert isinstance(bin_dict1, dict)
    assert np.array_equal(bin_dict1['binVector'], [x-4 for x in sensitive_features[1]])
    assert np.array_equal(bin_dict1['binLabels'], ['4', '5', '6'])

    assert isinstance(result['predictedY'], list)
    assert len(result['predictedY']) == 3
    for i in range(3):
        y_p = result['predictedY'][i]
        assert isinstance(y_p, list)
        assert np.array_equal(y_p, Y_pred[i])

    assert isinstance(result['precomputedMetrics'], list)
    assert len(result['precomputedMetrics']) == 2

    # Check the first grouping (with alphabetical labels)
    metrics_group_0 = result['precomputedMetrics'][0]
    assert isinstance(metrics_group_0, list)
    assert len(metrics_group_0) == 3
    # Loop over the models
    for i in range(3):
        m_g0 = metrics_group_0[i]
        assert isinstance(m_g0, dict)
        assert len(m_g0) == 10

        accuracy = m_g0['accuracy_score']
        assert isinstance(accuracy, dict)
        gmr = group_accuracy_score(Y_true, Y_pred[i], sensitive_features[0])
        assert gmr.overall == pytest.approx(accuracy['global'])
        assert isinstance(accuracy['bins'], list)
        assert len(accuracy['bins']) == 2
        assert gmr.by_group['a'] == pytest.approx(accuracy['bins'][0])
        assert gmr.by_group['b'] == pytest.approx(accuracy['bins'][1])

        roc_auc = m_g0['balanced_accuracy_score']
        assert isinstance(roc_auc, dict)
        gmr = group_roc_auc_score(Y_true, Y_pred[i], sensitive_features[0])
        assert gmr.overall == pytest.approx(roc_auc['global'])
        assert isinstance(roc_auc['bins'], list)
        assert len(roc_auc['bins']) == 2
        assert gmr.by_group['a'] == pytest.approx(roc_auc['bins'][0])
        assert gmr.by_group['b'] == pytest.approx(roc_auc['bins'][1])

    # Check the second grouping (three unique numeric labels)
    metrics_group_1 = result['precomputedMetrics'][1]
    assert isinstance(metrics_group_1, list)
    assert len(metrics_group_1) == 3
    # Loop over the models
    for i in range(3):
        m_g1 = metrics_group_1[i]
        assert isinstance(m_g1, dict)
        assert len(m_g1) == 10
        accuracy = m_g1['accuracy_score']
        assert isinstance(accuracy, dict)
        gmr = group_accuracy_score(Y_true, Y_pred[i], sensitive_features[1])
        assert gmr.overall == pytest.approx(accuracy['global'])
        assert isinstance(accuracy['bins'], list)
        assert len(accuracy['bins']) == 3
        # Use the fact that the groups are integers
        for j in range(3):
            assert gmr.by_group[j+4] == pytest.approx(accuracy['bins'][j])

        roc_auc = m_g1['balanced_accuracy_score']
        assert isinstance(roc_auc, dict)
        gmr = group_roc_auc_score(Y_true, Y_pred[i], sensitive_features[1])
        assert gmr.overall == pytest.approx(roc_auc['global'])
        assert isinstance(roc_auc['bins'], list)
        assert len(roc_auc['bins']) == 3
        for i in range(3):
            assert gmr.by_group[i+4] == pytest.approx(roc_auc['bins'][i])


@pytest.mark.parametrize("transform_y_true", conversions_for_1d)
@pytest.mark.parametrize("transform_y_pred1", conversions_for_1d)
@pytest.mark.parametrize("transform_group_1", conversions_for_1d)
def test_argument_types(transform_y_true,
                        transform_y_pred1,
                        transform_group_1):
    # Three models, two groups, no names
    Y_true = transform_y_true([0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0])
    Y_pred = [[0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
              transform_y_pred1([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1]),
              [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0]]
    g = [[0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
         [4, 5, 6, 6, 5, 4, 4, 5, 5, 6, 6]]
    Groups = [g[0],
              transform_group_1(g[1])]

    result = create_group_metric_set('binary_classification', Y_true, Y_pred, Groups)
    assert result['predictionType'] == 'binaryClassification'
    assert result['schemaType'] == 'groupMetricSet'
    assert result['schemaVersion'] == 0

    assert isinstance(result['trueY'], list)
    assert np.array_equal(result['trueY'], Y_true)

    assert isinstance(result['precomputedFeatureBins'], list)
    assert len(result['precomputedFeatureBins']) == 2
    bin_dict0 = result['precomputedFeatureBins'][0]
    assert isinstance(bin_dict0, dict)
    assert np.array_equal(bin_dict0['binVector'], g[0])
    assert np.array_equal(bin_dict0['binLabels'], ['0', '1'])
    bin_dict1 = result['precomputedFeatureBins'][1]
    assert isinstance(bin_dict1, dict)
    assert np.array_equal(bin_dict1['binVector'], [x-4 for x in g[1]])
    assert np.array_equal(bin_dict1['binLabels'], ['4', '5', '6'])

    assert isinstance(result['predictedY'], list)
    assert len(result['predictedY']) == 3
    for i in range(3):
        y_p = result['predictedY'][i]
        assert isinstance(y_p, list)
        assert np.array_equal(y_p, Y_pred[i])

    assert isinstance(result['precomputedMetrics'], list)
    assert len(result['precomputedMetrics']) == 2

    # Check the first grouping (with alphabetical labels)
    metrics_group_0 = result['precomputedMetrics'][0]
    assert isinstance(metrics_group_0, list)
    assert len(metrics_group_0) == 3
    # Loop over the models
    for i in range(3):
        m_g0 = metrics_group_0[i]
        assert isinstance(m_g0, dict)
        assert len(m_g0) == 10
        accuracy = m_g0['accuracy_score']
        assert isinstance(accuracy, dict)
        gmr = group_accuracy_score(Y_true, Y_pred[i], Groups[0])
        assert gmr.overall == pytest.approx(accuracy['global'])
        assert isinstance(accuracy['bins'], list)
        assert len(accuracy['bins']) == 2
        assert gmr.by_group[0] == pytest.approx(accuracy['bins'][0])
        assert gmr.by_group[1] == pytest.approx(accuracy['bins'][1])

    # Check the second grouping (three unique numeric labels)
    metrics_group_1 = result['precomputedMetrics'][1]
    assert isinstance(metrics_group_1, list)
    assert len(metrics_group_1) == 3
    # Loop over the models
    for i in range(3):
        m_g1 = metrics_group_1[i]
        assert isinstance(m_g1, dict)
        assert len(m_g1) == 10
        accuracy = m_g1['accuracy_score']
        assert isinstance(accuracy, dict)
        gmr = group_accuracy_score(Y_true, Y_pred[i], Groups[1])
        assert gmr.overall == pytest.approx(accuracy['global'])
        assert isinstance(accuracy['bins'], list)
        assert len(accuracy['bins']) == 3
        # Use the fact that the groups are integers
        for j in range(3):
            assert gmr.by_group[j+4] == pytest.approx(accuracy['bins'][j])
