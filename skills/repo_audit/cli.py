"""Command line entry for repository audit.

Future usage:
    agt-audit ~/ros2_ws

The CLI will remain read-only by default.
"""

import argparse


from pathlib import Path



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


if __name__ == "__main__":
    main()
