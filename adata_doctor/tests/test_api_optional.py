import importlib.util

import pytest


def test_anndata_method_patch_if_available():
    if importlib.util.find_spec("anndata") is None:
        pytest.skip("anndata not installed")
    import anndata as ad
    import numpy as np
    import scipy.sparse as sp
    import adata_doctor as doctor

    doctor.patch_anndata()
    x = sp.csr_matrix(np.random.default_rng(0).poisson(1, size=(50, 100)))
    adata = ad.AnnData(x)
    rep = adata.report(sample_cells=20)
    assert "X" in rep.matrices
