# LIO + PGO 建图流程

## 仓库

- `agt-lio-pgo-mapping` — 建图 Producer

## 流程

```
MID-360 CustomMsg + IMU
          │
          ▼
    MID360 Adapter
    (校验扫描 + 时间对齐)
          │
          ▼
    FAST-LIO2 Frontend
          │
          ▼
    Keyframes 提取
          │
          ▼
    PGO 位姿图优化
    (GTSAM / Ceres)
          │
          ▼
    Optimized PCD Map
    + poses.txt
          │
          ▼
    Map Package 导出
    (含校验和 + 元数据)
```

## 输入

- MID-360 rosbag (含 CustomMsg + IMU)
- 相机内参 / 外参 (可选)

## 输出

```
map_package/
├── map.pcd              # 优化后的点云地图
├── poses.txt            # 关键帧位姿
├── poses_timed.txt      # 带时间戳的位姿
├── patches/              # 局部地图补丁
├── calibration.yaml      # 标定参数
├── metadata.yaml        # 元数据 (backend, optimized)
├── manifest.yaml        # 清单
└── checksums.sha256     # 校验和
```

## 验收标准

- `metadata.yaml` 中 `backend: PGO`
- `optimized: true`
- 校验脚本通过
- 导出的地图可直接用于导航 v3

## 依赖

- FAST-LIO2 (锁定版本)
- GTSAM / Ceres (PGO)
- Livox SDK2
- ROS 2 Humble
