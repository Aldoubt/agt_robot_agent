"""Generate a vcs.repos candidate from repository inventory.

The generated file is a proposal only and requires human review.
"""

from pathlib import Path


def generate_vcs_candidate(repositories, output_file):
    lines = ["repositories:", ""]

    for repo in repositories:
        remote = repo.get("remote", "")
        name = Path(repo.get("path", "repo")).name

        if not remote:
            continue

        lines.extend([
            f"  {name}:",
            "    type: git",
            f"    url: {remote}",
            f"    version: {repo.get('branch', 'main')}",
            "",
        ])

    Path(output_file).write_text("\n".join(lines), encoding="utf-8")
