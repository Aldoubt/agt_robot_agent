"""
Unified ROS2 robot workspace audit pipeline.

The runner coordinates read-only audit stages.
No repository mutation, commit, push or configuration changes are allowed.
"""

from pathlib import Path
from datetime import datetime
import json


class AuditRunner:
    def __init__(self, workspace, output="audit_report"):
        self.workspace = Path(workspace).expanduser().resolve()
        self.output = Path(output)

    def run(self):
        self.output.mkdir(parents=True, exist_ok=True)

        result = {
            "workspace": str(self.workspace),
            "generated_at": datetime.utcnow().isoformat(),
            "readonly": True,
            "stages": [],
        }

        # Pipeline stages are intentionally isolated.
        # Individual scanners can be enabled without changing the runner API.
        stages = [
            "workspace_scan",
            "repository_scan",
            "environment_check",
            "dependency_analysis",
            "migration_analysis",
            "vcs_candidate_generation",
        ]

        result["stages"] = stages

        (self.output / "audit_manifest.json").write_text(
            json.dumps(result, indent=2),
            encoding="utf-8",
        )

        self._write_summary(result)
        return result

    def _write_summary(self, result):
        report = self.output / "audit_summary.md"
        report.write_text(
            "# Robot Workspace Audit Summary\n\n"
            f"Workspace: {result['workspace']}\n\n"
            f"Generated: {result['generated_at']}\n\n"
            "Mode: read-only\n\n"
            "Stages:\n"
            + "\n".join(f"- {s}" for s in result["stages"]),
            encoding="utf-8",
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    parser.add_argument("--output", default="audit_report")
    args = parser.parse_args()

    AuditRunner(args.workspace, args.output).run()
