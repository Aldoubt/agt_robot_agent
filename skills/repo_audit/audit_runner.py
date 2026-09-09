"""
Unified audit pipeline runner.

This module orchestrates the read-only repository audit workflow.
The runner should only collect information and generate reports.
It must not modify repositories.
"""

from pathlib import Path
from datetime import datetime


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
        }

        self._write_summary(result)
        return result

    def _write_summary(self, result):
        report = self.output / "audit_summary.md"
        report.write_text(
            "# Robot Workspace Audit Summary\n\n"
            f"Workspace: {result['workspace']}\n\n"
            f"Generated: {result['generated_at']}\n\n"
            "Mode: read-only\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("workspace")
    args = parser.parse_args()

    AuditRunner(args.workspace).run()
