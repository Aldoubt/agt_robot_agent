"""Repository audit scanner skeleton.

The implementation is intentionally separated from MCP transport.
Future versions can expose this through an MCP tool.
"""

from pathlib import Path
import json
import subprocess


def run_git(path: Path, args):
    return subprocess.check_output(
        ["git", *args],
        cwd=path,
        text=True,
    ).strip()


def scan_repository(path: Path):
    return {
        "path": str(path),
        "remote": run_git(path, ["remote", "-v"]),
        "branch": run_git(path, ["branch", "--show-current"]),
        "commit": run_git(path, ["rev-parse", "HEAD"]),
        "status": run_git(path, ["status", "--short"]),
    }


def save_inventory(items, output):
    Path(output).write_text(
        json.dumps(items, indent=2),
        encoding="utf-8",
    )
