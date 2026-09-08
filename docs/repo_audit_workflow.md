# Repo Audit Workflow

## Goal

Provide a safe first step for robot workspace migration and repository governance.

## Workflow

```
ros2_ws
  |
  v
repo_audit skill
  |
  +-- repository scan
  +-- ROS package discovery
  +-- third party modification detection
  |
  v
 audit_report
  |
  v
 architecture review model
  |
  v
 migration plan
```

## Safety Rules

Default mode is read-only.

The audit tool must not:

- modify source files
- change git history
- change remotes
- create commits

## Output

Expected reports:

- repositories.json
- repositories.md
- dirty_changes.md
- third_party_patch.md
- migration_candidates.md
