from __future__ import annotations

from typing import Any, Dict, Optional

import scipy.sparse as sp

from .compatibility import build_compatibility
from .diagnose import diagnose_matrix
from .models import AdataDoctorReport, MatrixDiagnosis
from .utils import matrix_type_name, safe_dtype_name


def inspect_anndata(
    adata: Any,
    *,
    sample_cells: int = 256,
    sample_genes: Optional[int] = None,
    target_sum: float = 1e4,
    seed: int = 0,
) -> AdataDoctorReport:
    """Inspect an AnnData-like object and diagnose its expression matrices."""
    _validate_anndata_like(adata)

    summary = _summarize_anndata(adata)
    warnings = _global_warnings(adata)

    matrices: Dict[str, MatrixDiagnosis] = {}

    matrices["X"] = diagnose_matrix(
        adata.X,
        name="X",
        sample_cells=sample_cells,
        sample_genes=sample_genes,
        target_sum=target_sum,
        seed=seed,
    )

    raw = getattr(adata, "raw", None)
    if raw is not None:
        try:
            matrices["raw.X"] = diagnose_matrix(
                raw.X,
                name="raw.X",
                sample_cells=sample_cells,
                sample_genes=sample_genes,
                target_sum=target_sum,
                seed=seed,
            )
        except Exception as exc:  # keep report alive
            warnings.append(f"诊断 raw.X 时失败：{exc}")

    layers = getattr(adata, "layers", {})
    for layer_name in list(layers.keys()):
        try:
            matrices[f"layers/{layer_name}"] = diagnose_matrix(
                layers[layer_name],
                name=f"layers/{layer_name}",
                sample_cells=sample_cells,
                sample_genes=sample_genes,
                target_sum=target_sum,
                seed=seed,
            )
        except Exception as exc:
            warnings.append(f"诊断 layer '{layer_name}' 时失败：{exc}")

    compatibility = build_compatibility(matrices, summary)

    return AdataDoctorReport(
        summary=summary,
        matrices=matrices,
        compatibility=compatibility,
        warnings=warnings,
    )


def _validate_anndata_like(adata: Any) -> None:
    required = ["X", "obs", "var", "layers", "uns"]
    missing = [x for x in required if not hasattr(adata, x)]
    if missing:
        raise TypeError(
            "Expected an AnnData-like object. Missing attributes: " + ", ".join(missing)
        )


def _summarize_anndata(adata: Any) -> Dict[str, Any]:
    x = adata.X
    obs_keys = list(getattr(adata, "obs", {}).keys())
    var_keys = list(getattr(adata, "var", {}).keys())
    layers = list(getattr(adata, "layers", {}).keys())
    uns_keys = list(getattr(adata, "uns", {}).keys())
    obsm_keys = list(getattr(adata, "obsm", {}).keys()) if hasattr(adata, "obsm") else []

    return {
        "shape": [int(adata.n_obs), int(adata.n_vars)],
        "n_obs": int(adata.n_obs),
        "n_vars": int(adata.n_vars),
        "X_type": matrix_type_name(x),
        "X_dtype": safe_dtype_name(x),
        "X_is_sparse": bool(sp.issparse(x)),
        "obs_columns": obs_keys,
        "var_columns": var_keys,
        "layers": layers,
        "has_raw": getattr(adata, "raw", None) is not None,
        "obsm_keys": obsm_keys,
        "uns_keys": uns_keys,
        "uns_log1p": getattr(adata, "uns", {}).get("log1p", None),
    }


def _global_warnings(adata: Any) -> list[str]:
    warnings: list[str] = []
    if adata.n_obs < 50:
        warnings.append("细胞数很少，抽样统计可能不稳定。")
    if adata.n_vars < 200:
        warnings.append("基因数较少，可能不是完整表达矩阵或已经经过强筛选。")
    if getattr(adata, "raw", None) is None:
        warnings.append("未发现 adata.raw；如果 X 已被处理，可能缺少可追溯的原始表达矩阵。")
    if len(list(getattr(adata, "layers", {}).keys())) == 0:
        warnings.append("未发现 layers；如果 X 状态不明，可能难以寻找 raw counts 备份。")
    return warnings
