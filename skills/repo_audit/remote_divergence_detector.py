"""Detect local commits that are not synchronized with remote branches."""

import subprocess


def run_git(path: str, args):
    result = subprocess.run(
        ["git", "-C", path] + args,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def detect_divergence(repo_path: str):
    """Return local/remote branch divergence information."""
    branch = run_git(repo_path, ["branch", "--show-current"])
    if not branch:
        return {"branch": "", "ahead": 0, "behind": 0}

    result = run_git(
        repo_path,
        ["rev-list", "--left-right", "--count", f"origin/{branch}...HEAD"],
    )

    if not result:
        return {"branch": branch, "ahead": None, "behind": None}

    behind, ahead = result.split()
    return {
        "branch": branch,
        "ahead": int(ahead),
        "behind": int(behind),
    }
