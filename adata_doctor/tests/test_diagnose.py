import numpy as np
import scipy.sparse as sp

from adata_doctor.diagnose import diagnose_matrix


def test_raw_counts_diagnosis():
    rng = np.random.default_rng(0)
    x = rng.poisson(1.5, size=(200, 500)).astype(np.int32)
    # add some highly expressed genes so max > 12
    x[:, 0] += rng.poisson(30, size=200)
    diag = diagnose_matrix(sp.csr_matrix(x), name="X", sample_cells=100, seed=0)
    assert diag.verdict in {"raw_counts", "probably_raw_counts"}


def test_normalized_not_log1p_diagnosis():
    rng = np.random.default_rng(1)
    x = rng.poisson(2, size=(120, 300)).astype(float)
    x[:, 0] += 50
    row_sum = x.sum(axis=1, keepdims=True)
    x = x / row_sum * 1e4
    diag = diagnose_matrix(sp.csr_matrix(x), name="X", sample_cells=80, seed=1)
    assert diag.verdict == "normalized_to_target_sum_not_log1p"


def test_log1p_normalized_diagnosis():
    rng = np.random.default_rng(2)
    x = rng.poisson(2, size=(120, 300)).astype(float)
    x[:, 0] += 50
    x = x / x.sum(axis=1, keepdims=True) * 1e4
    x = np.log1p(x)
    diag = diagnose_matrix(sp.csr_matrix(x), name="X", sample_cells=80, seed=2)
    assert diag.verdict in {"log1p_normalized_to_target_sum", "probably_log1p_normalized"}


def test_scaled_matrix_diagnosis():
    rng = np.random.default_rng(3)
    x = rng.normal(0, 1, size=(100, 200))
    diag = diagnose_matrix(x, name="X", sample_cells=80, seed=3)
    assert diag.verdict in {"scaled_or_other_transformed_matrix", "other_transformed_matrix"}
