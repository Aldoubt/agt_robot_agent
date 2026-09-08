"""Generate migration recommendations for audited repositories.

This module only produces recommendations. It never modifies repositories.
"""

from pathlib import Path


def classify_repository(repo: dict):
    remote = repo.get("remote", "") or ""
    status = repo.get("status", "") or ""

    result = {
        "path": repo.get("path", ""),
        "remote": remote,
        "status": status,
        "classification": "external_dependency",
        "recommendation": "manage_with_vcs",
    }

    if "Aldoubt" not in remote and status.strip():
        result["classification"] = "third_party_modified"
        result["recommendation"] = "create_fork"

    return result


def generate_migration_candidates(repositories, output_file):
    lines = ["# Migration Candidates", ""]

    for repo in repositories:
        item = classify_repository(repo)
        lines.extend([
            f"## {Path(item['path']).name}",
            f"- Classification: {item['classification']}",
            f"- Recommendation: {item['recommendation']}",
            "",
        ])

    Path(output_file).write_text("\n".join(lines), encoding="utf-8")
