"""Base rule class for accessibility checks.

All accessibility rules inherit from BaseRule and implement the analyze() and apply_fix() methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(Enum):
    """Severity level of an accessibility finding."""

    CRITICAL = "critical"  # Blocks accessibility completely
    HIGH = "high"  # Major accessibility issue
    MEDIUM = "medium"  # Moderate accessibility issue
    LOW = "low"  # Minor improvement
    INFO = "info"  # Informational only


class ActionType(Enum):
    """Type of action that can be taken to fix a finding."""

    AUTO_FIX = "auto_fix"  # Can be fixed automatically
    SUGGEST = "suggest"  # Requires human decision
    MANUAL = "manual"  # Cannot be automated


@dataclass
class Finding:
    """Represents a single accessibility finding."""

    rule_id: str  # e.g., "rule_01", "rule_02"
    slide_number: int  # Slide/page number (1-indexed)
    shape_id: str | None  # Shape/object ID (None for slide-level issues)
    severity: Severity
    title: str  # Short title of the issue
    description: str  # Detailed description
    action_type: ActionType
    suggested_fix: str | None  # Suggested fix description
    metadata: dict[str, Any] = field(default_factory=dict)  # Additional context

    def to_dict(self) -> dict[str, Any]:
        """Convert finding to dictionary for JSON serialization."""
        return {
            "rule_id": self.rule_id,
            "slide_number": self.slide_number,
            "shape_id": self.shape_id,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "action_type": self.action_type.value,
            "suggested_fix": self.suggested_fix,
            "metadata": self.metadata,
        }


class BaseRule(ABC):
    """Abstract base class for all accessibility rules."""

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize rule with optional configuration.

        Args:
            config: Rule-specific configuration options
        """
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique rule identifier (e.g., 'rule_01')."""
        pass

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Human-readable rule name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Rule description explaining what it checks."""
        pass

    @abstractmethod
    async def analyze(self, presentation: Any, context: dict[str, Any]) -> list[Finding]:
        """Analyze presentation and return findings.

        Args:
            presentation: Presentation object (PPTX or PDF wrapper)
            context: Additional context (file_type, session_id, etc.)

        Returns:
            List of findings discovered by this rule
        """
        pass

    @abstractmethod
    async def apply_fix(
        self, presentation: Any, finding: Finding, context: dict[str, Any]
    ) -> bool:
        """Apply the fix for a specific finding.

        Args:
            presentation: Presentation object (PPTX or PDF wrapper)
            finding: The finding to fix
            context: Additional context

        Returns:
            True if fix was successfully applied, False otherwise
        """
        pass

    def calculate_score(self, findings: list[Finding]) -> float:
        """Calculate accessibility score (0-100) based on findings.

        Args:
            findings: List of findings for this rule

        Returns:
            Score from 0 (worst) to 100 (perfect)
        """
        if not findings:
            return 100.0

        # Weight findings by severity
        severity_weights = {
            Severity.CRITICAL: 10,
            Severity.HIGH: 5,
            Severity.MEDIUM: 2,
            Severity.LOW: 1,
            Severity.INFO: 0,
        }

        total_weight = sum(severity_weights[f.severity] for f in findings)

        # Assume max 10 critical issues as baseline for scoring
        max_weight = 100

        score = max(0.0, 100.0 - (total_weight / max_weight * 100))
        return round(score, 1)

    def supports_file_type(self, file_type: str) -> bool:
        """Check if this rule supports the given file type.

        Args:
            file_type: 'pptx' or 'pdf'

        Returns:
            True if rule supports this file type
        """
        # By default, rules support both file types
        # Override in specific rules if needed
        return True
