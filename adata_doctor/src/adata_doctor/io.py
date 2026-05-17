from __future__ import annotations

from pathlib import Path
from typing import Union


def read_anndata(path: Union[str, Path]):
    """Read an AnnData file lazily imported to keep top-level import light."""
    try:
        import anndata as ad
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Reading .h5ad files requires anndata. Install with: pip install anndata"
        ) from exc

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() != ".h5ad":
        raise ValueError(
            f"adata-doctor v0.1 reads .h5ad files from CLI, got: {path.suffix}. "
            "You can still pass an already loaded AnnData object to adata_doctor.report()."
        )
    return ad.read_h5ad(path)
