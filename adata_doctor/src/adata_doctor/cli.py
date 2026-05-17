from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .api import inspect


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="adata-doctor",
        description="Diagnose AnnData expression matrix state and generate a report.",
    )
    parser.add_argument("path", help="Path to a .h5ad file")
    parser.add_argument(
        "--sample-cells",
        type=int,
        default=256,
        help="Number of cells to sample for diagnostics. Default: 256",
    )
    parser.add_argument(
        "--sample-genes",
        type=int,
        default=None,
        help="Optional number of genes for value-level statistics. Row sums still use all genes.",
    )
    parser.add_argument(
        "--target-sum",
        type=float,
        default=1e4,
        help="Expected normalization target sum. Default: 10000",
    )
    parser.add_argument("--seed", type=int, default=0, help="Random seed. Default: 0")
    parser.add_argument("--out", type=Path, default=None, help="Write Markdown report to this path")
    parser.add_argument("--json", type=Path, default=None, help="Write JSON report to this path")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    rep = inspect(
        args.path,
        sample_cells=args.sample_cells,
        sample_genes=args.sample_genes,
        target_sum=args.target_sum,
        seed=args.seed,
        out=args.out,
        json_out=args.json,
    )
    print(rep.to_text())
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
