#!/usr/bin/env python3
"""
xrobot_sync_modules.py - XRobot recursive module synchronization tool.

- Reads modules.yaml and sources.yaml to synchronize module repositories.
- Supports recursive dependency resolution based on MANIFEST in module header.
- Ensures consistent version for each module in the dependency graph.

Usage:
    python xrobot_sync_modules.py
    python xrobot_sync_modules.py --config Modules/modules.yaml --sources Modules/sources.yaml
    python xrobot_sync_modules.py --config https://example.com/modules.yaml --sources https://example.com/sources.yaml
"""

import argparse
import sys
import subprocess
import yaml
import re
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Set, Tuple

# Import your own source management package (implement load_yaml as shown below if needed)
from xrobot.SourceManager import SourceManager, load_yaml

CONFIG_TEMPLATE = """# XRobot module configuration example
modules:
  - xrobot-org/BlinkLED
"""

MODULES_DIR = Path("Modules")
DEFAULT_CONFIG = MODULES_DIR / "modules.yaml"
DEFAULT_SOURCES = MODULES_DIR / "sources.yaml"

def is_url(path) -> bool:
    """Check if a path is an HTTP(S) URL."""
    return str(path).startswith("http://") or str(path).startswith("https://")

def download_url_to_file(url: str, dest_path: Path):
    """Download the content of a URL to a local file."""
    print(f"[INFO] Downloading {url} -> {dest_path}")
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    dest_path.write_text(resp.text, encoding="utf-8")

def parse_modid(modid: str) -> Tuple[str, str, Optional[str]]:
    """
    Parse a module id of the form 'namespace/ModuleName[@version]'
    Returns: (namespace, module_name, version_or_none)
    """
    m = re.match(r"^([^/@]+)/([^/@]+)(?:@(.+))?$", modid)
    if not m:
        raise ValueError(f"Invalid module id: {modid}")
    return m.group(1), m.group(2), m.group(3)

