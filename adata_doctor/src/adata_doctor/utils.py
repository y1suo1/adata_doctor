from __future__ import annotations

from typing import Any

import numpy as np
import scipy.sparse as sp


def is_sparse_matrix(x: Any) -> bool:
    return sp.issparse(x)


def matrix_type_name(x: Any) -> str:
    if sp.issparse(x):
        return f"scipy.sparse.{x.getformat()}"
    return type(x).__name__


def safe_dtype_name(x: Any) -> str:
    dtype = getattr(x, "dtype", None)
    return str(dtype) if dtype is not None else "unknown"


def choose_indices(n: int, sample_n: int, seed: int) -> np.ndarray:
    if n <= 0:
        return np.array([], dtype=int)
    k = min(int(sample_n), int(n))
    rng = np.random.default_rng(seed)
    return np.sort(rng.choice(n, size=k, replace=False))


def as_dense_small(x: Any) -> np.ndarray:
    if sp.issparse(x):
        return x.toarray()
    return np.asarray(x)


def safe_to_float_array(x: Any) -> np.ndarray:
    arr = as_dense_small(x)
    return arr.astype(np.float64, copy=False)
