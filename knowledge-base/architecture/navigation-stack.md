# 导航栈架构

## 核心仓库

- **当前版本**: `agt_navigation_v3` (2026-09 活跃开发)
- **上一版本**: `agt_navigation_v2` (2026-08)
- **已归档**: `agt_navigation_stack` (2026-05, 已归档)

## V3 架构

```
MID360 / IMU
  │
  ├─► Batch-LIO ─► agt_batch_lio_adapter
  │                    └─► /agt/odometry/local, odom→base_link
  │
  ├─► mapping_body 全局重定位
  │     ├─ Polar Context 候选检索
  │     ├─ 3D-BBS 粗匹配
  │     └─ small_gicp 精配准
  │                    └─► /agt/relocalization/pose
  │
  └─► agt_localization_manager
        └─► map → odom (唯一发布者)
              │
              ▼
           Nav2
              ├─ SmacPlanner2D
              ├─ Regulated Pure Pursuit
              ├─ velocity smoother
              └─ cmd_vel_guard
                    │
                    ▼
              Bunker 底盘驱动
```

## 关键设计原则

1. **LocalizationManager 是唯一的 map→odom 发布者**
2. **Nav2 使用外部定位，不启动 AMCL**
3. **Map Package 是原子的、版本化的**
4. **建图和导航分离**: 建图由 `agt-lio-pgo-mapping` 负责

## Map Package 结构

```
site_name/v001/
├── navigation/
│   ├── map.yaml
│   └── map.pgm
├── localization/
│   ├── global_map.pcd
│   └── relocalization/
│       ├── polar_context/
│       └── bbs/
└── manifest.yaml
```
