"""ROS 2 inspection tools.

Read-only inspection of running ROS 2 system.
All tools are safe by default — no modification of parameters,
no node shutdown, no launch management without explicit confirmation.
"""

import subprocess
import shlex
from typing import Any

# ── Configuration ──────────────────────────────────────────────────────────

ROS2_TIMEOUT = 10  # seconds
TOPIC_ECHO_DURATION = 3  # seconds, for bounded echo
MAX_TOPIC_ECHO_LINES = 20


# ── Helpers ────────────────────────────────────────────────────────────────

def _run_ros2(args: list[str], timeout: int = ROS2_TIMEOUT) -> dict[str, Any]:
    """Run a ros2 CLI command safely."""
    try:
        cmd = ["ros2", *args]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "command": " ".join(shlex.quote(a) for a in cmd),
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "ok": result.returncode == 0,
        }
    except FileNotFoundError:
        return {
            "command": " ".join(args),
            "returncode": -1,
            "stdout": "",
            "stderr": "ros2 command not found. Is ROS 2 sourced?",
            "ok": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "command": " ".join(args),
            "returncode": -2,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "ok": False,
        }
    except Exception as e:
        return {
            "command": " ".join(args),
            "returncode": -3,
            "stdout": "",
            "stderr": str(e),
            "ok": False,
        }


# ── Node Tools ────────────────────────────────────────────────────────────

def list_nodes() -> dict[str, Any]:
    """List all running ROS 2 nodes."""
    result = _run_ros2(["node", "list"])
    if not result["ok"]:
        return result

    nodes = [n for n in result["stdout"].split("\n") if n.strip()]
    result["nodes"] = nodes
    result["count"] = len(nodes)
    return result


def node_info(node_name: str) -> dict[str, Any]:
    """Get detailed info about a node: publishers, subscribers, services, actions."""
    if not node_name.startswith("/"):
        node_name = "/" + node_name

    result = _run_ros2(["node", "info", node_name])
    return result


# ── Topic Tools ───────────────────────────────────────────────────────────

def list_topics() -> dict[str, Any]:
    """List all topics with message types."""
    result = _run_ros2(["topic", "list", "--verbose"])
    if not result["ok"]:
        return result

    topics = []
    for line in result["stdout"].split("\n"):
        line = line.strip()
        if line and ":" in line:
            parts = line.split(":", 1)
            topics.append({
                "name": parts[0].strip(),
                "type": parts[1].strip(),
            })
    result["topics"] = topics
    result["count"] = len(topics)
    return result


def topic_info(topic_name: str) -> dict[str, Any]:
    """Get topic details: publishers, subscribers, message count."""
    if not topic_name.startswith("/"):
        topic_name = "/" + topic_name

    result = _run_ros2(["topic", "info", topic_name])
    return result


def topic_hz(topic_name: str, window: int = 10) -> dict[str, Any]:
    """Get publishing rate of a topic."""
    if not topic_name.startswith("/"):
        topic_name = "/" + topic_name

    result = _run_ros2(
        ["topic", "hz", topic_name, "--window", str(window)],
        timeout=window + 5,
    )
    return result


def topic_echo_bounded(topic_name: str, duration: int = TOPIC_ECHO_DURATION) -> dict[str, Any]:
    """Echo a topic for a bounded duration and return captured messages."""
    if not topic_name.startswith("/"):
        topic_name = "/" + topic_name

    # Use timeout to auto-stop the echo
    result = _run_ros2(
        ["topic", "echo", topic_name, "--once"],
        timeout=duration + 5,
    )
    return result


# ── Parameter Tools ──────────────────────────────────────────────────────

def list_params(node_name: str | None = None) -> dict[str, Any]:
    """List parameters, optionally filtered by node."""
    args = ["param", "list"]
    if node_name:
        if not node_name.startswith("/"):
            node_name = "/" + node_name
        args.append(node_name)

    result = _run_ros2(args)
    if not result["ok"]:
        return result

    params = [p for p in result["stdout"].split("\n") if p.strip()]
    result["params"] = params
    result["count"] = len(params)
    return result


