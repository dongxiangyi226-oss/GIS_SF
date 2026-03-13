<div align="center">

# 🌍 GIS 算法基础

**Fundamentals of GIS Algorithms**

[![Book](https://img.shields.io/badge/教材-地理信息系统算法基础-blue?style=for-the-badge&logo=bookstack)](.)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](.)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](.)

> 📖 基于《地理信息系统算法基础》（张宏、温永宁、刘爱利 等编著，科学出版社）
> 从零手写 GIS 核心算法，配合笔记 + 代码实现，系统掌握空间分析的底层逻辑。

</div>

---

## ✨ 为什么做这个仓库？

GIS 软件（ArcGIS、QGIS）点几下按钮就能出结果，但**算法黑箱**会让人：
- 🤔 不知道参数该怎么调
- 🐛 出了错不知道是数据问题还是算法问题
- 📉 面试/科研时说不清底层原理

**这个仓库的目标**：把书上每个算法拆开，用 Python 从零实现，做到「知其然，更知其所以然」。

---

## 🗺️ 全书知识图谱

```
                        ┌─────────────────────────────────┐
                        │   🏗️ 第1章 算法设计和分析         │
                        │   复杂性度量 · 最优算法 · 评价     │
                        └───────────────┬─────────────────┘
                                        │
              ┌─────────────────────────┼─────────────────────────┐
              ▼                         ▼                         ▼
   ┌─────────────────┐     ┌─────────────────────┐    ┌──────────────────┐
   │ 📐 计算几何基础   │     │ 🔄 数据变换与转换     │    │ 📦 数据组织与索引  │
   │ Ch.2 DE-9IM     │     │ Ch.3 坐标/投影变换   │    │ Ch.5 压缩/拓扑    │
   │ 点线面关系判断    │     │ Ch.4 矢栅互转        │    │ Ch.7 B树/R树/四叉树│
   └────────┬────────┘     └──────────┬──────────┘    └────────┬─────────┘
            │                         │                         │
            └─────────────────────────┼─────────────────────────┘
                                      ▼
              ┌─────────────────────────────────────────────────┐
              │              🔬 空间分析核心算法                  │
              ├─────────────┬──────────────┬────────────────────┤
              │ 📏 Ch.6     │ 📊 Ch.8      │ 🔺 Ch.9            │
              │ 度量算法     │ 插值算法      │ Delaunay/Voronoi   │
              │ 距离·面积    │ IDW·Kriging  │ 三角网·泰森多边形   │
              ├─────────────┼──────────────┼────────────────────┤
              │ 🛡️ Ch.10    │ 🛣️ Ch.11     │ ⛰️ Ch.12           │
              │ 缓冲区分析   │ 网络分析      │ 地形分析            │
              │ 点线面缓冲   │ 最短路径·MST  │ DEM·坡度·通视      │
              └─────────────┴──────────────┴────────────────────┘
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
   ┌──────────────────────┐                    ┌──────────────────────┐
   │ ⛏️ Ch.13 数据挖掘     │                    │ 🎨 Ch.14 数据输出     │
   │ 分类·聚类·PCA·回归    │                    │ 地图符号绘制           │
   └──────────────────────┘                    └──────────────────────┘
```

---

## 📚 章节导航

| 章节 | 主题 | 核心算法 | 笔记 | 代码 |
|:---:|------|--------|:----:|:----:|
| 01 | 🏗️ 算法设计和分析 | 复杂性度量、平摊分析 | [📝](notes/) | - |
| 02 | 📐 计算几何基础 | DE-9IM、射线法、转角法、线段求交 | [📝](notes/) | [💻](code/ch02_computational_geometry/) |
| 03 | 🔄 空间数据变换 | 仿射变换、高斯-克吕格投影 | [📝](notes/) | [💻](code/ch03_coordinate_transform/) |
| 04 | 🔀 空间数据转换 | 矢量栅格化、栅格矢量化 | [📝](notes/) | [💻](code/ch04_data_conversion/) |
| 05 | 📦 空间数据组织 | Douglas-Peucker、游程编码、拓扑生成 | [📝](notes/) | [💻](code/ch05_data_organization/) |
| 06 | 📏 空间度量 | 点线距离、多边形面积 | [📝](notes/) | [💻](code/ch06_spatial_measurement/) |
| 07 | 🗂️ 空间索引 | B⁺树、R树/R*树、四叉树、Hilbert曲线 | [📝](notes/) | [💻](code/ch07_spatial_indexing/) |
| 08 | 📊 空间插值 | IDW、Kriging、薄板样条、趋势面 | [📝](notes/) | [💻](code/ch08_interpolation/) |
| 09 | 🔺 Delaunay & Voronoi | 增量构造、分治法、平面扫描 | [📝](notes/) | [💻](code/ch09_delaunay_voronoi/) |
| 10 | 🛡️ 缓冲区分析 | 点/线/面缓冲、多目标合并 | [📝](notes/) | [💻](code/ch10_buffer_analysis/) |
| 11 | 🛣️ 网络分析 | Dijkstra、Prim、Kruskal、资源分配 | [📝](notes/) | [💻](code/ch11_network_analysis/) |
| 12 | ⛰️ 地形分析 | DEM生成、坡度坡向、山脊谷线、通视域 | [📝](notes/) | [💻](code/ch12_terrain_analysis/) |
| 13 | ⛏️ 数据挖掘 | 决策树、聚类、PCA、关联规则 | [📝](notes/) | [💻](code/ch13_data_mining/) |
| 14 | 🎨 数据输出 | SVG符号模型、点/线/面符号绘制 | [📝](notes/) | [💻](code/ch14_cartographic_output/) |

---

## 📁 仓库结构

```
GIS_SF/
│
├── 📄 README.md                        # 你正在看的这个文件
├── 📕 地理信息系统算法基础.pdf            # 教材原书 (本地, 未上传)
│
├── 📝 notes/                           # 各章学习笔记 (Markdown)
│   ├── ch01_算法设计和分析.md
│   ├── ch02_计算几何基础.md
│   └── ...
│
└── 💻 code/                            # 算法实现 (Python)
    ├── ch02_computational_geometry/     # 计算几何
    ├── ch03_coordinate_transform/      # 坐标变换
    ├── ch04_data_conversion/           # 矢栅转换
    ├── ch05_data_organization/         # 数据压缩 & 拓扑
    ├── ch06_spatial_measurement/       # 空间度量
    ├── ch07_spatial_indexing/          # 空间索引
    ├── ch08_interpolation/            # 空间插值
    ├── ch09_delaunay_voronoi/         # Delaunay & Voronoi
    ├── ch10_buffer_analysis/          # 缓冲区分析
    ├── ch11_network_analysis/         # 网络分析
    ├── ch12_terrain_analysis/         # 地形分析
    ├── ch13_data_mining/              # 空间数据挖掘
    └── ch14_cartographic_output/      # 地图符号输出
```

---

## 🚀 学习进度

> 🔲 未开始 &nbsp; 🟡 进行中 &nbsp; ✅ 已完成

| 状态 | 章节 | 备注 |
|:---:|------|------|
| 🔲 | Ch.01 算法设计和分析 | |
| 🔲 | Ch.02 计算几何基础 | |
| 🔲 | Ch.03 空间数据变换 | |
| 🔲 | Ch.04 空间数据转换 | |
| 🔲 | Ch.05 空间数据组织 | |
| 🔲 | Ch.06 空间度量 | |
| 🔲 | Ch.07 空间索引 | |
| 🔲 | Ch.08 空间插值 | |
| 🔲 | Ch.09 Delaunay & Voronoi | |
| 🔲 | Ch.10 缓冲区分析 | |
| 🔲 | Ch.11 网络分析 | |
| 🔲 | Ch.12 地形分析 | |
| 🔲 | Ch.13 数据挖掘 | |
| 🔲 | Ch.14 数据输出 | |

---

## 🛠️ 技术栈

| 工具 | 用途 |
|------|------|
| 🐍 Python 3.x | 算法实现主语言 |
| 📐 NumPy / SciPy | 数值计算 |
| 📊 Matplotlib | 算法可视化 |
| 🗺️ Shapely / GDAL | GIS 数据处理 (对照验证) |

---

<div align="center">

**⭐ 如果觉得有帮助，欢迎 Star！⭐**

</div>
