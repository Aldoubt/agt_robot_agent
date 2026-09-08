"""Command line entry for repository audit.

Usage:
    python skills/repo_audit/cli.py ~/ros2_ws

The CLI remains read-only by default.
"""

import argparse
from pathlib import Path

from .workspace_scanner import scan_workspace
from .report_generator import generate_markdown_report


def main():
    parser = argparse.ArgumentParser(description="Audit ROS2 robot workspace")
    parser.add_argument("workspace", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit_report"),
    )
    args = parser.parse_args()

    print(f"Audit workspace: {args.workspace}")
    print(f"Output directory: {args.output}")
    print("Read-only audit mode")

    inventory = scan_workspace(str(args.workspace))

    generate_markdown_report(inventory, str(args.output))

    # Reserved for migration/vcs/environment reports.
    # The first phase keeps report generation independent and safe.

    print("Audit completed")
    print(f"Report generated: {args.output}")


if __name__ == "__main__":
    main()
