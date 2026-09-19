"""ROS 2 bag analysis tools.

Wrapper around the rosbag_sensor_trimmer ROS 2 package.
Provides MCP-callable interfaces for bag inspection, verification, and trimming.

Prerequisites:
- rosbag_sensor_trimmer package must be built in the ROS 2 workspace
- Python scripts in rosbag_sensor_trimmer/scripts/ must be accessible

All inspection tools are read-only.
Trimming and conversion tools are WRITE operations (marked as such).
"""

import subprocess
import json
import os
from pathlib import Path
from typing import Any

# ── Configuration ──────────────────────────────────────────────────────────

DEFAULT_WORKSPACE = os.environ.get("AGT_WORKSPACE", str(Path.home() / "ros2_ws"))
BAG_TOOL_TIMEOUT = 60  # seconds for bag operations
INSPECT_TIMEOUT = 30


# ── Helpers ────────────────────────────────────────────────────────────────

def _run_command(cmd: list[str], timeout: int = BAG_TOOL_TIMEOUT) -> dict[str, Any]:
    """Run a shell command safely."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "command": " ".join(cmd),
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "ok": result.returncode == 0,
        }
    except FileNotFoundError as e:
        return {
            "command": " ".join(cmd),
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command not found: {e}",
            "ok": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "command": " ".join(cmd),
            "returncode": -2,
            "stdout": "",
            "stderr": f"Timed out after {timeout}s",
            "ok": False,
        }
    except Exception as e:
        return {
            "command": " ".join(cmd),
            "returncode": -3,
            "stdout": "",
            "stderr": str(e),
            "ok": False,
        }


def _find_bag_dirs(parent_dir: str) -> list[dict[str, Any]]:
    """Find all rosbag2 directories under parent_dir."""
    parent = Path(parent_dir).expanduser().resolve()
    bags = []

    if not parent.exists():
        return bags

    # Look for metadata.yaml which identifies rosbag2 directories
    for meta in parent.rglob("metadata.yaml"):
        bag_dir = meta.parent
        try:
            bags.append({
                "path": str(bag_dir),
                "name": bag_dir.name,
                "size_mb": round(sum(f.stat().st_size for f in bag_dir.rglob("*") if f.is_file()) / 1024 / 1024, 1),
            })
        except Exception:
            continue

    return sorted(bags, key=lambda x: x["name"])


# ── Bag Inspection Tools (read-only) ──────────────────────────────────────

def bag_info(bag_path: str) -> dict[str, Any]:
    """Get detailed info about a rosbag2 directory.

    Uses rosbag_sensor_trimmer CLI --info mode.
    Falls back to ros2 bag info if the custom CLI is not available.
    """
    bag_path = str(Path(bag_path).expanduser().resolve())

    # Try custom trimmer CLI first
    result = _run_command([
        "ros2", "run", "rosbag_sensor_trimmer", "rosbag_sensor_trimmer_cli",
        "--input", bag_path,
        "--info",
    ], timeout=INSPECT_TIMEOUT)

    if result["ok"]:
        result["tool"] = "rosbag_sensor_trimmer_cli"
        return result

    # Fallback to standard ros2 bag info
    result2 = _run_command(["ros2", "bag", "info", bag_path], timeout=INSPECT_TIMEOUT)
    result2["tool"] = "ros2 bag info (fallback)"
    return result2


def bag_list(parent_dir: str) -> dict[str, Any]:
    """List all rosbag2 directories under a parent directory."""
    bags = _find_bag_dirs(parent_dir)
    return {
        "parent_dir": parent_dir,
        "bag_count": len(bags),
        "bags": bags,
    }


def bag_topics(bag_path: str) -> dict[str, Any]:
    """Get topic list and message types from a bag.

    Uses ros2 bag info --verbose for structured output.
    """
    bag_path = str(Path(bag_path).expanduser().resolve())

    result = _run_command(
        ["ros2", "bag", "info", bag_path, "--verbose"],
        timeout=INSPECT_TIMEOUT,
    )

    # Parse topics from verbose output
    topics = []
    if result["ok"]:
        for line in result["stdout"].split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("Files:") and not line.startswith("Duration:"):
                # Try to parse topic: type lines
                parts = line.split(":", 1)
                if len(parts) == 2 and parts[0].strip().startswith("/"):
                    topics.append({
                        "name": parts[0].strip(),
                        "type": parts[1].strip(),
                    })

    result["topics"] = topics
    result["topic_count"] = len(topics)
    return result


# ── Bag Verification (read-only) ──────────────────────────────────────────

def bag_verify(bag_path: str, report_path: str | None = None) -> dict[str, Any]:
    """Verify bag integrity using rosbag_sensor_trimmer.

    Checks:
    - Metadata can be re-opened
    - Topic names and message types
    - Time range and monotonic timestamps
    - LiDAR/IMU coverage
    - Frequency and drop detection
    """
    bag_path = str(Path(bag_path).expanduser().resolve())

    cmd = [
        "ros2", "run", "rosbag_sensor_trimmer", "rosbag_sensor_trimmer_cli",
        "--input", bag_path,
        "--verify-only",
    ]

    if report_path:
        cmd.extend(["--report", report_path])

    result = _run_command(cmd, timeout=BAG_TOOL_TIMEOUT)
    result["mode"] = "verify-only"
    return result


# ── Bag Trimming (WRITE operation, requires confirmation) ────────────────

def bag_trim(
    input_path: str,
    output_path: str,
    start_sec: float | None = None,
    end_sec: float | None = None,
    topics: list[str] | None = None,
    compression: str | None = None,
    verify: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Trim a rosbag by time and/or topics.

    WARNING: This is a WRITE operation that creates new files.
    Original bag is never modified.

    Args:
        input_path: Path to input bag directory
        output_path: Path for trimmed output bag
        start_sec: Start time in seconds relative to bag start
        end_sec: End time in seconds relative to bag start
        topics: List of topics to keep (white list)
        compression: Compression type (zstd) or None
        verify: Whether to verify output after trimming
        dry_run: Only estimate, don't write
    """
    input_path = str(Path(input_path).expanduser().resolve())
    output_path = str(Path(output_path).expanduser().resolve())

    cmd = [
        "ros2", "run", "rosbag_sensor_trimmer", "rosbag_sensor_trimmer_cli",
        "--input", input_path,
        "--output", output_path,
    ]

    if start_sec is not None:
        cmd.extend(["--start", str(start_sec)])
    if end_sec is not None:
        cmd.extend(["--end", str(end_sec)])
    if topics:
        cmd.extend(["--topics", *topics])
    if compression:
        cmd.extend(["--compression", compression])
    if verify:
        cmd.append("--verify")
    if dry_run:
        cmd.append("--dry-run")

    result = _run_command(cmd, timeout=BAG_TOOL_TIMEOUT * 5)  # trimming takes longer
    result["mode"] = "dry-run" if dry_run else "trim"
    result["input"] = input_path
    result["output"] = output_path
    return result


