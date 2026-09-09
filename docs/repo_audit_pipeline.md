# Repo Audit Pipeline

## Goal

Build a read-only audit pipeline for ROS2 robot software workspaces.

## Pipeline

```
ros2_ws
  |
  v
workspace scanner
  |
  +-- git repository scanner
  +-- ROS package analyzer
  +-- environment checker
  +-- dirty change detector
  +-- remote divergence detector
  |
  v
inventory data
  |
  v
report generator
  |
  +-- repositories.md
  +-- environment.md
  +-- dependency_graph.md
  +-- migration_candidates.md
  +-- robot_candidate.repos
```

## Safety Rules

- Audit mode is read-only.
- No automatic commit.
- No remote modification.
- No deletion.

## Future Integration

The generated reports are consumed by a higher-level architecture review agent to decide:

- fork strategy
- repository ownership
- vcs manifest generation
- migration order
