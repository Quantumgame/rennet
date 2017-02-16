"""
@motjuste
Created: 08-02-2017

Test the Numpy Utilities
"""
import pytest
import numpy as np
from numpy.testing import assert_almost_equal
from sklearn.metrics import confusion_matrix as ext_confusionmatrix
from keras.utils.np_utils import to_categorical as ext_tocategorical

from rennet.utils import np_utils as nu

# pylint: disable=redefined-outer-name


@pytest.fixture(scope='module')
def base_labels_cls3():
    """ sample array of class labels
    that can be recombined to act as predicitons of each other
    """

    return np.array([
        [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1],  # Exact
        [1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2],  # No 2_0
        [0, 0, 2, 2, 1, 1, 2, 2, 2, 2, 0, 0, 1, 1],  # No 1_0
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],  # No 2
        [1, 1, 1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1],  # No 0
        [1, 1, 1, 2, 2, 2, 2, 2, 1, 1, 1, 0, 0, 0],  # None correct
        [4, 4, 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 0, 0],  # Extra class
    ])


## FIXTURES AND TESTS FOR TO_CATEGORICAL ###########################################


@pytest.fixture(
    scope='module',
    params=list(range(len(base_labels_cls3()))),
    ids=lambda i: "TPU-(1, B, 1, 3)-{}".format(i)  #pylint: disable=unnecessary-lambda
)
def pred1_batB_seqL1_cls3_trues_preds_user_cat(request, base_labels_cls3):
    """ y and Y (categorical) in user expected format
    trues and preds look the same from the user's perspective when
    there is only one predictor
    """
    i = request.param
    y = base_labels_cls3[i]
    nclasses = max(y) + 1
    Y = ext_tocategorical(y, nb_classes=nclasses)

    return {
        'y': y,
        'Y': Y,
        'nclasses': nclasses,
    }


def test_tocategorical_trues_preds_user(
        pred1_batB_seqL1_cls3_trues_preds_user_cat):
    y, Y, nc = [
        pred1_batB_seqL1_cls3_trues_preds_user_cat[k]
        for k in ['y', 'Y', 'nclasses']
    ]

    assert_almost_equal(nu.to_categorical(y, nclasses=nc), Y)

    if y.max() == nc:
        assert_almost_equal(nu.to_categorical(y), Y)

    assert True


@pytest.fixture(
    scope='module',
    params=list(range(len(base_labels_cls3()))),
    ids=lambda i: "TG-(B, 1, 3)-{}".format(i)  #pylint: disable=unnecessary-lambda
)
def batB_seqL1_cls3_trues_generic_cat(request, base_labels_cls3):
    """ y and Y (categorical) in format expected by the generic function
    The generic representation expects:
    (Predictions, Batchsize, SequenceLength)

    For Trues, there is no Predictions dimension
    """
    i = request.param
    y = base_labels_cls3[i]
    nclasses = max(y) + 1
    Y = ext_tocategorical(y, nb_classes=nclasses)

    return {
        'nclasses': nclasses,

        # Batchsize=B, SequenceLength=1, ClassLabel=1(implicit)
        'y': y[:, np.newaxis],

        # Batchsize=B, SequenceLength=1, ClassLabel=nclasses(categorical)
        'Y': Y[:, np.newaxis, :],
    }


def test_tocategorical_trues_generic(batB_seqL1_cls3_trues_generic_cat):
    y, Y, nc = [
        batB_seqL1_cls3_trues_generic_cat[k] for k in ['y', 'Y', 'nclasses']
    ]

    assert_almost_equal(nu.to_categorical(y, nclasses=nc), Y)

    if y.max() == nc:
        assert_almost_equal(nu.to_categorical(y), Y)

    assert True


@pytest.fixture(
    scope='module',
    params=list(range(len(base_labels_cls3()))),
    ids=lambda i: "PG-(B, 1, 3)-{}".format(i)  #pylint: disable=unnecessary-lambda
)
def pred1_batB_seqL1_cls3_generic_cat(request, base_labels_cls3):
    """ y and Y (categorical) in format expected by the generic function
    The generic representation expects:
    (Predictions, Batchsize, SequenceLength)

    Here, there is only one prediction
    """
    i = request.param
    y = base_labels_cls3[i]
    nclasses = max(y) + 1
    Y = ext_tocategorical(y, nb_classes=nclasses)

    return {
        'nclasses': nclasses,

        # Predictor=1, Batchsize=B, SequenceLength=1, ClassLabel=1(implicit)
        'y': y[np.newaxis, :, np.newaxis],

        # Predictor=1, Batchsize=B, SequenceLength=1, ClassLabel=nclasses(categorical)
        'Y': Y[np.newaxis, :, np.newaxis, :],
    }


