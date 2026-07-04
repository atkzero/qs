#!/usr/bin/env python3
"""Generate a Material 3 color scheme JSON from a wallpaper image."""

import sys
import json
import argparse
from pathlib import Path

from material_color_utilities import (
    quantize, hexfromrgb, Hct, DynamicScheme,
    MaterialDynamicColors, Variant, Tone
)

def rgb_to_hex(rgb: int) -> str:
    """Convert RGB int to hex string."""
    return f"#{hexfromrgb(rgb)}"

def generate_scheme(image_path: str, scheme_name: str = "custom", 
                    mode: str = "dark", flavour: str = "auto") -> dict:
    """Generate a full Material 3 scheme from an image."""
    
    # Quantize the image to get the dominant color
    from PIL import Image
    img = Image.open(image_path)
    img_small = img.resize((128, 128))  # Speed up quantization
    pixels = list(img_small.getdata())
    
    # Convert to format material_color_utilities expects
    argb_pixels = []
    for r, g, b in pixels[:5000]:
        argb = (0xFF << 24) | (r << 16) | (g << 8) | b
        argb_pixels.append(argb)
    
    # Get dominant colors
    colors = quantize(argb_pixels, 128)
    dominant = colors[0] if colors else 0xFF0000FF
    
    # Create a dynamic scheme
    source_color_hct = Hct(dominant)
    variant = Variant.TONAL_SPOT
    
    is_dark = mode == "dark"
    dynamic_scheme = DynamicScheme(
        source_color_hct, variant, is_dark,
        contrast_level=0.0
    )
    
    def color_value(name: str) -> str:
        color = MaterialDynamicColors.get(name)
        if color is None:
            return "#000000"
        argb = color.get_argb(dynamic_scheme)
        return rgb_to_hex(argb)
    
    scheme = {
        "name": scheme_name,
        "flavour": flavour if flavour != "auto" else "custom",
        "mode": mode,
    }
    
    # Map all Material 3 color roles
    color_roles = [
        "primary", "on_primary", "primary_container", "on_primary_container",
        "secondary", "on_secondary", "secondary_container", "on_secondary_container",
        "tertiary", "on_tertiary", "tertiary_container", "on_tertiary_container",
        "error", "on_error", "error_container", "on_error_container",
        "background", "on_background", "surface", "on_surface",
        "surface_variant", "on_surface_variant",
        "outline", "outline_variant",
        "inverse_surface", "inverse_on_surface", "inverse_primary",
        "shadow", "scrim",
    ]
    
    for role in color_roles:
        scheme[role] = color_value(role)
    
    return scheme


def main():
    parser = argparse.ArgumentParser(description="Generate M3 color scheme from wallpaper")
    parser.add_argument("image", help="Path to wallpaper image")
    parser.add_argument("--name", default="custom", help="Scheme name")
    parser.add_argument("--mode", choices=["dark", "light"], default="dark")
    parser.add_argument("--flavour", default="auto")
    parser.add_argument("--output", "-o", help="Output file path (default: stdout)")
    
    args = parser.parse_args()
    
    scheme = generate_scheme(args.image, args.name, args.mode, args.flavour)
    json_output = json.dumps(scheme, indent=2)
    
    if args.output:
        Path(args.output).write_text(json_output)
        print(f"Scheme written to {args.output}")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
