"""Rule 3: Color and Contrast - Check WCAG contrast ratios."""

from typing import Any

from pptx_accessibility.rules.base import ActionType, BaseRule, Finding, Severity
from pptx_accessibility.utils.color_utils import (
    get_contrast_ratio,
    meets_wcag_aa,
    suggest_darker_color,
    suggest_lighter_color,
)


class ContrastRule(BaseRule):
    """Check color contrast for accessibility."""

    @property
    def rule_id(self) -> str:
        return "rule_03"

    @property
    def rule_name(self) -> str:
        return "Color and Contrast"

    @property
    def description(self) -> str:
        return "Ensures sufficient color contrast between text and background (WCAG 4.5:1 for AA)"

    async def analyze(self, presentation: Any, context: dict[str, Any]) -> list[Finding]:
        """Analyze color contrast.

        Checks:
        - Text-to-background contrast ratio >= 4.5:1 (WCAG AA)
        - Large text (18pt+) >= 3:1
        """
        findings = []
        slide_count = presentation.get_slide_count()

        for slide_idx in range(slide_count):
            text_shapes = presentation.get_all_text_shapes(slide_idx)

            for shape in text_shapes:
                # Skip if no text frame info
                if not shape.get("text_frame"):
                    continue

                text_frame = shape["text_frame"]

                # Check each text run
                for run in text_frame.get("runs", []):
                    font_color = run.get("font_color")
                    font_size = run.get("font_size")

                    # Skip if we don't have color information
                    if not font_color:
                        continue

                    # Assume white background if not specified
                    # TODO: Extract actual background color from slide/shape
                    background_color = "#FFFFFF"

                    try:
                        # Calculate contrast ratio
                        contrast_ratio = get_contrast_ratio(font_color, background_color)

                        # Determine if large text (18pt+ or 14pt+ bold)
                        is_large_text = font_size and font_size >= 18
                        if font_size and font_size >= 14 and run.get("bold"):
                            is_large_text = True

                        # Check if meets WCAG AA
                        meets_aa = meets_wcag_aa(contrast_ratio, is_large_text)

                        if not meets_aa:
                            # Determine severity based on how far off we are
                            if contrast_ratio < 2.0:
                                severity = Severity.CRITICAL
                            elif contrast_ratio < 3.0:
                                severity = Severity.HIGH
                            else:
                                severity = Severity.MEDIUM

                            # Suggest a better color
                            # If text is dark on white, make it darker. If light, suggest darker.
                            suggested_color = suggest_darker_color(
                                font_color,
                                target_contrast=4.5 if not is_large_text else 3.0,
                                background=background_color
                            )

                            findings.append(Finding(
                                rule_id=self.rule_id,
                                slide_number=slide_idx + 1,
                                shape_id=str(shape["shape_id"]),
                                severity=severity,
                                title="Insufficient color contrast",
                                description=f"Contrast ratio {contrast_ratio:.2f}:1 does not meet WCAG AA "
                                          f"{'(3:1 for large text)' if is_large_text else '(4.5:1)'}",
                                action_type=ActionType.AUTO_FIX,
                                suggested_fix=f"Change text color from {font_color} to {suggested_color}",
                                metadata={
                                    "current_color": font_color,
                                    "background_color": background_color,
                                    "contrast_ratio": round(contrast_ratio, 2),
                                    "required_ratio": 3.0 if is_large_text else 4.5,
                                    "suggested_color": suggested_color,
                                    "is_large_text": is_large_text,
                                    "text_preview": run["text"][:50],
                                }
                            ))

                    except Exception as e:
                        # Log but don't fail on color analysis errors
                        continue

        return findings

    async def apply_fix(
        self, presentation: Any, finding: Finding, context: dict[str, Any]
    ) -> bool:
        """Apply contrast fixes.

        Args:
            presentation: Presentation object
            finding: The finding to fix
            context: Additional context

        Returns:
            True if fix was applied successfully
        """
        # TODO: Implement when PPTX writer is ready
        # We would change the font color to the suggested color
        return False
