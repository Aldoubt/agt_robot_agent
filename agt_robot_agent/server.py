"""AGT Robot Agent - MCP Server

A safe bridge between AI assistants and ROS 2 robot development workspaces.
Provides read-only tools for inspecting, searching, and understanding robot software.

All tools default to read-only mode. Write operations require explicit confirmation.
"""

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ── Configuration ──────────────────────────────────────────────────────────

DEFAULT_WORKSPACE = os.environ.get("AGT_WORKSPACE", str(Path.home() / "ros2_ws"))
SAFE_SHELL_TIMEOUT = 30  # seconds
MAX_FILE_SIZE = 1024 * 1024  # 1 MB
MAX_SEARCH_RESULTS = 50

# ── Helpers ────────────────────────────────────────────────────────────────

def _resolve_workspace(path: str | None = None) -> Path:
    base = Path(path or DEFAULT_WORKSPACE).expanduser().resolve()
    return base


def _is_safe_path(path: Path, workspace: Path) -> bool:
    """Ensure path stays within workspace."""
    try:
        path.resolve().relative_to(workspace.resolve())
        return True
    except ValueError:
        return False


def _run_git(repo_path: Path, args: list[str]) -> str:
    """Run git command safely in a repo."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"git error: {e}"


def _find_git_repos(workspace: Path) -> list[dict[str, Any]]:
    """Find all git repositories in workspace."""
    repos = []
    for git_dir in workspace.rglob(".git"):
        repo_path = git_dir.parent
        if not _is_safe_path(repo_path, workspace):
            continue

        remote = _run_git(repo_path, ["remote", "-v"])
        branch = _run_git(repo_path, ["branch", "--show-current"])
        commit = _run_git(repo_path, ["rev-parse", "--short", "HEAD"])
        status = _run_git(repo_path, ["status", "--short"])

        repos.append({
            "path": str(repo_path.relative_to(workspace)),
            "remote": remote.split("\n")[0] if remote else "",
            "branch": branch,
            "commit": commit,
            "dirty": bool(status),
            "dirty_files": status.split("\n") if status else [],
        })
    return sorted(repos, key=lambda x: x["path"])


# ── MCP Server ────────────────────────────────────────────────────────────

server = Server("agt-robot-agent")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="workspace_inspect",
            description="Inspect the ROS 2 workspace structure. Returns list of packages, repos, and basic stats.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Path to ROS 2 workspace (default: ~/ros2_ws)",
                    }
                },
            },
        ),
        Tool(
            name="list_repositories",
            description="List all git repositories in the workspace with their status, branch, and dirty state.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace": {
                        "type": "string",
                        "description": "Path to ROS 2 workspace",
                    }
                },
            },
        ),
        Tool(
            name="read_file",
            description="Read a file from the workspace safely. Returns file contents or error if file is too large or outside workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from workspace root",
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Path to ROS 2 workspace",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="search_code",
            description="Search for a pattern in code files within the workspace.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern (regex)",
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Path to ROS 2 workspace",
                    },
                    "file_glob": {
                        "type": "string",
                        "description": "File pattern to search (e.g. *.py, *.cpp)",
                        "default": "*",
                    },
                },
                "required": ["pattern"],
            },
        ),
        Tool(
            name="git_status",
            description="Get detailed git status for a specific repository.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {
                        "type": "string",
                        "description": "Relative path of repository from workspace root",
                    },
                    "workspace": {
                        "type": "string",
                        "description": "Path to ROS 2 workspace",
                    },
                },
                "required": ["repo_path"],
            },
        ),
        Tool(
            name="knowledge_base_list",
            description="List all documents in the robot knowledge base.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category (navigation, slam, sensors, etc.)",
                    }
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    workspace = _resolve_workspace(arguments.get("workspace"))

    if name == "workspace_inspect":
        ros_packages = []
        for pkg_xml in workspace.rglob("package.xml"):
            ros_packages.append(str(pkg_xml.parent.relative_to(workspace)))

        repos = _find_git_repos(workspace)
        dirty_repos = [r for r in repos if r["dirty"]]

        result = {
            "workspace": str(workspace),
            "ros_packages": len(ros_packages),
            "repositories": len(repos),
            "dirty_repositories": len(dirty_repos),
            "package_paths": ros_packages[:20],
        }
        return [TextContent(type="text", text=str(result))]

    elif name == "list_repositories":
        repos = _find_git_repos(workspace)
        return [TextContent(type="text", text=str(repos))]

    elif name == "read_file":
        rel_path = arguments["path"]
        file_path = workspace / rel_path

        if not _is_safe_path(file_path, workspace):
            return [TextContent(type="text", text=f"Error: Path outside workspace: {rel_path}")]

        if not file_path.exists():
            return [TextContent(type="text", text=f"Error: File not found: {rel_path}")]

        if file_path.stat().st_size > MAX_FILE_SIZE:
            return [TextContent(type="text", text=f"Error: File too large ({file_path.stat().st_size} bytes)")]

        content = file_path.read_text(encoding="utf-8", errors="replace")
        return [TextContent(type="text", text=content)]

    elif name == "search_code":
        pattern = arguments["pattern"]
        file_glob = arguments.get("file_glob", "*")
        results = []

        for file_path in workspace.rglob(file_glob):
            if not file_path.is_file():
                continue
            if not _is_safe_path(file_path, workspace):
                continue
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                for i, line in enumerate(content.split("\n"), 1):
                    if pattern.lower() in line.lower():
                        rel = file_path.relative_to(workspace)
                        results.append(f"{rel}:{i}: {line.strip()[:100]}")
                        if len(results) >= MAX_SEARCH_RESULTS:
                            break
                if len(results) >= MAX_SEARCH_RESULTS:
                    break
            except Exception:
                continue

        return [TextContent(type="text", text=f"Found {len(results)} matches:\n" + "\n".join(results))]

    elif name == "git_status":
        repo_rel = arguments["repo_path"]
        repo_path = workspace / repo_rel

        if not _is_safe_path(repo_path, workspace):
            return [TextContent(type="text", text=f"Error: Path outside workspace: {repo_rel}")]

        remote = _run_git(repo_path, ["remote", "-v"])
        branch = _run_git(repo_path, ["branch", "--show-current"])
        commit = _run_git(repo_path, ["log", "-1", "--format=%h %s (%ar)"])
        status = _run_git(repo_path, ["status", "--short"])
        ahead_behind = _run_git(repo_path, ["rev-list", "--left-right", "--count", "HEAD...@{u}"])

        result = {
            "path": repo_rel,
            "remote": remote,
            "branch": branch,
            "last_commit": commit,
            "status": status,
            "ahead_behind": ahead_behind,
        }
        return [TextContent(type="text", text=str(result))]

    elif name == "knowledge_base_list":
        kb_dir = workspace / "knowledge-base"
        category = arguments.get("category")

        if not kb_dir.exists():
            return [TextContent(type="text", text="Knowledge base directory not found at: " + str(kb_dir))]

        docs = []
        search_dir = kb_dir / category if category else kb_dir

        for md_file in search_dir.rglob("*.md"):
            rel = md_file.relative_to(kb_dir)
            docs.append(str(rel))

        return [TextContent(type="text", text=f"Found {len(docs)} docs:\n" + "\n".join(sorted(docs)))]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


# ── CLI Entry ─────────────────────────────────────────────────────────────

def main():
    import sys

    # CLI mode: audit workspace
    if len(sys.argv) > 1 and sys.argv[1] == "audit":
        workspace = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_WORKSPACE
        print(f"AGT Robot Agent - Repo Audit")
        print(f"Workspace: {workspace}")
        print(f"Mode: read-only")
        print()

        from skills.repo_audit.cli import main as audit_main
        sys.argv = ["repo_audit", workspace]
        audit_main()
        return

    # MCP server mode
    print("Starting agt-robot-agent MCP server...", file=sys.stderr)
    print(f"Workspace: {DEFAULT_WORKSPACE}", file=sys.stderr)

    asyncio.run(_run_server())


async def _run_server():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    main()