def test_tocategorical_pred1_generic(pred1_batB_seqL1_cls3_generic_cat):
    y, Y, nc = [
        pred1_batB_seqL1_cls3_generic_cat[k] for k in ['y', 'Y', 'nclasses']
    ]

    assert_almost_equal(nu.to_categorical(y, nclasses=nc), Y)

    if y.max() == nc:
        assert_almost_equal(nu.to_categorical(y), Y)

    assert True


@pytest.fixture(
    scope='module',
    params=[list(range(2))],  # P: number of predictions
    ids=lambda i: "PU-({}, B, 1, 3)".format(i)  #pylint: disable=unnecessary-lambda
)
def predP_batB_seqL1_cls3_user_cat(request, base_labels_cls3):
    """ y and Y (categorical) in user expected format
    there are P predictions
    """
    i = request.param
    y = [base_labels_cls3[ii] for ii in i]
    nclasses = max([max(yy) for yy in y]) + 1
    Y = [ext_tocategorical(yy, nb_classes=nclasses) for yy in y]

    return {
        'y': np.array(y),
        'Y': np.array(Y),
        'nclasses': nclasses,
    }


def test_tocategorical_predP_user(predP_batB_seqL1_cls3_user_cat):
    y, Y, nc = [
        predP_batB_seqL1_cls3_user_cat[k] for k in ['y', 'Y', 'nclasses']
    ]

    assert_almost_equal(nu.to_categorical(y, nclasses=nc), Y)

    if y.max() == nc:
        assert_almost_equal(nu.to_categorical(y), Y)

    assert True


@pytest.fixture(
    scope='module',
    params=[list(range(2))],  # P: number of predictions
    ids=lambda i: "PU-({}, B, 1, 3)".format(i)  #pylint: disable=unnecessary-lambda
)
def predP_batB_seqL1_cls3_generic_cat(request, base_labels_cls3):
    """ y and Y (categorical) in user expected format
    """
    i = request.param
    y = [base_labels_cls3[ii] for ii in i]
    nclasses = max([max(yy) for yy in y]) + 1
    Y = [ext_tocategorical(yy, nb_classes=nclasses) for yy in y]

    return {
        'nclasses': nclasses,

        # Predictor=P, Batchsize=B, SequenceLength=1, ClassLabel=1(implicit)
        'y': np.array(y)[..., np.newaxis],

        # Predictor=P, Batchsize=B, SequenceLength=1, ClassLabel=nclasses(categorical)
        'Y': np.array(Y)[..., np.newaxis, :],
    }


def test_tocategorical_predsP_generic(predP_batB_seqL1_cls3_generic_cat):
    y, Y, nc = [
        predP_batB_seqL1_cls3_generic_cat[k] for k in ['y', 'Y', 'nclasses']
    ]

    print(y.shape, Y.shape, nu.to_categorical(y, nc).shape)
    assert_almost_equal(nu.to_categorical(y, nclasses=nc), Y)

    if y.max() == nc:
        assert_almost_equal(nu.to_categorical(y), Y)

    assert True


@pytest.fixture(
    scope='module',
    params=[list(range(2))],  # B: batchsize
    ids=lambda i: "TU-({}, Q, 3)".format(i)  #pylint: disable=unnecessary-lambda
)
def pred1_batB_seqlQ_cls3_trues_preds_user_cat(request, base_labels_cls3):
    """ y and Y (categorical) in format the user expects
    this is exactly like predP_batB_seqL1_cls3_user_cat
    but these are trues
    non-zero sequence length trues and preds look similar for single predictor
    """
    i = request.param
    y = [base_labels_cls3[ii] for ii in i]
    nclasses = max([max(yy) for yy in y]) + 1
    Y = [ext_tocategorical(yy, nb_classes=nclasses) for yy in y]

    return {
        'y': np.array(y),
        'Y': np.array(Y),
        'nclasses': nclasses,
    }


def test_tocategorical_batB_seqLQ_user(
        pred1_batB_seqlQ_cls3_trues_preds_user_cat):
    y, Y, nc = [
        pred1_batB_seqlQ_cls3_trues_preds_user_cat[k]
        for k in ['y', 'Y', 'nclasses']
    ]

    assert_almost_equal(nu.to_categorical(y, nclasses=nc), Y)

    if y.max() == nc:
        assert_almost_equal(nu.to_categorical(y), Y)

    assert True


