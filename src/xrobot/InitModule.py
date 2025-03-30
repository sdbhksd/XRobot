import argparse
import subprocess
import yaml
import tempfile
import urllib.request
from pathlib import Path

CONFIG_TEMPLATE = """# XRobot module configuration example
modules:
  - name: BlinkLED
    repo: https://github.com/xrobot-org/BlinkLED
    version: master  # optional: branch name or tag
"""

def execute_git_command(cmd: list[str], workdir: Path = None):
    """Execute git commands with error handling."""
    try:
        subprocess.run(cmd, cwd=workdir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Git command failed: {' '.join(cmd)}\n{str(e)}")

def sync_module(name: str, repo: str, version: str, base_dir: Path):
    """Clone or update a module repository."""
    module_path = base_dir / name

    if module_path.exists() and (module_path / ".git").exists():
        print(f"[INFO] Updating module: {name}")
        execute_git_command(["git", "pull"], workdir=module_path)
        if version:
            execute_git_command(["git", "checkout", version], workdir=module_path)
    else:
        print(f"[INFO] Cloning new module: {name}")
        clone_cmd = ["git", "clone", "--recurse-submodules"]
        if version:
            clone_cmd += ["--branch", version]
        clone_cmd += [repo, str(module_path)]
        execute_git_command(clone_cmd)

from urllib.parse import urlparse

def load_configuration(config_path_or_url: str, save_dir: Path) -> list[dict]:
    """Load module configuration from a local file or remote URL, save as modules.yaml in target directory."""
    if config_path_or_url.startswith("http://") or config_path_or_url.startswith("https://"):
        print(f"[INFO] Downloading configuration from URL: {config_path_or_url}")
        try:
            with urllib.request.urlopen(config_path_or_url) as response:
                content = response.read().decode("utf-8")
        except Exception as e:
            print(f"[ERROR] Failed to download config: {e}")
            return []

        save_path = save_dir / "modules.yaml"
        save_path.write_text(content, encoding="utf-8")
        print(f"[INFO] Configuration file saved to: {save_path}")

        config_path = save_path
    else:
        config_path = Path(config_path_or_url)

        if not config_path.exists():
            print(f"[WARN] Configuration file not found, creating template: {config_path}")
            config_path.write_text(CONFIG_TEMPLATE, encoding="utf-8")
            print("[INFO] Please edit the configuration file and rerun this script.")
            return []

    with config_path.open(encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    return config_data.get("modules", [])


def main():
    """Main entry point for module synchronization."""
    parser = argparse.ArgumentParser(
        description="XRobot module synchronization tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--config", "-c", default="modules.yaml",
                        help="Path to module configuration file")
    parser.add_argument("--directory", "-d", default="Modules",
                        help="Output directory for module repositories")

    args = parser.parse_args()
    module_dir = Path(args.directory)
    module_dir.mkdir(parents=True, exist_ok=True)

    modules = load_configuration(args.config, module_dir)
    if not modules:
        return

    for module in modules:
        if not all(key in module for key in ("name", "repo")):
            print(f"[WARN] Skipping invalid module entry: {module}")
            continue
        version = module.get("version", None)
        sync_module(module["name"], module["repo"], version, module_dir)

    print("[SUCCESS] All modules processed")

if __name__ == "__main__":
    main()
