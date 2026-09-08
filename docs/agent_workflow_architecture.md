# Agent Workflow Architecture

## Goal

Transform `agt_robot_agent` from an MCP bridge into a robot engineering workflow agent.

## Agent Roles

```
User
 |
 v
Planner / Router
 |
 +----------------+
 |                |
 v                v
Audit Agent    Execution Agent
 |
 v
Architecture Review Agent
```

## Model Routing Principle

### Low cost models

Used for:

- file inventory
- git status collection
- report formatting
- repetitive inspection

### Medium models

Used for:

- code modification
- build fixing
- script generation

### High reasoning models

Used for:

- architecture decisions
- migration strategy
- dependency management

## First Workflow

Repository audit:

1. scan workspace
2. collect git metadata
3. classify repositories
4. generate migration proposal
5. human approval
6. execute changes
