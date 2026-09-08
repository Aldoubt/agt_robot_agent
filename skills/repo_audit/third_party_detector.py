"""Detect locally modified third-party repositories.

This module is intentionally read-only. It analyzes git metadata and produces
recommendations; it never changes remotes, branches, or files.
"""

from dataclasses import dataclass


@dataclass
class RepositoryClassification:
    path: str
    category: str
    reason: str


def classify_repository(remote: str, status: str) -> RepositoryClassification:
    """Classify a repository based on ownership and local modifications."""
    is_aldbourt_repo = "github.com/Aldoubt" in (remote or "")
    modified = bool(status and status.strip())

    if not is_aldbourt_repo and modified:
        return RepositoryClassification(
            path="",
            category="third_party_modified",
            reason="External repository contains local changes. Consider creating a fork."
        )

    if not is_aldbourt_repo:
        return RepositoryClassification(
            path="",
            category="external_dependency",
            reason="External dependency without detected local modification."
        )

    return RepositoryClassification(
        path="",
        category="self_owned",
        reason="Repository is maintained under Aldoubt namespace."
    )
