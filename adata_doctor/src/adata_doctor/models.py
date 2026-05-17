from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class MatrixDiagnosis:
    name: str
    verdict: str
    confidence: float
    advice: str
    evidence: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AdataDoctorReport:
    summary: Dict[str, Any]
    matrices: Dict[str, MatrixDiagnosis]
    compatibility: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "matrices": {k: v.to_dict() for k, v in self.matrices.items()},
            "compatibility": self.compatibility,
            "warnings": self.warnings,
        }

    def to_json(self, path: Optional[Union[str, Path]] = None, *, indent: int = 2) -> str:
        text = json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)
        if path is not None:
            Path(path).write_text(text, encoding="utf-8")
        return text

    def to_markdown(self, path: Optional[Union[str, Path]] = None) -> str:
        lines: List[str] = []
        lines.append("# adata-doctor report")
        lines.append("")
        lines.append("## 1. AnnData overview")
        lines.append("")
        lines.append("| Item | Value |")
        lines.append("|---|---:|")
        for key, value in self.summary.items():
            lines.append(f"| `{key}` | {self._fmt(value)} |")

        if self.warnings:
            lines.append("")
            lines.append("## 2. Global warnings")
            lines.append("")
            for item in self.warnings:
                lines.append(f"- ⚠️ {item}")

        lines.append("")
        lines.append("## 3. Matrix diagnoses")
        for name, diag in self.matrices.items():
            lines.append("")
            lines.append(f"### {name}")
            lines.append("")
            lines.append(f"- **Verdict:** `{diag.verdict}`")
            lines.append(f"- **Confidence:** `{diag.confidence:.2f}`")
            lines.append(f"- **Advice:** {diag.advice}")

            if diag.evidence:
                lines.append("- **Evidence:**")
                for e in diag.evidence:
                    lines.append(f"  - {e}")
            if diag.warnings:
                lines.append("- **Warnings:**")
                for w in diag.warnings:
                    lines.append(f"  - ⚠️ {w}")

            lines.append("")
            lines.append("| Statistic | Value |")
            lines.append("|---|---:|")
            for key, value in diag.stats.items():
                lines.append(f"| `{key}` | {self._fmt(value)} |")

        lines.append("")
        lines.append("## 4. Downstream compatibility")
        lines.append("")
        lines.append("| Task | Status | Recommendation |")
        lines.append("|---|---|---|")
        for task, info in self.compatibility.items():
            lines.append(
                f"| {task} | `{info.get('status', 'unknown')}` | {info.get('recommendation', '')} |"
            )

        text = "\n".join(lines) + "\n"
        if path is not None:
            Path(path).write_text(text, encoding="utf-8")
        return text

    def to_text(self) -> str:
        lines: List[str] = []
        lines.append("=" * 80)
        lines.append("adata-doctor report")
        lines.append("=" * 80)
        shape = self.summary.get("shape", "unknown")
        lines.append(f"Shape: {shape}")
        lines.append(f"X type: {self.summary.get('X_type', 'unknown')}")
        lines.append(f"Layers: {self.summary.get('layers', [])}")
        lines.append(f"Raw exists: {self.summary.get('has_raw', False)}")
        if self.warnings:
            lines.append("\nGlobal warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")

        lines.append("\nMatrix diagnoses:")
        for name, diag in self.matrices.items():
            lines.append(f"\n[{name}]")
            lines.append(f"  verdict    : {diag.verdict}")
            lines.append(f"  confidence : {diag.confidence:.2f}")
            lines.append(f"  advice     : {diag.advice}")
            if diag.evidence:
                lines.append("  evidence:")
                for e in diag.evidence:
                    lines.append(f"    - {e}")
            if diag.warnings:
                lines.append("  warnings:")
                for w in diag.warnings:
                    lines.append(f"    - {w}")
            important_keys = [
                "sampled_cells",
                "sampled_genes_for_value_stats",
                "finite_ratio",
                "min",
                "max",
                "mean",
                "nonzero_ratio",
                "int_like_ratio_nonzero",
                "row_sum_median",
                "row_sum_close_to_target_ratio",
                "expm1_sum_median",
                "expm1_sum_close_to_target_ratio",
            ]
            for key in important_keys:
                if key in diag.stats:
                    lines.append(f"  {key:34s}: {self._fmt(diag.stats[key])}")

        lines.append("\nCompatibility:")
        for task, info in self.compatibility.items():
            lines.append(
                f"  - {task}: {info.get('status', 'unknown')} | {info.get('recommendation', '')}"
            )
        lines.append("=" * 80)
        return "\n".join(lines)

    @staticmethod
    def _fmt(value: Any) -> str:
        if isinstance(value, float):
            if value != value:  # NaN
                return "NaN"
            return f"{value:.6g}"
        if isinstance(value, (list, tuple)):
            if len(value) > 20:
                return f"{list(value[:20])} ... (+{len(value)-20} more)"
            return str(list(value))
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return str(value)