@pytest.fixture(
    scope='module',
    params=[list(range(2))],  # B: batchsize
    ids=lambda i: "TU-({}, Q, 3)".format(i)  #pylint: disable=unnecessary-lambda
)
def batB_seqlQ_cls3_trues_generic_cat(request, base_labels_cls3):
    """ y and Y (categorical) in format the user expects
    this is exactly like predP_batB_seqL1_cls3_user_cat
    but these are trues
    non-zero sequence length trues and preds look similar for single predictor
    """
    i = request.param
    y = [base_labels_cls3[ii] for ii in i]
    nclasses = max([max(yy) for yy in y]) + 1
    Y = [ext_tocategorical(yy, nb_classes=nclasses) for yy in y]

    return {
        'nclasses': nclasses,

        # Batchsize=B, SequenceLength=Q, ClassLabel=1(implicit)
        'y': np.array(y),

        # Batchsize=B, SequenceLength=Q, ClassLabel=nclasses(categorical)
        'Y': np.array(Y),
    }


def test_tocategorical_batB_seqlQ_trues_generic(
        batB_seqlQ_cls3_trues_generic_cat):
    y, Y, nc = [
        batB_seqlQ_cls3_trues_generic_cat[k] for k in ['y', 'Y', 'nclasses']
    ]

    print(y.shape, Y.shape, nu.to_categorical(y, nc).shape)
    assert_almost_equal(nu.to_categorical(y, nclasses=nc), Y)

    if y.max() == nc:
        assert_almost_equal(nu.to_categorical(y), Y)

    assert True


@pytest.fixture(
    scope='module',
    params=[list(range(2))],  # B: batchsize
    ids=lambda i: "TU-({}, Q, 3)".format(i)  #pylint: disable=unnecessary-lambda
)
def pred1_batB_seqlQ_cls3_preds_generic_cat(request, base_labels_cls3):
    """ y and Y (categorical) in format the user expects
    """
    i = request.param
    y = [base_labels_cls3[ii] for ii in i]
    nclasses = max([max(yy) for yy in y]) + 1
    Y = [ext_tocategorical(yy, nb_classes=nclasses) for yy in y]

    return {
        'nclasses': nclasses,

        # Predictor=1, Batchsize=B, SequenceLength=Q, ClassLabel=1(implicit)
        'y': np.array(y)[np.newaxis, ...],

        # Predictor=1, Batchsize=B, SequenceLength=Q, ClassLabel=nclasses(categorical)
        'Y': np.array(Y)[np.newaxis, ...],
    }


def test_tocategorical_pred1_batB_seqlQ_preds_generic(
        pred1_batB_seqlQ_cls3_preds_generic_cat):
    y, Y, nc = [
        pred1_batB_seqlQ_cls3_preds_generic_cat[k]
        for k in ['y', 'Y', 'nclasses']
    ]

    print(y.shape, Y.shape, nu.to_categorical(y, nc).shape)
    assert_almost_equal(nu.to_categorical(y, nclasses=nc), Y)

    if y.max() == nc:
        assert_almost_equal(nu.to_categorical(y), Y)

    assert True


@pytest.fixture(
    scope='module',
    params=[[list(range(2)), list(range(5))]],  # P: Predictions, B: batchsize
    ids=lambda i: "PU-({}, {}, Q, 3)".format(*i)  #pylint: disable=unnecessary-lambda
)
def predP_batB_seqlQ_cls3_preds_user_cat(request, base_labels_cls3):
    """ y and Y (categorical) in format the user expects
    """
    p, b = request.param
    y = []
    nclasses = 0
    for _ in p:
        yy = []
        for i in b:
            yy.append(base_labels_cls3[i])
            nclasses = max(nclasses, max(base_labels_cls3[i]) + 1)
        y.append(yy)

    Y = []
    for yp in y:
        YY = []
        for yb in yp:
            YY.append(ext_tocategorical(yb, nb_classes=nclasses))
        Y.append(YY)

    return {
        'y': np.array(y),
        'Y': np.array(Y),
        'nclasses': nclasses,
    }


