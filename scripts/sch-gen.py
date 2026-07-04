#!/usr/bin/env python3
"""Generate a Material 3 color scheme from a single seed color."""

import sys
import json
import argparse
from materialyoucolor.hct.hct import Hct
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.dynamiccolor.color_spec import COLOR_NAMES

def generate_scheme(seed_argb: int, name="custom", mode="dark", flavour="custom"):
    hct = Hct.from_int(seed_argb)
    scheme = SchemeTonalSpot(hct, mode == "dark", 0.0)
    mdc = MaterialDynamicColors(spec="2021")

    result = {"name": name, "flavour": flavour, "mode": mode}
    
    errors = []
    for color_name in COLOR_NAMES:
        try:
            color_obj = getattr(mdc, color_name, None)
            if color_obj is not None:
                hex_val = color_obj.get_hex(scheme)[:-2]
                result[color_name] = f"#{hex_val}"
            else:
                errors.append(f"{color_name}: no such attribute")
        except Exception as e:
            errors.append(f"{color_name}: {type(e).__name__}: {e}")

    # Debug: print failures to stderr so stdout is still clean JSON
    if errors:
        import sys
        print("WARNINGS:", file=sys.stderr)
        for err in errors[:10]:  # Limit output
            print(f"  {err}", file=sys.stderr)

    return result

def main():
    parser = argparse.ArgumentParser(description="Generate M3 scheme from seed color")
    parser.add_argument("color", help="Seed color as 0xAARRGGBB hex (e.g. 0xFF4285F4)")
    parser.add_argument("--name", default="custom")
    parser.add_argument("--mode", choices=["dark", "light"], default="dark")
    parser.add_argument("--flavour", default="custom")
    args = parser.parse_args()

    seed = int(args.color, 16)
    scheme = generate_scheme(seed, name=args.name, mode=args.mode, flavour=args.flavour)
    print(json.dumps(scheme))


if __name__ == "__main__":
    main()
