# Navigation V3 详细说明

## 仓库

- `agt_navigation_v3` — 当前主力导航栈

## 里程碑

- **v0.3.0**: 定位合同冻结 (当前)
- **下一阶段**: P3 运行时验收、Nav2 现场验证

## 核心组件

| 组件 | 职责 |
|------|------|
| `agt_batch_lio_adapter` | Batch-LIO 局部里程计适配器 |
| `agt_localization_manager` | 全局定位管理，唯一 map→odom 发布者 |
| `agt_global_relocalization` | 3D 全局重定位 (Polar Context + BBS + GICP) |
| `agt_map_manager` | Map Package 创建、校验、版本管理 |
| `agt_operator_console` | 操作员控制台 |
| Nav2 | 路径规划 + 运动控制 |

## 启动流程

### 现场启动

1. 启动传感器会话: `sensor_session.launch.py`
2. 选择 Map Package: `select_map_package`
3. 校验地图: `validate_active_map`
4. 启动 RViz 导航: `rviz_field_demo.launch.py`

### 离线回放

1. 使用 `acceptance_offline_replay.launch.py`
2. 传入 bag + map + relocalization assets
3. 验证: LIO 输出 → 重定位成功 → Nav2 加载

## 文档导航

| 需求 | 文档 |
|------|------|
| 当前里程碑 | `docs/CODEX_CONTEXT.md` |
| 文档权威矩阵 | `docs/AUTHORITY_MATRIX.md` |
| TF 合同 | `docs/contracts/TF_CONVENTION.md` |
| P3 验收 | `docs/acceptance/P3_RUNTIME_ACCEPTANCE_AUDIT.md` |
