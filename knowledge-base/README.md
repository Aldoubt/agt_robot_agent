# AGT Robot Knowledge Base

> 农业机器人开发知识库 — 供 AI 助手（ChatGPT / Claude / 豆包）和人类工程师共享。

## 目录索引

| 分类 | 文档 | 说明 |
|------|------|------|
| **Architecture** | [system-overview](architecture/system-overview.md) | 整体系统架构 |
| | [navigation-stack](architecture/navigation-stack.md) | 导航栈架构 |
| | [sensor-pipeline](architecture/sensor-pipeline.md) | 传感器数据流 |
| **Navigation** | [navigation-v3](navigation/navigation-v3.md) | 导航 v3 详细说明 |
| | [localization](navigation/localization.md) | 定位方案 |
| | [map-package](navigation/map-package.md) | 地图包规范 |
| **SLAM & Mapping** | [lio-pgo-mapping](slam-mapping/lio-pgo-mapping.md) | LIO + PGO 建图 |
| | [fastlivo2-platform](slam-mapping/fastlivo2-platform.md) | FAST-LIVO2 平台 |
| **Perception** | [pointcloud-pipeline](perception/pointcloud-pipeline.md) | 点云处理流水线 |
| | [ground-segmentation](perception/ground-segmentation.md) | 地面分割 |
| **Sensors** | [sensor-calibration](sensors/sensor-calibration.md) | 传感器标定 |
| | [mid360-setup](sensors/mid360-setup.md) | MID360 配置 |
| **Robot Base** | [chassis-description](robot-base/chassis-description.md) | 底盘 URDF |
| | [bunker-driver](robot-base/bunker-driver.md) | Bunker 底盘驱动 |
| **Benchmarks** | [lio-benchmark](benchmarks/lio-benchmark.md) | LIO 基准测试 |
| | [map-benchmark](benchmarks/map-benchmark.md) | 地图质量基准 |
| **Dev Notes** | [troubleshooting](dev-notes/troubleshooting.md) | 常见问题排查 |
| | [experiment-notes](dev-notes/experiment-notes.md) | 实验记录 |

## AI 使用指南

### 给 GPT / Claude

在 Custom GPT 或 Claude 项目中：
1. 上传整个 `knowledge-base/` 目录
2. 或配置 GitHub 插件指向此仓库
3. 提示词模板：
   > "你是农业机器人开发助手。请参考知识库中的文档回答问题。如果知识库中没有相关信息，请明确说明。"

### 给豆包

通过 `agt_robot_agent` MCP Server：
1. 启动 MCP Server 连接到你的机器人工作站
2. 使用 `knowledge_base_list` 工具列出所有文档
3. 使用 `read_file` 工具读取具体文档内容

## 维护规则

- 每份文档对应一个或多个代码仓库
- 文档变更需要在对应代码仓库的 PR 中同步更新
- 重要决策记录在 `dev-notes/decisions/` 目录下（ADR 格式）
- 实验结果必须记录数据来源和复现步骤