def test_tocategorical_predP_batB_seqLQ_user(
        predP_batB_seqlQ_cls3_preds_user_cat):
    y, Y, nc = [
        predP_batB_seqlQ_cls3_preds_user_cat[k]
        for k in ['y', 'Y', 'nclasses']
    ]

    print(y.shape, Y.shape, nu.to_categorical(y, nc).shape)
    assert_almost_equal(nu.to_categorical(y, nclasses=nc), Y)

    if y.max() == nc:
        assert_almost_equal(nu.to_categorical(y), Y)

    assert True


@pytest.fixture(
    scope='module',
    params=[[list(range(2)), list(range(5))]],  # P: Predictions, B: batchsize
    ids=lambda i: "PG-({}, {}, Q, 3)".format(*i)  #pylint: disable=unnecessary-lambda
)
def predP_batB_seqlQ_cls3_generic_cat(request, base_labels_cls3):
    """ y and Y (categorical) in format the user expects
    """
    p, b = request.param
    y = []
    nclasses = 0
    for _ in p:
        yy = []
        for i in b:
            yy.append(base_labels_cls3[i])
            nclasses = max(nclasses, max(base_labels_cls3[i]) + 1)
        y.append(yy)

    Y = []
    for yp in y:
        YY = []
        for yb in yp:
            YY.append(ext_tocategorical(yb, nb_classes=nclasses))
        Y.append(YY)

    return {
        'nclasses': nclasses,

        # Predictor=P, Batchsize=B, SequenceLength=Q, ClassLabel=1(implicit)
        'y': np.array(y)[...],

        # Predictor=P, Batchsize=B, SequenceLength=Q, ClassLabel=nclasses(categorical)
        'Y': np.array(Y)[...],
    }


def test_tocategorical_predP_batB_seqLQ_generic(
        predP_batB_seqlQ_cls3_preds_user_cat):
    y, Y, nc = [
        predP_batB_seqlQ_cls3_preds_user_cat[k]
        for k in ['y', 'Y', 'nclasses']
    ]

    print(y.shape, Y.shape, nu.to_categorical(y, nc).shape)
    assert_almost_equal(nu.to_categorical(y, nclasses=nc), Y)

    if y.max() == nc:
        assert_almost_equal(nu.to_categorical(y), Y)

    assert True


## FIXTURES AND TESTS FOR CONFUSION MATRIX CALCULATIONS #######################


@pytest.fixture(
    scope='module',
    params=list(range(5)),
    ids=lambda i: "T={}".format(i),  #pylint: disable=unnecessary-lambda
)
def batB_seql1_cls3_trues_confmat(request, base_labels_cls3):
    i = request.param

    y = base_labels_cls3[i]
    nclasses = 3
    Y = nu.to_categorical(y, nclasses)

    return {'yt': y, 'Yt': Y, 'nclasses': nclasses}


@pytest.fixture(
    scope='module',
    params=list(range(5)),
    ids=lambda i: "P={}".format(i),  #pylint: disable=unnecessary-lambda
)
def pred1_batB_seql1_cls3_preds_confmat(request, base_labels_cls3,
                                        batB_seql1_cls3_trues_confmat):
    i = request.param

    yp = base_labels_cls3[i]

    nclasses = batB_seql1_cls3_trues_confmat['nclasses']
    Yp = nu.to_categorical(yp, nclasses)

    yt = batB_seql1_cls3_trues_confmat['yt']
    Yt = batB_seql1_cls3_trues_confmat['Yt']
    confmat = ext_confusionmatrix(yt, yp, labels=np.arange(nclasses))

    confrecall = confmat / (confmat.sum(axis=1))[:, np.newaxis]
    confprecision = (confmat.T / (confmat.sum(axis=0))[:, np.newaxis]).T

    return {
        'yt': yt,
        'Yt': Yt,
        'yp': yp,
        'Yp': Yp,
        'confmat': confmat,
        'confrecall': confrecall,
        'confprecision': confprecision,
    }


@pytest.mark.confmat
def test_pred1_batB_seql1_confmat(pred1_batB_seql1_cls3_preds_confmat):
    Yt, Yp, confmat = [
        pred1_batB_seql1_cls3_preds_confmat[k]
        for k in ['Yt', 'Yp', 'confmat']
    ]
    print(Yt.shape, Yp.shape)
    assert_almost_equal(nu.confusion_matrix_forcategorical(Yt, Yp), confmat)

    yt, yp = [pred1_batB_seql1_cls3_preds_confmat[k] for k in ['yt', 'yp']]
    nclasses = Yt.shape[-1]
    print(yt.shape, yp.shape)
    assert_almost_equal(nu.confusion_matrix(yt, yp, nclasses), confmat)

    assert True
