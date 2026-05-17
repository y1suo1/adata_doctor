from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

from .doctor import inspect_anndata
from .io import read_anndata
from .models import AdataDoctorReport


def report(
    adata: Any,
    *,
    sample_cells: int = 256,
    sample_genes: Optional[int] = None,
    target_sum: float = 1e4,
    seed: int = 0,
    out: Optional[Union[str, Path]] = None,
    json_out: Optional[Union[str, Path]] = None,
) -> AdataDoctorReport:
    """Create a diagnostic report for an already loaded AnnData object.

    Parameters
    ----------
    adata:
        An AnnData-like object.
    sample_cells:
        Number of cells sampled for matrix-level diagnostics.
    sample_genes:
        Optional number of genes sampled for value-level diagnostics. Row-sum
        diagnostics still use all genes for the sampled cells.
    target_sum:
        Expected library size after normalization, usually 1e4 in Scanpy workflows.
    seed:
        Random seed for reproducible sampling.
    out:
        Optional path to write a Markdown report.
    json_out:
        Optional path to write a JSON report.

    Returns
    -------
    AdataDoctorReport
        Structured report object.
    """
    rep = inspect_anndata(
        adata,
        sample_cells=sample_cells,
        sample_genes=sample_genes,
        target_sum=target_sum,
        seed=seed,
    )
    if out is not None:
        rep.to_markdown(out)
    if json_out is not None:
        rep.to_json(json_out)
    return rep


def inspect(
    obj: Any,
    *,
    sample_cells: int = 256,
    sample_genes: Optional[int] = None,
    target_sum: float = 1e4,
    seed: int = 0,
    out: Optional[Union[str, Path]] = None,
    json_out: Optional[Union[str, Path]] = None,
) -> AdataDoctorReport:
    """Inspect either an AnnData object or a path to a .h5ad file."""
    if isinstance(obj, (str, Path)):
        adata = read_anndata(obj)
    else:
        adata = obj
    return report(
        adata,
        sample_cells=sample_cells,
        sample_genes=sample_genes,
        target_sum=target_sum,
        seed=seed,
        out=out,
        json_out=json_out,
    )


def patch_anndata() -> None:
    """Install an optional ``adata.report()`` method on AnnData.

    This is intentionally opt-in because modifying third-party classes at import
    time can surprise users.
    """
    try:
        import anndata as ad
    except ImportError as exc:  # pragma: no cover
        raise ImportError("patch_anndata() requires anndata to be installed.") from exc

    def _report_method(self, **kwargs):  # type: ignore[no-untyped-def]
        return report(self, **kwargs)

    setattr(ad.AnnData, "report", _report_method)
