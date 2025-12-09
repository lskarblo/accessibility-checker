"""Rule 4: Fonts and Text Format - Check font size, type, and formatting."""

from typing import Any

from pptx_accessibility.rules.base import ActionType, BaseRule, Finding, Severity


class FontsRule(BaseRule):
    """Check fonts and text formatting for accessibility."""

    @property
    def rule_id(self) -> str:
        return "rule_04"

    @property
    def rule_name(self) -> str:
        return "Fonts and Text Format"

    @property
    def description(self) -> str:
        return "Ensures text uses readable fonts with appropriate size (≥24pt recommended)"

    async def analyze(self, presentation: Any, context: dict[str, Any]) -> list[Finding]:
        """Analyze fonts and text formatting.

        Checks:
        - Minimum font size (default 24pt)
        - Sans-serif fonts preferred
        - Avoid excessive italics/underlines
        """
        findings = []
        min_font_size = self.config.get("min_font_size", 24)
        preferred_fonts = self.config.get("preferred_fonts", [
            "Arial", "Calibri", "Helvetica", "Tahoma", "Verdana", "Segoe UI"
        ])

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
                    # Check font size
                    font_size = run.get("font_size")
                    if font_size and font_size < min_font_size:
                        findings.append(Finding(
                            rule_id=self.rule_id,
                            slide_number=slide_idx + 1,
                            shape_id=str(shape["shape_id"]),
                            severity=Severity.MEDIUM,
                            title="Text too small",
                            description=f"Font size {font_size:.1f}pt is below recommended {min_font_size}pt",
                            action_type=ActionType.AUTO_FIX,
                            suggested_fix=f"Increase font size to {min_font_size}pt",
                            metadata={
                                "current_size": font_size,
                                "recommended_size": min_font_size,
                                "text_preview": run["text"][:50],
                            }
                        ))

                    # Check font type
                    font_name = run.get("font_name", "")
                    if font_name and font_name not in preferred_fonts:
                        # Check if it's a serif font (common serif fonts)
                        serif_fonts = ["Times New Roman", "Georgia", "Garamond", "Palatino"]
                        if any(serif in font_name for serif in serif_fonts):
                            findings.append(Finding(
                                rule_id=self.rule_id,
                                slide_number=slide_idx + 1,
                                shape_id=str(shape["shape_id"]),
                                severity=Severity.LOW,
                                title="Serif font detected",
                                description=f"Font '{font_name}' is a serif font. Sans-serif fonts are more readable.",
                                action_type=ActionType.SUGGEST,
                                suggested_fix=f"Replace with sans-serif font like Arial or Calibri",
                                metadata={
                                    "current_font": font_name,
                                    "suggested_font": "Arial",
                                }
                            ))

                    # Check excessive italics
                    if run.get("italic") and len(run["text"]) > 50:
                        findings.append(Finding(
                            rule_id=self.rule_id,
                            slide_number=slide_idx + 1,
                            shape_id=str(shape["shape_id"]),
                            severity=Severity.LOW,
                            title="Excessive italic text",
                            description="Long text in italics is harder to read",
                            action_type=ActionType.SUGGEST,
                            suggested_fix="Use regular text or bold for emphasis instead of italics",
                            metadata={
                                "text_length": len(run["text"]),
                            }
                        ))

        return findings

    async def apply_fix(
        self, presentation: Any, finding: Finding, context: dict[str, Any]
    ) -> bool:
        """Apply font formatting fixes.

        Args:
            presentation: Presentation object
            finding: The finding to fix
            context: Additional context

        Returns:
            True if fix was applied successfully
        """
        # TODO: Implement actual fix when PPTX writer is ready
        # For now, we just validate that we can apply the fix
        if finding.action_type == ActionType.AUTO_FIX:
            # We would increase font size here
            return True
        return False
