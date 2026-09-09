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

        self._run_workspace_stage(context)
        self._run_environment_stage(context)
        self._run_repository_risk_stage(context)
        self._run_dependency_stage(context)

        self._write_manifest(context)
        self._write_summary(context)
        return context

    def _run_workspace_stage(self, context):
        try:
            from .workspace_scanner import scan_workspace
            result = scan_workspace(context.workspace)
            if isinstance(result, dict):
                context.repositories.extend(result.get("repositories", []))
                context.ros_packages.extend(result.get("ros_packages", []))
        except Exception as exc:
            context.risks.append({"stage": "workspace_scan", "error": str(exc)})

    def _run_environment_stage(self, context):
        try:
            from .environment_checker import collect_environment
            context.environment.update(collect_environment())
        except Exception as exc:
            context.risks.append({"stage": "environment_check", "error": str(exc)})

    def _run_repository_risk_stage(self, context):
        try:
            from .third_party_detector import classify_repository
            for repo in context.repositories:
                result = classify_repository(repo.get("remote", ""), repo.get("status", ""))
                context.risks.append({
                    "path": repo.get("path", ""),
                    "category": result.category,
                    "reason": result.reason,
                })
        except Exception as exc:
            context.risks.append({"stage": "repository_risk", "error": str(exc)})

    def _run_dependency_stage(self, context):
        try:
            from .ros_dependency_analyzer import analyze_ros_packages
            context.dependencies = {
                "packages": analyze_ros_packages(context.workspace)
            }
        except Exception as exc:
            context.risks.append({"stage": "dependency_analysis", "error": str(exc)})

    def _write_manifest(self, context):
        manifest = {
            "workspace": context.workspace,
            "generated_at": datetime.utcnow().isoformat(),
            "readonly": context.readonly,
            "context": context.to_dict(),
        }
        (self.output / "audit_manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )

    def _write_summary(self, context):
        (self.output / "audit_summary.md").write_text(
            "# Robot Workspace Audit Summary\n\n"
            f"Workspace: {context.workspace}\n\n"
            "Mode: read-only\n\n"
            f"Repositories found: {len(context.repositories)}\n\n"
            f"ROS packages found: {len(context.ros_packages)}\n\n"
            f"Dependencies analyzed: {len(context.dependencies.get('packages', []))}\n\n"
            f"Risks detected: {len(context.risks)}\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    parser.add_argument("--output", default="audit_report")
    args = parser.parse_args()
    AuditRunner(args.workspace, args.output).run()
