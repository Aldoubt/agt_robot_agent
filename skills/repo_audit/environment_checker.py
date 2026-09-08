"""Environment information collector for repo_audit.

Read-only ROS2 development environment inspection.
"""

from pathlib import Path
import platform
import shutil
import subprocess


def _run_command(command):
    try:
        return subprocess.check_output(
            command,
            stderr=subprocess.STDOUT,
            text=True,
        ).strip()
    except Exception:
        return ""


def collect_environment():
    return {
        "system": {
            "os": platform.platform(),
            "python": platform.python_version(),
        },
        "ros": {
            "distro": _run_command(["bash", "-lc", "echo $ROS_DISTRO"]),
        },
        "tools": {
            "git": shutil.which("git") or "",
            "colcon": shutil.which("colcon") or "",
        },
    }
