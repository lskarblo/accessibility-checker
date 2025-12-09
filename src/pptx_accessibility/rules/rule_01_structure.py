"""Rule 1: Structure and Reading Order - Check slide structure and titles."""

from typing import Any

from pptx_accessibility.rules.base import ActionType, BaseRule, Finding, Severity


class StructureRule(BaseRule):
    """Check presentation structure and reading order."""

    @property
    def rule_id(self) -> str:
        return "rule_01"

    @property
    def rule_name(self) -> str:
        return "Structure and Reading Order"

    @property
    def description(self) -> str:
        return "Ensures all slides have titles and use proper layout structure"

    async def analyze(self, presentation: Any, context: dict[str, Any]) -> list[Finding]:
        """Analyze presentation structure.

        Checks:
        - Every slide has a title
        - Title is in title placeholder (not text box)
        - Logical reading order
        """
        findings = []
        slide_count = presentation.get_slide_count()

        for slide_idx in range(slide_count):
            # Check if slide has a title
            has_title = presentation.has_title(slide_idx)
            title = presentation.get_slide_title(slide_idx)

            if not has_title or not title:
                findings.append(Finding(
                    rule_id=self.rule_id,
                    slide_number=slide_idx + 1,
                    shape_id=None,
                    severity=Severity.CRITICAL,
                    title="Missing slide title",
                    description=f"Slide {slide_idx + 1} does not have a title. Titles are essential for navigation and screen readers.",
                    action_type=ActionType.SUGGEST,
                    suggested_fix="Add a descriptive title to the slide using the title placeholder",
                    metadata={
                        "layout_name": presentation.get_slide_layout_name(slide_idx),
                    }
                ))

            # Check if title is too short (likely not descriptive)
            elif title and len(title) < 3:
                findings.append(Finding(
                    rule_id=self.rule_id,
                    slide_number=slide_idx + 1,
                    shape_id=None,
                    severity=Severity.MEDIUM,
                    title="Title too short",
                    description=f"Slide title '{title}' is very short and may not be descriptive enough",
                    action_type=ActionType.SUGGEST,
                    suggested_fix="Use a more descriptive title that summarizes the slide content",
                    metadata={
                        "current_title": title,
                        "title_length": len(title),
                    }
                ))

            # Check layout usage
            layout_name = presentation.get_slide_layout_name(slide_idx)
            if "blank" in layout_name.lower():
                # Blank layouts often mean content not using placeholders
                text_shapes = presentation.get_all_text_shapes(slide_idx)
                non_placeholder_count = sum(1 for shape in text_shapes if not shape.get("is_placeholder"))

                if non_placeholder_count > 0:
                    findings.append(Finding(
                        rule_id=self.rule_id,
                        slide_number=slide_idx + 1,
                        shape_id=None,
                        severity=Severity.MEDIUM,
                        title="Blank layout with text boxes",
                        description=f"Slide uses blank layout with {non_placeholder_count} text boxes. Using standard layouts with placeholders improves accessibility.",
                        action_type=ActionType.SUGGEST,
                        suggested_fix="Consider using a standard layout (Title Slide, Title and Content, etc.)",
                        metadata={
                            "layout_name": layout_name,
                            "non_placeholder_count": non_placeholder_count,
                        }
                    ))

        return findings

    async def apply_fix(
        self, presentation: Any, finding: Finding, context: dict[str, Any]
    ) -> bool:
        """Apply structure fixes.

        Args:
            presentation: Presentation object
            finding: The finding to fix
            context: Additional context

        Returns:
            True if fix was applied successfully
        """
        # TODO: Implement when PPTX writer is ready
        # For missing titles, we could add a placeholder title
        return False
