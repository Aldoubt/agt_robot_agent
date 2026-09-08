# repo_audit skill

## Purpose

Audit ROS2 workspace repositories before migration or deployment.

## Input

A workspace path, for example:

```
~/ros2_ws
```

## Output

Generate:

```
audit_report/
├── repositories.json
├── repositories.md
├── dirty_changes.md
├── third_party_patch.md
└── migration_candidates.md
```

## Checks

- repository list
- remote URL
- branch
- commit hash
- uncommitted changes
- untracked files
- third party modification detection

## Safety

The audit phase is read-only by default.