def execute_git_command(cmd: list, workdir: Path = None):
    """
    Execute a git command and check for errors.
    """
    try:
        subprocess.run(cmd, cwd=workdir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git command failed: {' '.join(cmd)}\n{str(e)}")
        sys.exit(2)

def sync_module_git(modid: str, repo: str, ref: Optional[str], base_dir: Path):
    """
    Synchronize a module using git clone/fetch/pull.
    Supports branch/tag/commit checkout.
    """
    ns, name, _ = parse_modid(modid)
    module_path = base_dir / name

    if module_path.exists() and (module_path / ".git").exists():
        print(f"[INFO] Updating module: {modid}")
        execute_git_command(["git", "fetch", "--all"], workdir=module_path)
        execute_git_command(["git", "pull"], workdir=module_path)
        if ref:
            execute_git_command(["git", "checkout", ref], workdir=module_path)
        else:
            execute_git_command(["git", "checkout", "master"], workdir=module_path)
    else:
        print(f"[INFO] Cloning new module: {modid}")
        clone_cmd = ["git", "clone", "--recurse-submodules"]
        if ref:
            clone_cmd += ["--branch", ref]
        clone_cmd += [repo, str(module_path)]
        execute_git_command(clone_cmd)
        # In rare cases, branch/tag must be checked out explicitly after clone
        if ref and not ref.startswith("v") and not re.match(r"^\d", ref):
            execute_git_command(["git", "checkout", ref], workdir=module_path)

def parse_manifest_from_header(hpp_path: Path) -> Optional[dict]:
    """
    Parse the MANIFEST block from a module .hpp header file.
    """
    try:
        txt = hpp_path.read_text(encoding="utf-8")
    except Exception:
        return None
    match = re.search(
        r"/\*\s*=== MODULE MANIFEST(?: V2)? ===(.*?)=== END MANIFEST ===\s*\*/",
        txt, re.DOTALL
    )
    if not match:
        return None
    try:
        manifest = yaml.safe_load(match.group(1))
        return manifest if isinstance(manifest, dict) else None
    except Exception:
        return None

def resolve_and_sync(
    modid: str,
    repo_map: Dict[str, str],
    sm: SourceManager,
    modules_dir: Path,
    seen: Dict[str, Optional[str]],
    stack: list
):
    """
    Recursively resolve dependencies and synchronize modules.
    'seen' records processed modules and their version.
    'stack' tracks the dependency chain for conflict reporting.
    """
    name_only = modid.split("@")[0]
    ref = modid.split("@")[1] if "@" in modid else None

    # Version conflict detection
    if name_only in seen:
        prev_ref = seen[name_only]
        if ref and prev_ref and ref != prev_ref:
            chain = ' -> '.join(stack + [modid])
            err = (
                f"\n[DEPENDENCY CONFLICT]\n"
                f"Module '{name_only}' is requested in multiple versions:\n"
                f"  - Version 1: '{prev_ref}' (chain: { ' -> '.join(stack) or '(root)' })\n"
                f"  - Version 2: '{ref}' (this path: {chain})\n"
                f"Check your modules.yaml and all 'depends' fields. Dependency chain:\n"
                f"  {chain}\n"
                f"Solution: All dependencies of the same module must use the same version.\n"
            )
            raise RuntimeError(err)
        # Upgrade version information if available
        if not prev_ref and ref:
            seen[name_only] = ref
        return
    else:
        seen[name_only] = ref

    # Synchronize source code
    repo = repo_map.get(name_only)
    if not repo:
        print(f"[ERROR] Module {name_only} not found in repo map")
        sys.exit(3)
    sync_module_git(name_only, repo, seen[name_only], modules_dir)

    # Parse MANIFEST for dependencies
    hpp_path = modules_dir / name_only.split("/")[1] / (name_only.split("/")[1] + ".hpp")
    manifest = parse_manifest_from_header(hpp_path)
    if not manifest:
        print(f"[WARN] No MANIFEST found in {hpp_path}")
        return

    depends = manifest.get("depends", [])
    for dep in depends:
        if not dep:
            continue
        resolve_and_sync(dep, repo_map, sm, modules_dir, seen, stack + [modid])

def sync_modules_by_config(config_path, sources_path, modules_dir) -> None:
    """
    Synchronize all modules and their dependencies from a configuration file or URL.
    If the config or sources is a URL, download to local directory first.
    """
    modules_dir = Path(modules_dir)
    modules_dir.mkdir(parents=True, exist_ok=True)

    # Always keep local copies of modules.yaml and sources.yaml in modules_dir
    if is_url(config_path):
        local_config_path = modules_dir / "modules.yaml"
        download_url_to_file(config_path, local_config_path)
        config_path = local_config_path
    else:
        config_path = Path(config_path)
        if not config_path.exists():
            print(f"[WARN] Configuration file not found, creating template: {config_path}")
            config_path.write_text(CONFIG_TEMPLATE, encoding="utf-8")
            print("[INFO] Please edit the configuration file and rerun this script.")
            return

    if is_url(sources_path):
        local_sources_path = modules_dir / "sources.yaml"
        download_url_to_file(sources_path, local_sources_path)
        sources_path = local_sources_path
    else:
        sources_path = Path(sources_path)
        if not sources_path.exists():
            print(f"[ERROR] sources.yaml not found: {sources_path}")
            return

    # Now always load local files
    config_data = load_yaml(config_path)
    module_ids = config_data.get("modules", [])
    if not module_ids:
        print("[ERROR] No modules configured")
        return

    sm = SourceManager(sources_path)
    repo_map = sm.module_map
    seen = {}
    for modid_entry in module_ids:
        resolve_and_sync(modid_entry, repo_map, sm, modules_dir, seen, [])

    print("[SUCCESS] All modules and their dependencies processed.")

def main():
    parser = argparse.ArgumentParser(
        description="XRobot module synchronization tool with MANIFEST-based recursive dependency resolution",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--config", "-c", default=DEFAULT_CONFIG,
                        help="Path or URL to module configuration file (modules.yaml)")
    parser.add_argument("--sources", "-s", default=DEFAULT_SOURCES,
                        help="Path or URL to sources.yaml for module indexes")
    parser.add_argument("--directory", "-d", default="Modules",
                        help="Output directory for module repositories")
    args = parser.parse_args()
    try:
        sync_modules_by_config(args.config, args.sources, args.directory)
    except RuntimeError as e:
        print(str(e))
        sys.exit(4)

if __name__ == "__main__":
    main()
