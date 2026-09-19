# 农业机器人系统总览

## 硬件栈

- **底盘**: Bunker 履带底盘 / Autolabor C1
- **LiDAR**: Livox MID-360 (非重复扫描)
- **IMU**: 内置 IMU + 可选 RTK/INS
- **相机**: 工业相机（可选）

## 软件栈

```
┌─────────────────────────────────────────┐
│  AI Agent / HMI 层                     │
│  agt_robot_agent · agt_operator_hmi    │
├─────────────────────────────────────────┤
│  导航栈层                               │
│  agt_navigation_v3 · Nav2              │
├─────────────────────────────────────────┤
│  SLAM / 建图层                          │
│  agt-lio-pgo-mapping · FAST-LIO2       │
├─────────────────────────────────────────┤
│  感知层                                 │
│  agt_pointcloud_pipeline · 滤波        │
├─────────────────────────────────────────┤
│  传感器层                               │
│  MID360 驱动 · INS · 标定              │
├─────────────────────────────────────────┤
│  硬件层                                 │
│  Bunker 底盘 · URDF 描述               │
└─────────────────────────────────────────┘
```

## 对应仓库

| 层级 | 主仓库 | 说明 |
|------|--------|------|
| AI Agent | `agt_robot_agent` | MCP Server, AI 桥接 |
| 导航栈 | `agt_navigation_v3` | 当前主力导航 |
| SLAM 建图 | `agt-lio-pgo-mapping` | 离线建图 producer |
| 感知 | `agt_pointcloud_pipeline` | 点云预处理 |
| 传感器 | `agt_ins_driver` / `agt_sensor_calibration` | 驱动与标定 |
| 底盘 | `agt_chassis_description` / `agt_bunker_base` | URDF 与驱动 |

## 技术版本

- ROS 2: Humble
- Python: >= 3.10
- 操作系统: Ubuntu 22.04
- CMake: >= 3.22
