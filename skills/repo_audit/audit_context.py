"""Shared context model for the repository audit pipeline.

The context object is used to pass collected information between audit stages.
All stages should keep data collection read-only.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AuditContext:
    workspace: str
    readonly: bool = True
    repositories: List[Dict[str, Any]] = field(default_factory=list)
    ros_packages: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    risks: List[Dict[str, Any]] = field(default_factory=list)
    migration_candidates: List[Dict[str, Any]] = field(default_factory=list)
    vcs_candidates: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self):
        return {
            "workspace": self.workspace,
            "readonly": self.readonly,
            "repositories": self.repositories,
            "ros_packages": self.ros_packages,
            "dependencies": self.dependencies,
            "environment": self.environment,
            "risks": self.risks,
            "migration_candidates": self.migration_candidates,
            "vcs_candidates": self.vcs_candidates,
        }
