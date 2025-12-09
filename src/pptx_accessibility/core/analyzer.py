"""Analysis Orchestrator - coordinates running accessibility rules."""

from typing import Any

from loguru import logger

from pptx_accessibility.pptx_access.reader import PPTXReader
from pptx_accessibility.rules.base import BaseRule, Finding, Severity
from pptx_accessibility.rules.rule_01_structure import StructureRule
from pptx_accessibility.rules.rule_03_contrast import ContrastRule
from pptx_accessibility.rules.rule_04_fonts import FontsRule


class AccessibilityAnalyzer:
    """Orchestrates accessibility analysis by running multiple rules."""

    def __init__(self) -> None:
        """Initialize analyzer with available rules."""
        self.available_rules: dict[str, BaseRule] = {
            "rule_01": StructureRule(),
            "rule_03": ContrastRule(),
            "rule_04": FontsRule(),
        }

    async def analyze_presentation(
        self,
        presentation: PPTXReader,
        enabled_rules: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run accessibility analysis on a presentation.

        Args:
            presentation: PPTXReader instance
            enabled_rules: List of rule IDs to run (default: all)
            context: Additional context for rules

        Returns:
            Dictionary with findings, scores, and metadata
        """
        if enabled_rules is None:
            enabled_rules = list(self.available_rules.keys())

        if context is None:
            context = {}

        logger.info(f"Starting analysis with {len(enabled_rules)} rules")

        all_findings: list[Finding] = []
        rule_results: dict[str, list[Finding]] = {}

        # Run each enabled rule
        for rule_id in enabled_rules:
            if rule_id not in self.available_rules:
                logger.warning(f"Unknown rule: {rule_id}, skipping")
                continue

            rule = self.available_rules[rule_id]
            logger.info(f"Running {rule.rule_name} ({rule_id})")

            try:
                findings = await rule.analyze(presentation, context)
                rule_results[rule_id] = findings
                all_findings.extend(findings)
                logger.info(f"  → Found {len(findings)} issues")

            except Exception as e:
                logger.error(f"Error running {rule_id}: {e}")
                # Continue with other rules even if one fails
                rule_results[rule_id] = []

        # Calculate scores
        scores = self._calculate_scores(all_findings, presentation.get_slide_count())

        # Group findings by severity
        findings_by_severity = self._group_by_severity(all_findings)

        # Group findings by slide
        findings_by_slide = self._group_by_slide(all_findings)

        return {
            "total_findings": len(all_findings),
            "findings": [self._finding_to_dict(f) for f in all_findings],
            "findings_by_severity": findings_by_severity,
            "findings_by_slide": findings_by_slide,
            "rule_results": {
                rule_id: len(findings) for rule_id, findings in rule_results.items()
            },
            "scores": scores,
            "metadata": {
                "slide_count": presentation.get_slide_count(),
                "rules_run": enabled_rules,
                "presentation_title": presentation.get_presentation_metadata().get("title"),
            },
        }

    def _calculate_scores(self, findings: list[Finding], slide_count: int) -> dict[str, Any]:
        """Calculate accessibility scores.

        Args:
            findings: List of findings
            slide_count: Total number of slides

        Returns:
            Dictionary with various scores
        """
        if slide_count == 0:
            return {"overall_score": 100, "grade": "A"}

        # Count findings by severity
        severity_counts = {
            "critical": sum(1 for f in findings if f.severity == Severity.CRITICAL),
            "high": sum(1 for f in findings if f.severity == Severity.HIGH),
            "medium": sum(1 for f in findings if f.severity == Severity.MEDIUM),
            "low": sum(1 for f in findings if f.severity == Severity.LOW),
            "info": sum(1 for f in findings if f.severity == Severity.INFO),
        }

        # Calculate weighted score (0-100)
        # Start at 100, deduct points based on severity
        penalty = (
            severity_counts["critical"] * 10
            + severity_counts["high"] * 5
            + severity_counts["medium"] * 2
            + severity_counts["low"] * 1
            + severity_counts["info"] * 0.5
        )

        # Normalize by slide count to account for presentation size
        penalty_per_slide = penalty / slide_count
        overall_score = max(0, 100 - penalty_per_slide)

        # Assign grade
        if overall_score >= 90:
            grade = "A"
        elif overall_score >= 75:
            grade = "B"
        elif overall_score >= 60:
            grade = "C"
        elif overall_score >= 40:
            grade = "D"
        else:
            grade = "F"

        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "severity_counts": severity_counts,
            "total_issues": len(findings),
            "issues_per_slide": round(len(findings) / slide_count, 2),
        }

    def _group_by_severity(self, findings: list[Finding]) -> dict[str, int]:
        """Group findings by severity level."""
        return {
            "critical": sum(1 for f in findings if f.severity == Severity.CRITICAL),
            "high": sum(1 for f in findings if f.severity == Severity.HIGH),
            "medium": sum(1 for f in findings if f.severity == Severity.MEDIUM),
            "low": sum(1 for f in findings if f.severity == Severity.LOW),
            "info": sum(1 for f in findings if f.severity == Severity.INFO),
        }

    def _group_by_slide(self, findings: list[Finding]) -> dict[int, int]:
        """Group findings by slide number."""
        slide_counts: dict[int, int] = {}
        for finding in findings:
            slide_num = finding.slide_number
            slide_counts[slide_num] = slide_counts.get(slide_num, 0) + 1
        return slide_counts

    def _finding_to_dict(self, finding: Finding) -> dict[str, Any]:
        """Convert Finding to dictionary for JSON serialization."""
        return {
            "rule_id": finding.rule_id,
            "slide_number": finding.slide_number,
            "shape_id": finding.shape_id,
            "severity": finding.severity.value,
            "title": finding.title,
            "description": finding.description,
            "action_type": finding.action_type.value,
            "suggested_fix": finding.suggested_fix,
            "metadata": finding.metadata,
        }

    def get_available_rules(self) -> dict[str, dict[str, str]]:
        """Get information about available rules.

        Returns:
            Dictionary mapping rule IDs to rule info
        """
        return {
            rule_id: {
                "rule_id": rule.rule_id,
                "name": rule.rule_name,
                "description": rule.description,
            }
            for rule_id, rule in self.available_rules.items()
        }
