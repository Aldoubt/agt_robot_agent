# agt_robot_agent

AI Native Robot Engineering Agent based on MCP.

## Vision

`agt_robot_agent` provides a safe bridge between web-based AI assistants and Ubuntu robot development environments.

Target users:

- ROS 2 developers
- autonomous robot engineers
- field debugging engineers

The goal is to allow AI assistants to understand, inspect, build, test and debug robot software projects.

## Architecture

```
ChatGPT / Claude / ShunCode
          |
       MCP Client
          |
  agt_robot_agent MCP Server
          |
+----------------------------+
| Ubuntu Robot Development PC |
+----------------------------+
          |
 ROS2 workspace
 Nav2
 FAST-LIO2
 MID360
 RTK
 Robot drivers
```

## Development Roadmap

### Phase 1 - MCP Core

- MCP server bootstrap
- workspace inspection
- file reading
- code searching
- git status
- safe shell execution

### Phase 2 - ROS2 Integration

- ros node inspection
- topic inspection
- parameter query
- colcon build
- launch management

### Phase 3 - Robot Engineering Agent

- rosbag analysis
- TF validation
- sensor diagnostics
- experiment recording

### Phase 4 - Autonomous Engineering Workflow

AI can:

1. understand robot architecture
2. locate problems
3. modify code
4. compile
5. run tests
6. generate reports

## Design Principles

- safety first
- explicit permissions
- reproducible experiments
- Git based workflow
- ROS native

