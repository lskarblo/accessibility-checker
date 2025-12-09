"""Color utilities for WCAG contrast calculations."""

import re
from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., '#FF0000' or 'FF0000')

    Returns:
        RGB tuple (r, g, b) with values 0-255
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color.

    Args:
        r: Red value (0-255)
        g: Green value (0-255)
        b: Blue value (0-255)

    Returns:
        Hex color string (e.g., '#FF0000')
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def get_relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Calculate relative luminance according to WCAG 2.1.

    Args:
        rgb: RGB tuple (r, g, b) with values 0-255

    Returns:
        Relative luminance (0-1)
    """
    # Convert to 0-1 range
    r, g, b = [x / 255.0 for x in rgb]

    # Apply gamma correction
    def gamma_correct(val: float) -> float:
        if val <= 0.03928:
            return val / 12.92
        return ((val + 0.055) / 1.055) ** 2.4

    r = gamma_correct(r)
    g = gamma_correct(g)
    b = gamma_correct(b)

    # Calculate luminance
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two colors.

    Args:
        color1: First color as hex string
        color2: Second color as hex string

    Returns:
        Contrast ratio (1-21)
    """
    rgb1 = hex_to_rgb(color1)
    rgb2 = hex_to_rgb(color2)

    lum1 = get_relative_luminance(rgb1)
    lum2 = get_relative_luminance(rgb2)

    # Ensure lum1 is the lighter color
    if lum1 < lum2:
        lum1, lum2 = lum2, lum1

    # Calculate contrast ratio
    return (lum1 + 0.05) / (lum2 + 0.05)


def meets_wcag_aa(contrast_ratio: float, large_text: bool = False) -> bool:
    """Check if contrast ratio meets WCAG AA standard.

    Args:
        contrast_ratio: Contrast ratio (1-21)
        large_text: True if text is large (18pt+ or 14pt+ bold)

    Returns:
        True if meets WCAG AA
    """
    if large_text:
        return contrast_ratio >= 3.0
    return contrast_ratio >= 4.5


def meets_wcag_aaa(contrast_ratio: float, large_text: bool = False) -> bool:
    """Check if contrast ratio meets WCAG AAA standard.

    Args:
        contrast_ratio: Contrast ratio (1-21)
        large_text: True if text is large (18pt+ or 14pt+ bold)

    Returns:
        True if meets WCAG AAA
    """
    if large_text:
        return contrast_ratio >= 4.5
    return contrast_ratio >= 7.0


def suggest_darker_color(hex_color: str, target_contrast: float = 4.5,
                         background: str = "#FFFFFF") -> str:
    """Suggest a darker version of the color to meet contrast requirements.

    Args:
        hex_color: Original color as hex
        target_contrast: Target contrast ratio
        background: Background color as hex

    Returns:
        Suggested darker color as hex
    """
    rgb = list(hex_to_rgb(hex_color))

    # Try darkening the color incrementally
    for factor in range(1, 20):
        darker_rgb = tuple(max(0, int(c * (1 - factor * 0.05))) for c in rgb)
        darker_hex = rgb_to_hex(*darker_rgb)

        contrast = get_contrast_ratio(darker_hex, background)
        if contrast >= target_contrast:
            return darker_hex

    # If can't achieve target, return black
    return "#000000"


def suggest_lighter_color(hex_color: str, target_contrast: float = 4.5,
                          background: str = "#000000") -> str:
    """Suggest a lighter version of the color to meet contrast requirements.

    Args:
        hex_color: Original color as hex
        target_contrast: Target contrast ratio
        background: Background color as hex

    Returns:
        Suggested lighter color as hex
    """
    rgb = list(hex_to_rgb(hex_color))

    # Try lightening the color incrementally
    for factor in range(1, 20):
        lighter_rgb = tuple(min(255, int(c + (255 - c) * factor * 0.05)) for c in rgb)
        lighter_hex = rgb_to_hex(*lighter_rgb)

        contrast = get_contrast_ratio(lighter_hex, background)
        if contrast >= target_contrast:
            return lighter_hex

    # If can't achieve target, return white
    return "#FFFFFF"
