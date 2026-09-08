"""Workspace scanner for repo_audit skill.

Read-only discovery of ROS2 workspace repositories.
"""

from pathlib import Path
from .repository_scanner import scan_repository


def find_git_repositories(workspace_path: str):
    root = Path(workspace_path).expanduser().resolve()
    repositories = []

    for git_dir in root.rglob('.git'):
        repo_path = git_dir.parent
        repositories.append(scan_repository(str(repo_path)))

    return repositories


def find_ros_packages(workspace_path: str):
    root = Path(workspace_path).expanduser().resolve()
    packages = []

    for package_xml in root.rglob('package.xml'):
        packages.append(str(package_xml.parent))

    return packages


def scan_workspace(workspace_path: str):
    return {
        'workspace': str(Path(workspace_path).expanduser().resolve()),
        'repositories': find_git_repositories(workspace_path),
        'ros_packages': find_ros_packages(workspace_path),
    }
