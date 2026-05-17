"""adata-doctor: lightweight diagnostics for AnnData expression matrices."""

from .api import inspect, patch_anndata, report
from .models import AdataDoctorReport, MatrixDiagnosis

__all__ = [
    "report",
    "inspect",
    "patch_anndata",
    "AdataDoctorReport",
    "MatrixDiagnosis",
]

__version__ = "0.1.1"
