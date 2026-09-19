# AGT Robot Agent

AI Native Robot Engineering Agent based on MCP (Model Context Protocol).

为农业机器人开发工作流提供 AI 助手桥接，让 ChatGPT / Claude / 豆包等 AI 助手能够安全地理解、检查、调试和构建你的 ROS 2 机器人软件栈。

---

## Vision

`agt_robot_agent` 是你机器人开发工作区的 **AI 共享知识库入口**：

```
ChatGPT / Claude / 豆包
          │
       MCP Client
          │
  agt_robot_agent MCP Server
          │
┌─────────────────────────────┐
│  Ubuntu 机器人开发工作站     │
│  ┌───────────────────────┐  │
│  │ ROS 2 Workspace       │  │
│  │ ├── agt_navigation_v3 │  │
│  │ ├── agt-lio-pgo-mapping│ │
│  │ └── ... (40+ repos)   │  │
│  └───────────────────────┘  │
│                             │
│  knowledge-base/            │
│  ├── architecture/         │
│  ├── navigation/           │
│  └── sensors/              │
└─────────────────────────────┘
```

## Core Capabilities

### Phase 1 — MCP Core (当前)
- [x] Workspace inspection — 扫描 ROS 2 工作区结构
- [x] File reading — 安全读取代码和文档
- [x] Code searching — 在代码库中搜索
- [x] Git status — 查看仓库状态和变更
- [x] Safe shell execution — 受控执行 shell 命令
- [x] Repo audit — 工作区审计与迁移建议

### Phase 2 — ROS 2 Integration (规划中)
- [ ] ROS node inspection
- [ ] Topic inspection & echo
- [ ] Parameter query
- [ ] Colcon build
- [ ] Launch management

### Phase 3 — Knowledge Base (本次完善重点)
- [x] Architecture knowledge graph
- [x] Repository catalog
- [x] Cross-repo dependency map
- [x] Doc indexing & search
- [ ] Experiment notes
- [ ] Troubleshooting FAQ

### Phase 4 — Autonomous Workflow (远期)
- [ ] Understand robot architecture
- [ ] Locate problems
- [ ] Modify code safely
- [ ] Compile & test
- [ ] Generate reports

---

## Quick Start

### 安装

```bash
git clone https://github.com/Aldoubt/agt_robot_agent.git
cd agt_robot_agent
pip install -e .
```

### 配置 MCP Client

在你的 MCP Client（如 Claude Desktop、Continue、或豆包）中添加：

```json
{
  "mcpServers": {
    "agt-robot-agent": {
      "command": "agt-robot-agent",
      "args": ["--workspace", "~/ros2_ws"]
    }
  }
}
```

### 运行 Repo Audit

```bash
# 审计你的 ROS 2 工作区
agt-robot-agent audit ~/ros2_ws

# 输出报告
# audit_report/
#   ├── repositories.md
#   ├── environment.md
#   ├── dependency_graph.md
#   └── migration_candidates.md
```

---

## Knowledge Base

知识库模块是你和 AI 助手共享机器人开发知识的核心。

### 目录结构

```
knowledge-base/
├── README.md                    # 知识库索引
├── architecture/                # 系统架构
│   ├── system-overview.md
│   ├── navigation-stack.md
│   └── sensor-pipeline.md
├── navigation/                   # 导航相关知识
├── slam-mapping/                # SLAM 与建图
├── perception/                  # 感知与点云
├── sensors/                     # 传感器与标定
├── robot-base/                   # 底盘与硬件
├── benchmarks/                   # 基准测试
└── dev-notes/                    # 开发笔记
```

### AI 如何使用知识库

AI 助手通过 MCP 工具可以：
1. **列出所有仓库及其职责** — `list_repositories()`
2. **查询特定模块的文档** — `read_doc("navigation/stack-overview.md")`
3. **搜索代码和配置** — `search_code("FastLIO2", language="cpp")`
4. **理解架构关系** — `get_dependency_graph("agt_navigation_v3")`

---

## Safety First

所有工具默认 **read-only** 模式：

- ❌ 不会自动修改源代码
- ❌ 不会自动 git commit/push
- ❌ 不会删除文件
- ✅ 所有写操作需要明确确认
- ✅ 所有命令执行有审计日志

---

## Development

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行 lint
ruff check .
```

## License

MIT
