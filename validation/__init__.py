"""
Validation and verification framework (Phase 8).

Verification: code behaves as specified (synthetic/property/regression tests).
Validation: correspondence with external expert/listening data (scaffolding only
until corpora are supplied).
"""

from validation.metrics import (
    bootstrap_ci,
    kendall_tau,
    krippendorff_alpha_placeholder,
    mean_absolute_error,
    root_mean_square_error,
    spearman_correlation,
)
from validation.report import generate_validation_report
from validation.schemas import ExpertAnnotation, load_expert_annotations
from validation.verification import VerificationResult, run_verification_suite

__all__ = [
    "spearman_correlation",
    "kendall_tau",
    "root_mean_square_error",
    "mean_absolute_error",
    "bootstrap_ci",
    "krippendorff_alpha_placeholder",
    "ExpertAnnotation",
    "load_expert_annotations",
    "VerificationResult",
    "run_verification_suite",
    "generate_validation_report",
]
