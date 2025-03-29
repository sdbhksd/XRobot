#!/usr/bin/env python3
"""
xrobot_add_mod.py - 添加模块仓库或追加模块实例配置

Usage 示例：
  # 添加模块仓库（默认写入 Modules/modules.yaml）
  python xrobot_add_mod.py https://github.com/yourorg/BlinkLED.git --version main

  # 追加模块实例（默认写入 User/xrobot.yaml）
  python xrobot_add_mod.py BlinkLED
"""

import argparse
import yaml
from pathlib import Path
from urllib.parse import urlparse
from collections import OrderedDict

DEFAULT_REPO_CONFIG = Path("Modules/modules.yaml")
DEFAULT_INSTANCE_CONFIG = Path("User/xrobot.yaml")
MODULES_DIR = Path("Modules")

def is_repo_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")

def extract_name_from_repo(repo: str) -> str:
    return Path(urlparse(repo).path).stem

def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}

def save_yaml(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

def parse_manifest_from_header(header_path: Path) -> dict:
    content = header_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    block = []
    inside = False

    for line in lines:
        stripped = line.strip()
        if stripped == "/* === MODULE MANIFEST ===":
            inside = True
            continue
        if stripped == "=== END MANIFEST === */":
            break
        if inside:
            block.append(line.replace("/*", "  ").replace("*/", "  ").rstrip())

    try:
        return yaml.safe_load("\n".join(block)) or {}
    except yaml.YAMLError as e:
        print(f"[ERROR] Failed to parse manifest: {e}")
        return {}

def append_module_instance(module_name: str, config_path: Path):
    header_path = MODULES_DIR / module_name / f"{module_name}.hpp"
    if not header_path.exists():
        print(f"[ERROR] Module header not found: {header_path}")
        return

    manifest = parse_manifest_from_header(header_path)
    args = manifest.get("constructor_args", {})
    args_ordered = OrderedDict()
    if isinstance(args, dict):
        args_ordered.update(args)
    elif isinstance(args, list):
        for item in args:
            if isinstance(item, dict):
                args_ordered.update(item)

    data = load_yaml(config_path)
    if "modules" not in data or not isinstance(data["modules"], list):
        data["modules"] = []

    data["modules"].append({
        "name": module_name,
        "constructor_args": dict(args_ordered)
    })

    save_yaml(config_path, data)
    print(f"[SUCCESS] Appended module instance '{module_name}' to {config_path}")

def add_repo_entry(repo: str, version: str, config_path: Path):
    name = extract_name_from_repo(repo)
    data = load_yaml(config_path)
    modules = data.get("modules", [])

    if any(m.get("name") == name for m in modules):
        print(f"[WARN] Module '{name}' already exists in {config_path}. Skipping.")
        return

    entry = {"name": name, "repo": repo}
    if version:
        entry["version"] = version
    modules.append(entry)

    save_yaml(config_path, {"modules": modules})
    print(f"[SUCCESS] Added repo module '{name}' to {config_path}")

def main():
    parser = argparse.ArgumentParser(description="Add module repo or instance config to YAML")
    parser.add_argument("target", help="Repo URL or local module name")
    parser.add_argument("--version", "-v", help="Branch or tag (repo only)")
    parser.add_argument("--config", "-c", help="YAML file path to write (auto default)")

    args = parser.parse_args()

    # 判断类型并选择默认 config 路径
    if is_repo_url(args.target):
        config_path = Path(args.config) if args.config else DEFAULT_REPO_CONFIG
        add_repo_entry(args.target, args.version, config_path)
    else:
        config_path = Path(args.config) if args.config else DEFAULT_INSTANCE_CONFIG
        append_module_instance(args.target, config_path)

if __name__ == "__main__":
    main()