# ── ROS 1 Livox Conversion (WRITE operation) ─────────────────────────────

def bag_convert_ros1_livox(
    input_dir: str,
    output_dir: str,
    duration_sec: float | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Convert ROS 1 Livox split bags to ROS 2 bag.

    Uses the convert_ros1_livox_bag_to_ros2.py script.

    WARNING: This is a WRITE operation.
    """
    input_dir = str(Path(input_dir).expanduser().resolve())
    output_dir = str(Path(output_dir).expanduser().resolve())

    # Find the conversion script
    script_path = _find_convert_script()
    if not script_path:
        return {
            "ok": False,
            "error": "convert_ros1_livox_bag_to_ros2.py not found in workspace",
        }

    cmd = ["python3", script_path, "--input", input_dir, "--output", output_dir]

    if duration_sec is not None:
        cmd.extend(["--duration", str(duration_sec)])
    if dry_run:
        cmd.append("--dry-run")

    result = _run_command(cmd, timeout=BAG_TOOL_TIMEOUT * 10)
    result["mode"] = "ros1-to-ros2-livox"
    return result


def _find_convert_script() -> str | None:
    """Find the ROS 1 to ROS 2 Livox conversion script."""
    # Common locations in ROS 2 workspace
    search_paths = [
        Path(DEFAULT_WORKSPACE) / "src" / "rosbag_sensor_trimmer" / "scripts" / "convert_ros1_livox_bag_to_ros2.py",
        Path.home() / "ros2_ws" / "src" / "rosbag_sensor_trimmer" / "scripts" / "convert_ros1_livox_bag_to_ros2.py",
    ]

    for p in search_paths:
        if p.exists():
            return str(p)

    # Try rglob search
    ws = Path(DEFAULT_WORKSPACE)
    if ws.exists():
        matches = list(ws.rglob("convert_ros1_livox_bag_to_ros2.py"))
        if matches:
            return str(matches[0])

    return None


# ── Tool Definitions ──────────────────────────────────────────────────────

BAG_TOOL_DEFINITIONS = [
    {
        "name": "bag_list",
        "description": "List all rosbag2 directories under a parent folder. Returns bag names, paths, and sizes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "parent_dir": {
                    "type": "string",
                    "description": "Parent directory to search for bags (e.g. /data/rosbags)",
                }
            },
            "required": ["parent_dir"],
        },
    },
    {
        "name": "bag_info",
        "description": "Get detailed info about a rosbag: duration, message count, topics, frequency.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bag_path": {
                    "type": "string",
                    "description": "Path to the rosbag2 directory",
                }
            },
            "required": ["bag_path"],
        },
    },
    {
        "name": "bag_topics",
        "description": "List all topics and message types in a rosbag.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bag_path": {
                    "type": "string",
                    "description": "Path to the rosbag2 directory",
                }
            },
            "required": ["bag_path"],
        },
    },
    {
        "name": "bag_verify",
        "description": "Verify bag integrity: metadata check, time range, frequency, LiDAR/IMU coverage. Read-only.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bag_path": {
                    "type": "string",
                    "description": "Path to the rosbag2 directory",
                },
                "report_path": {
                    "type": "string",
                    "description": "Optional path to save verification report (JSON)",
                }
            },
            "required": ["bag_path"],
        },
    },
    {
        "name": "bag_trim",
        "description": "Trim a rosbag by time range and/or topics. WARNING: This is a WRITE operation that creates new files. Original bag is preserved.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_path": {
                    "type": "string",
                    "description": "Path to input bag directory",
                },
                "output_path": {
                    "type": "string",
                    "description": "Path for trimmed output bag",
                },
                "start_sec": {
                    "type": "number",
                    "description": "Start time in seconds relative to bag start",
                },
                "end_sec": {
                    "type": "number",
                    "description": "End time in seconds relative to bag start",
                },
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Topics to keep (whitelist)",
                },
                "compression": {
                    "type": "string",
                    "description": "Compression type (zstd)",
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Only estimate, don't write output",
                    "default": False,
                },
            },
            "required": ["input_path", "output_path"],
        },
    },
    {
        "name": "bag_convert_ros1",
        "description": "Convert ROS 1 Livox split bags to ROS 2 format. WARNING: This is a WRITE operation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "input_dir": {
                    "type": "string",
                    "description": "Path to ROS 1 split bag directory (contains data_0.bag, data_1.bag, etc.)",
                },
                "output_dir": {
                    "type": "string",
                    "description": "Path for output ROS 2 bag",
                },
                "duration_sec": {
                    "type": "number",
                    "description": "Optional: only convert first N seconds",
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "Scan only, don't convert",
                    "default": False,
                },
            },
            "required": ["input_dir", "output_dir"],
        },
    },
]
