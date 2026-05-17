# adata-doctor

`adata-doctor` is a lightweight diagnostic reporter for AnnData expression matrices.

It helps answer a practical question before downstream single-cell analysis:

> What state is this matrix in? Raw counts, normalized values, log1p-normalized data, scaled data, or something ambiguous?

## Installation for local development

```bash
cd adata_doctor
pip install -e .
```

## Python usage

```python
import anndata as ad
import adata_doctor as doctor

adata = ad.read_h5ad("example.h5ad")
report = doctor.report(adata)

print(report.to_text())
report.to_markdown("adata_doctor_report.md")
report.to_json("adata_doctor_report.json")
```

## Optional AnnData method style

By default, `adata-doctor` does not monkey-patch `AnnData`. If you want `adata.report()`:

```python
import adata_doctor as doctor

doctor.patch_anndata()
report = adata.report()
print(report.to_text())
```

## CLI usage

```bash
adata-doctor example.h5ad
adata-doctor example.h5ad --out report.md
adata-doctor example.h5ad --json report.json
```

## What it checks in v0.1

- AnnData shape
- `.X` type, dtype, sparse/dense status
- `.obs`, `.var`, `.layers`, `.raw`, `.obsm`, `.uns` overview
- Matrix state diagnosis for:
  - `.X`
  - `.raw.X` if present
  - each `adata.layers[...]`
- Whether values look integer-like
- Whether row sums look normalized to 10,000
- Whether `expm1(X)` row sums look normalized to 10,000
- Whether negative values suggest scaled/transformed matrix
- Simple downstream recommendations

## Scope

This is a first version. It uses heuristics rather than a guaranteed proof. Public single-cell files can be inconsistent, so the report should be treated as a structured pre-check, not as final biological validation.