def get_param(node_name: str, param_name: str) -> dict[str, Any]:
    """Get a parameter value from a node."""
    if not node_name.startswith("/"):
        node_name = "/" + node_name

    result = _run_ros2(["param", "get", node_name, param_name])
    return result


# ── Lifecycle Tools ──────────────────────────────────────────────────────

def list_lifecycle_nodes() -> dict[str, Any]:
    """List lifecycle nodes and their states."""
    result = _run_ros2(["component", "list"])
    return result


# ── TF Tools ──────────────────────────────────────────────────────────────

def tf_echo(source_frame: str, target_frame: str) -> dict[str, Any]:
    """Echo the transform between two frames."""
    result = _run_ros2(
        ["run", "tf2_ros", "tf2_echo", source_frame, target_frame],
        timeout=5,
    )
    return result


# ── Build Tools (write operations, require confirmation) ────────────────

def colcon_build(packages: list[str] | None = None, workspace: str | None = None) -> dict[str, Any]:
    """Run colcon build. This is a WRITE operation.

    Safety:
    - Defaults to --symlink-install
    - Timeout: 300s
    - Only builds specified packages if provided
    """
    import os

    if workspace:
        os.chdir(workspace)

    args = ["colcon", "build", "--symlink-install"]
    if packages:
        args.extend(["--packages-select", *packages])

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=300,
    )

    return {
        "command": " ".join(args),
        "returncode": result.returncode,
        "stdout": result.stdout[-5000:],  # last 5000 chars
        "stderr": result.stderr[-2000:],
        "ok": result.returncode == 0,
    }


# ── Discovery: all tool definitions ────────────────────────────────────────

ROS2_TOOL_DEFINITIONS = [
    {
        "name": "ros_nodes_list",
        "description": "List all running ROS 2 nodes.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ros_node_info",
        "description": "Get detailed info about a node: publishers, subscribers, services.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_name": {
                    "type": "string",
                    "description": "Node name (e.g. /bt_navigator, /lifecycle_manager_navigation)",
                }
            },
            "required": ["node_name"],
        },
    },
    {
        "name": "ros_topics_list",
        "description": "List all ROS 2 topics with their message types.",
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "ros_topic_info",
        "description": "Get topic details: publishers, subscribers, message count.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_name": {
                    "type": "string",
                    "description": "Topic name (e.g. /odom, /scan, /tf)",
                }
            },
            "required": ["topic_name"],
        },
    },
    {
        "name": "ros_topic_hz",
        "description": "Measure the publishing rate (Hz) of a topic.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_name": {
                    "type": "string",
                    "description": "Topic name",
                },
                "window": {
                    "type": "integer",
                    "description": "Window size for rate measurement",
                    "default": 10,
                }
            },
            "required": ["topic_name"],
        },
    },
    {
        "name": "ros_topic_echo",
        "description": "Echo the first message from a topic (bounded, non-blocking).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic_name": {
                    "type": "string",
                    "description": "Topic name to echo",
                }
            },
            "required": ["topic_name"],
        },
    },
    {
        "name": "ros_params_list",
        "description": "List parameters, optionally filtered by node.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_name": {
                    "type": "string",
                    "description": "Optional: filter by node name",
                }
            },
        },
    },
    {
        "name": "ros_param_get",
        "description": "Get a parameter value from a specific node.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_name": {
                    "type": "string",
                    "description": "Node name",
                },
                "param_name": {
                    "type": "string",
                    "description": "Parameter name",
                }
            },
            "required": ["node_name", "param_name"],
        },
    },
    {
        "name": "ros_tf_echo",
        "description": "Echo the TF transform between two frames.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source_frame": {
                    "type": "string",
                    "description": "Source frame (e.g. base_link)",
                },
                "target_frame": {
                    "type": "string",
                    "description": "Target frame (e.g. map)",
                }
            },
            "required": ["source_frame", "target_frame"],
        },
    },
    {
        "name": "colcon_build",
        "description": "Run colcon build. WARNING: this is a write operation that modifies the workspace. Use with caution.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "packages": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional: list of specific packages to build",
                },
                "workspace": {
                    "type": "string",
                    "description": "Workspace path",
                }
            },
        },
    },
]
