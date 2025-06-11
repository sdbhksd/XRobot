#!/usr/bin/env python3
"""
xrobot_add_mod.py - Add a module repository to modules.yaml or append a module instance config.

Usage examples:
  python xrobot_add_mod.py xrobot-org/BlinkLED@main
  python xrobot_add_mod.py BlinkLED
"""

import argparse
import yaml
from pathlib import Path

# Default config file paths
DEFAULT_REPO_CONFIG = Path("Modules/modules.yaml")
DEFAULT_INSTANCE_CONFIG = Path("User/xrobot.yaml")
MODULES_DIR = Path("Modules")

# Import utility functions from local module
from xrobot.ModuleParser import load_single_module, parse_constructor_args

def is_repo_id(s: str) -> bool:
    """
    Determine if string is a repo ID (e.g., 'namespace/ModuleName' or 'namespace/ModuleName@version').
    """
    return "/" in s

def get_next_instance_id(modules: list, base_name: str) -> str:
    """
    Return a unique instance id for the given module name, such as 'BlinkLED_0', 'BlinkLED_1', etc.
    """
    existing = [m.get("id", "") for m in modules if m.get("name") == base_name]
    nums = []
    for eid in existing:
        if eid and eid.startswith(base_name + "_"):
            try:
                nums.append(int(eid[len(base_name) + 1:]))
            except Exception:
                pass
    next_num = (max(nums) + 1) if nums else 0
    return f"{base_name}_{next_num}"

def append_module_instance(module_name: str, config_path: Path, instance_id: str = None):
    """
    Append a module instance (with id and constructor args) to the user config YAML.
    """
    mod_dir = MODULES_DIR / module_name
    manifest = load_single_module(mod_dir)
    if not manifest:
        print(f"[ERROR] Module manifest not found in: {mod_dir}")
        return

    # Parse constructor and template args in order
    args_ordered = parse_constructor_args(manifest.constructor_args)
    template_args_ordered = parse_constructor_args(manifest.template_args)

    # Load or create config file
    if config_path.exists():
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    else:
        data = {}
    if "modules" not in data or not isinstance(data["modules"], list):
        data["modules"] = []

    # Auto-generate unique instance id if not given
    inst_id = instance_id or get_next_instance_id(data["modules"], module_name)

    mod_entry = {
        "id": inst_id,
        "name": module_name,
        "constructor_args": dict(args_ordered)
    }
    if template_args_ordered:
        mod_entry["template_args"] = dict(template_args_ordered)

    data["modules"].append(mod_entry)

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"[SUCCESS] Appended module instance '{module_name}' as id '{inst_id}' to {config_path}")

def add_repo_entry(repo_id: str, config_path: Path):
    """
    Add a new repo module (as a plain string, e.g., 'namespace/ModuleName[@version]') to modules.yaml.
    """
    if config_path.exists():
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    else:
        data = {}
    if "modules" not in data or not isinstance(data["modules"], list):
        data["modules"] = []

    if repo_id in data["modules"]:
        print(f"[WARN] Module '{repo_id}' already exists in {config_path}. Skipping.")
        return

    data["modules"].append(repo_id)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"[SUCCESS] Added repo module '{repo_id}' to {config_path}")

def main():
    parser = argparse.ArgumentParser(description="Add a module repo or instance config to a YAML file")
    parser.add_argument("target", help="namespace/ModuleName[@version] or local module name")
    parser.add_argument("--config", "-c", help="Path to YAML config file (optional, auto default)")
    parser.add_argument("--instance-id", help="Optional: manually set the module instance id")

    args = parser.parse_args()

    if is_repo_id(args.target):
        config_path = Path(args.config) if args.config else DEFAULT_REPO_CONFIG
        add_repo_entry(args.target, config_path)
    else:
        config_path = Path(args.config) if args.config else DEFAULT_INSTANCE_CONFIG
        append_module_instance(args.target, config_path, args.instance_id)

if __name__ == "__main__":
    main()
