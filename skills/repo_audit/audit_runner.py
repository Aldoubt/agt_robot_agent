"""Unified ROS2 robot workspace audit pipeline.

The runner coordinates read-only audit stages.
No repository mutation, commit, push or configuration changes are allowed.
"""

from pathlib import Path
from datetime import datetime
import json

from .audit_context import AuditContext


class AuditRunner:
    def __init__(self, workspace, output="audit_report"):
        self.workspace = Path(workspace).expanduser().resolve()
        self.output = Path(output)

    def run(self):
        self.output.mkdir(parents=True, exist_ok=True)

        context = AuditContext(workspace=str(self.workspace))

        # Stage execution will gradually connect scanners.
        # Keeping a shared context avoids tight coupling between modules.
        stages = [
            "workspace_scan",
            "repository_scan",
            "environment_check",
            "dependency_analysis",
            "migration_analysis",
            "vcs_candidate_generation",
        ]

        manifest = {
            "workspace": context.workspace,
            "generated_at": datetime.utcnow().isoformat(),
            "readonly": context.readonly,
            "stages": stages,
            "context": context.to_dict(),
        }

        (self.output / "audit_manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )

        self._write_summary(manifest)
        return context

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
