# repo_audit skill

## Purpose

Audit a ROS2 workspace and generate a reproducible software inventory before migration, fork management, or deployment.

This skill is read-only by default.

## Input

Example:

```bash
repo_audit ~/ros2_ws
```

## Output

```text
audit_report/
├── repositories.json
├── repositories.md
├── dirty_changes.md
├── third_party_patch.md
├── migration_candidates.md
└── environment.md
```

## Checks

- repository discovery
- remote URL
- branch
- commit hash
- dirty files
- untracked files
- third-party modification detection
- fork migration candidates
- ROS2 environment information

## Workflow

```text
Workspace
    |
    v
Scanner
    |
    +-- Repository Scanner
    +-- Workspace Scanner
    +-- Third Party Detector
    +-- Environment Checker
    |
    v
Inventory JSON
    |
    v
Report Generator
    |
    v
Architecture Review
```

## Safety

The audit phase must not:

- modify source code
- modify git history
- change remotes
- create commits

Migration actions require an explicit execution workflow.
