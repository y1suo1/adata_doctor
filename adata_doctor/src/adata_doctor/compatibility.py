from __future__ import annotations

from typing import Any, Dict

from .models import MatrixDiagnosis


def build_compatibility(
    matrices: Dict[str, MatrixDiagnosis], summary: Dict[str, Any]
) -> Dict[str, Dict[str, str]]:
    """Generate simple downstream recommendations."""
    x = matrices.get("X")

    raw_candidates = [
        name for name, d in matrices.items()
        if d.verdict in {"raw_counts", "probably_raw_counts"}
    ]
    recoverable_count_candidates = [
        name for name, d in matrices.items()
        if d.verdict == "log1p_counts_not_normalized"
    ]
    log_candidates = [
        name for name, d in matrices.items()
        if d.verdict in {"log1p_normalized_to_target_sum", "probably_log1p_normalized"}
    ]

    result: Dict[str, Dict[str, str]] = {}

    if x is None:
        result["general"] = {
            "status": "fail",
            "recommendation": "没有可诊断的 X 矩阵。",
        }
        return result

    if x.verdict == "log1p_normalized_to_target_sum":
        result["celltypist_like_input"] = {
            "status": "pass",
            "recommendation": "X 看起来已经是 log1p-normalized；可直接用于需要 log1p normalized 输入的流程。",
        }
    elif x.verdict == "raw_counts":
        result["celltypist_like_input"] = {
            "status": "needs_preprocessing",
            "recommendation": "X 看起来是 raw counts；通常需要 normalize_total 后再 log1p。",
        }
    elif x.verdict == "log1p_counts_not_normalized":
        result["celltypist_like_input"] = {
            "status": "needs_preprocessing",
            "recommendation": "X 像 log1p(raw counts)，但不是标准 target_sum 归一化；建议先 expm1 还原 counts，再 normalize_total+log1p。",
        }
    elif x.verdict in {"scaled_or_other_transformed_matrix", "other_transformed_matrix"}:
        result["celltypist_like_input"] = {
            "status": "fail_or_caution",
            "recommendation": "X 含负值或已被转换，不建议直接作为表达矩阵输入；优先寻找 counts/log-normalized layer。",
        }
    else:
        result["celltypist_like_input"] = {
            "status": "caution",
            "recommendation": "X 状态不够明确，建议结合 layers/raw 与数据来源复核。",
        }

    if raw_candidates:
        result["renormalization"] = {
            "status": "pass",
            "recommendation": f"发现可能的 raw counts 矩阵：{', '.join(raw_candidates)}；可用于重新标准化。",
        }
    elif recoverable_count_candidates:
        result["renormalization"] = {
            "status": "recoverable_with_caution",
            "recommendation": f"发现可能的 log1p(raw counts) 矩阵：{', '.join(recoverable_count_candidates)}；可尝试 expm1 还原 counts 后重新标准化，但需要人工确认。",
        }
    else:
        result["renormalization"] = {
            "status": "caution",
            "recommendation": "未发现明确 raw counts；如果需要从原始 counts 重新处理，建议回到数据源确认。",
        }

    if log_candidates:
        result["visualization_or_marker_plot"] = {
            "status": "pass",
            "recommendation": f"发现可能的 log-normalized 矩阵：{', '.join(log_candidates)}；通常适合表达量可视化。",
        }
    elif recoverable_count_candidates:
        result["visualization_or_marker_plot"] = {
            "status": "caution",
            "recommendation": f"发现可能的 log1p(raw counts) 矩阵：{', '.join(recoverable_count_candidates)}；可用于粗略查看表达，但不等价于 normalize_total 后的 log-normalized 矩阵。",
        }
    else:
        result["visualization_or_marker_plot"] = {
            "status": "caution",
            "recommendation": "未发现明确 log-normalized 矩阵；作图前需要确认是否已经 normalize/log1p。",
        }

    if raw_candidates:
        result["traceability"] = {
            "status": "pass",
            "recommendation": "存在明确 raw counts 或 raw-like layer，数据处理可追溯性较好。",
        }
    elif recoverable_count_candidates:
        result["traceability"] = {
            "status": "caution",
            "recommendation": "存在可疑 log1p(raw counts) 矩阵，具备一定可追溯性，但仍需人工确认。",
        }
    elif summary.get("has_raw"):
        result["traceability"] = {
            "status": "caution",
            "recommendation": "虽然存在 raw.X，但 raw.X 不是明确 raw counts 或标准 log-normalized，不能直接视为可靠原始备份。",
        }
    else:
        result["traceability"] = {
            "status": "caution",
            "recommendation": "缺少 raw/raw-like 矩阵，后续解释和复现需要谨慎。",
        }

    return result
