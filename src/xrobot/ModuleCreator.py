#!/usr/bin/env python3
"""
xrobot_module_generator.py - Quickly create a new XRobot module with standardized manifest (V2).

Features:
- Generates C++ header with MANIFEST block, README, and CMakeLists.txt for the module.
- Supports command-line arguments for class name, description, hardware, constructor args, template args, and dependencies.

Usage:
    python xrobot_module_generator.py MyModule --desc "A blinking LED" --hw led --constructor id=foo gpio=LED
"""

import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

HEADER_TEMPLATE = """#pragma once

// clang-format off
/* === MODULE MANIFEST V2 ===
module_description: {description}
{constructor_args_block}
{template_args_block}
{hardware_block}
{depends_block}
=== END MANIFEST === */
// clang-format on

#include "app_framework.hpp"

class {class_name} : public LibXR::Application {{
public:
  {class_name}(LibXR::HardwareContainer &hw, LibXR::ApplicationManager &app) {{
    // Hardware initialization example:
    // auto dev = hw.template Find<LibXR::GPIO>("led");
  }}

  void OnMonitor() override {{}}

private:
}};
"""

README_TEMPLATE = """# {class_name}

{description}

## Required Hardware
{hardware}
"""

def yaml_block(obj: Any, key: str, indent: int = 2) -> str:
    """
    Output a compliant YAML field block:
    - Empty list/dict/None: key: []
    - Non-empty list/dict: block format, indented
    - String: key: value
    """
    import yaml
    if obj is None or obj == [] or obj == {}:
        return f"{key}: []"
    if isinstance(obj, str):
        return f"{key}: {obj}"
    text = yaml.dump(obj, allow_unicode=True, sort_keys=False, default_flow_style=False)
    pad = " " * indent
    lines = text.splitlines()
    return f"{key}:\n" + "\n".join(pad + l if l.strip() else l for l in lines)

def _auto_type(val: str):
    """Try to convert to int/float/bool if possible, else return original string."""
    v = val.strip()
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    try:
        if v.startswith("0x") or v.startswith("0X"):
            return int(v, 16)
        if '.' in v:
            return float(v)
        return int(v)
    except Exception:
        return v  # fallback as string

def parse_arg(arglist):
    """
    Support name=value (becomes {name: value, type detected}), or name (becomes {name: ""})
    """
    result = []
    for s in arglist:
        if '=' in s:
            k, v = s.split('=', 1)
            result.append({k.strip(): _auto_type(v)})
        else:
            result.append({s.strip(): ""})
    return result

def create_module(
    class_name: str,
    description: str,
    required_hardware: List[str],
    constructor_args: Optional[List[Dict[str, Any]]] = None,
    template_args: Optional[List[Dict[str, Any]]] = None,
    depends: Optional[List[str]] = None,
    output_dir: Path = Path("Modules")
):
    """Create a new XRobot module with standardized manifest and build files."""
    mod_dir = output_dir / class_name
    mod_dir.mkdir(parents=True, exist_ok=True)

    constructor_args = constructor_args or []
    template_args = template_args or []
    depends = depends or []
    required_hardware = required_hardware or []

    hpp_code = HEADER_TEMPLATE.format(
        class_name=class_name,
        description=description,
        constructor_args_block=yaml_block(constructor_args, "constructor_args"),
        template_args_block=yaml_block(template_args, "template_args"),
        hardware_block=yaml_block(required_hardware, "required_hardware"),
        depends_block=yaml_block(depends, "depends"),
    )

    readme_code = README_TEMPLATE.format(
        class_name=class_name,
        description=description,
        hardware=", ".join(required_hardware) if required_hardware else "None"
    )

    (mod_dir / f"{class_name}.hpp").write_text(hpp_code, encoding="utf-8")
    (mod_dir / "README.md").write_text(readme_code, encoding="utf-8")

    # Generate build configuration
    cmake_code = f"""# CMakeLists.txt for {class_name}

# Add module to include path
target_include_directories(xr PUBLIC ${{CMAKE_CURRENT_LIST_DIR}})

# Auto-include source files
file(GLOB MODULE_{class_name.upper()}_SRC
    "${{CMAKE_CURRENT_LIST_DIR}}/*.cpp"
    "${{CMAKE_CURRENT_LIST_DIR}}/*.c"
)

target_sources(xr PRIVATE ${{MODULE_{class_name.upper()}_SRC}})
"""
    (mod_dir / "CMakeLists.txt").write_text(cmake_code, encoding="utf-8")

    print(f"[OK] Module {class_name} generated at {mod_dir}")

def main():
    parser = argparse.ArgumentParser(
        description="Create a new XRobot module (standardized manifest structure)"
    )
    parser.add_argument("class_name", help="Module class/dir name (should match directory name)")
    parser.add_argument("--desc", default="No description provided", help="Module description")
    parser.add_argument("--hw", nargs="*", default=[], help="Required hardware interfaces (logical names)")
    parser.add_argument("--constructor", nargs="*", default=[], help="Constructor args, e.g., id=foo gpio=LED")
    parser.add_argument("--template", nargs="*", default=[], help="Template args, e.g., T=int U=double")
    parser.add_argument("--depends", nargs="*", default=[], help="Dependencies (other modules)")
    parser.add_argument("--out", default="Modules", help="Output directory (default: Modules/)")

    args = parser.parse_args()

    constructor_args = parse_arg(args.constructor)
    template_args = parse_arg(args.template)

    create_module(
        class_name=args.class_name,
        description=args.desc,
        required_hardware=args.hw,
        constructor_args=constructor_args,
        template_args=template_args,
        depends=args.depends,
        output_dir=Path(args.out)
    )

if __name__ == "__main__":
    main()
