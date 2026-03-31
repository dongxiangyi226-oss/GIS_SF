# 📐 Douglas-Peucker 矢量数据压缩 —— 完整 GUI 教学文档

> **对应章节**：第5章 §5.1.3 道格拉斯-普克法
> **核心算法**：递归分治 + 点到线段垂距
> **技术栈**：Python 3.x + Tkinter + Matplotlib
> **前置知识**：第2章 §2.3 向量叉积（已在「折线段拐向判断」中学过）

---

## 📖 目录

1. [数学原理](#1-数学原理)
2. [项目结构（三文件分离）](#2-项目结构三文件分离)
3. [文件A: algorithm.py — 纯算法](#3-文件a-algorithmpy--纯算法)
   - [A-1: 点到线段的垂直距离](#a-1-点到线段的垂直距离)
   - [A-2: Douglas-Peucker 递归](#a-2-douglas-peucker-递归)
4. [文件B: gui.py — 绘图界面](#4-文件b-guipy--绘图界面)
   - [B-1: 导入依赖](#b-1-导入依赖)
   - [B-2: 主窗口初始化](#b-2-主窗口初始化)
   - [B-3: 工具栏搭建（含 ε 滑块）](#b-3-工具栏搭建含-ε-滑块)
   - [B-4: Matplotlib 画布嵌入](#b-4-matplotlib-画布嵌入)
   - [B-5: 右侧结果面板](#b-5-右侧结果面板)
   - [B-6: 底部状态栏](#b-6-底部状态栏)
   - [B-7: 鼠标事件绑定](#b-7-鼠标事件绑定)
   - [B-8: 采点 / 撤销 / 拖动](#b-8-采点--撤销--拖动)
   - [B-9: 画布重绘](#b-9-画布重绘)
   - [B-10: 压缩执行 + 结果面板写入](#b-10-压缩执行--结果面板写入)
   - [B-11: ε 滑块联动](#b-11-ε-滑块联动)
   - [B-12: 连线 / 清空 / 导入 / 导出](#b-12-连线--清空--导入--导出)
5. [文件C: main.py — 启动入口](#5-文件c-mainpy--启动入口)
6. [坐标文件格式](#6-坐标文件格式)
7. [手算验证练习](#7-手算验证练习)
8. [思考题](#8-思考题)

---

## 1. 数学原理

### 1.1 问题定义

一条折线有 n 个点，许多点"几乎在一条直线上"，可以去掉而不明显改变折线形状。
给定一个**容差 ε**（允许的最大偏移），用尽可能少的点近似原始折线。

### 1.2 算法思路：递归分治

```
原始折线:  P0 ─ P1 ─ P2 ─ P3 ─ P4 ─ P5 ─ P6

步骤1: 连首尾 P0────────────────────P6

步骤2: 算每个中间点到首尾连线的垂距
       P0────────────────────P6
            P1↕d1  P2↕d2  ...

步骤3: 找到最远的点 P3, d_max = d3

步骤4: d_max > ε ?
       ├── 是 → 保留P3, 分两半递归:
       │        DP(P0..P3, ε)  和  DP(P3..P6, ε)
       │
       └── 否 → 中间点全部丢弃, 只保留 P0 和 P6
```

### 1.3 点到线段的垂直距离

这是整个算法的**基础计算单元**，用叉积推导：

```
线段端点:  A(x1, y1),  B(x2, y2)
待测点:    P(px, py)

向量 AB = (x2-x1, y2-y1)
向量 AP = (px-x1, py-y1)

叉积 cross = AB × AP = (x2-x1)(py-y1) - (y2-y1)(px-x1)

                |cross|           叉积的绝对值
垂距 d = ──────────────── = ──────────────────────
              |AB|           线段AB的长度
```

**几何含义**：叉积 = 以 AB 和 AP 为两边的平行四边形面积，除以底边 AB 长度就是高（垂距）。

### 1.4 特殊情况：首尾重合

当 A 和 B 是同一个点时（`|AB| = 0`），退化为**点到点的距离**：

```
d = |AP| = sqrt( (px-x1)² + (py-y1)² )
```

### 1.5 递归终止条件

```
如果输入折线只有 2 个点（首和尾），无法再分割，直接返回 [首点]。
最外层调用结束后，手动补上末尾点。
```

### 1.6 时间复杂度

| 情况 | 复杂度 | 说明 |
|------|--------|------|
| 最好 | O(n log n) | 每次从中间分割 |
| 最坏 | O(n²) | 每次在端点附近分割（退化） |
| 平均 | O(n log n) | 实际数据通常接近最好情况 |

---

## 2. 项目结构（三文件分离）

```
Douglas_Peucker/
├── 教学文档_Douglas_Peucker.md    ← 你正在看的文件
│
├── algorithm.py                  ← A: 纯算法（不依赖任何GUI库）
├── gui.py                        ← B: 绘图界面（Tkinter + Matplotlib）
├── main.py                       ← C: 启动入口（3行代码）
│
└── sample_coastline.csv          ← 示例坐标文件
```

### 为什么要分三个文件？

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  algorithm.py │     │   gui.py     │     │   main.py    │
│              │     │              │     │              │
│ 纯数学计算    │◄────│ 界面调用算法  │◄────│ 组装并启动    │
│ 不import GUI │     │ import算法   │     │ import GUI   │
│ 可单独测试   │     │ 绑图+交互    │     │ 3行搞定      │
└──────────────┘     └──────────────┘     └──────────────┘
   0个依赖              依赖 algorithm       依赖 gui
```

**好处**：
- `algorithm.py` 可以脱离 GUI **单独 import 使用**（比如批量处理 1000 条折线）
- 改界面不动算法，改算法不动界面
- 测试算法时不需要弹窗口：`python -c "from algorithm import *; print(douglas_peucker(...))">`

### 2.1 最终界面布局

```
┌──────────────────────────────────────────────────────────────┐
│ [📌采点][✋拖动][📐连线][🔍压缩] ε:[=====●=====] 2.00 [📂][💾][🗑️] │
├────────────────────────────────────┬─────────────────────────┤
│                                    │ 📋 压缩结果              │
│    蓝色细线 + 蓝点 = 原始折线       │                         │
│    红色粗线 + 绿点 = 压缩后         │ 原始点数:  20           │
│    灰色 × = 被丢弃的点             │ 保留点数:  6            │
│                                    │ 压缩率:    70.0%        │
│                                    │ 容差 ε:    2.00         │
│                                    │                         │
│                                    │ ── 保留的点 ──           │
│                                    │ P1(1.0, 2.0)           │
│                                    │ P5(4.2, 8.1)           │
│                                    │ ...                     │
├────────────────────────────────────┴─────────────────────────┤
│ 📍 已压缩 | 20→6 个点 | 压缩率 70.0% | 拖动滑块调整 ε         │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 调用关系

```python
# main.py 中:
from gui import DPApp            # main 只认识 gui

# gui.py 中:
from algorithm import point_to_segment_dist, douglas_peucker
                                  # gui 调用 algorithm 的两个函数

# algorithm.py 中:
import math                       # 只依赖标准库, 不认识 tkinter/matplotlib
```

---

## 3. 文件A: algorithm.py — 纯算法

> 这个文件**不 import 任何 GUI 库**，只有纯数学计算。
> 可以单独 `from algorithm import *` 在脚本或 Jupyter 中使用。

整个文件只有 **2 个函数**，写进同一个 `algorithm.py` 即可。

---

### A-1: 点到线段的垂直距离

```python
"""
algorithm.py —— Douglas-Peucker 纯算法模块
不依赖任何 GUI 库, 可独立 import 使用。
"""
import math


def point_to_segment_dist(p, a, b):
    """
    计算点 P 到直线 AB 的垂直距离。

    参数:
        p: tuple (px, py) —— 待测点
        a: tuple (x1, y1) —— 线段起点
        b: tuple (x2, y2) —— 线段终点

    返回:
        float —— 垂直距离

    数学推导:
        向量 AB = (x2-x1, y2-y1)
        向量 AP = (px-x1, py-y1)

        叉积 cross = AB x AP
                   = (x2-x1)*(py-y1) - (y2-y1)*(px-x1)

        平行四边形面积 / 底边长度 = 高 = 垂距

                |cross|
        d = ─────────────
               |AB|

    特殊情况:
        A == B（线段退化为点）→ 直接算 |AP|（欧氏距离）
    """

    # 线段向量 AB 的分量
    ab_x = b[0] - a[0]            # x2 - x1
    ab_y = b[1] - a[1]            # y2 - y1

    # 线段长度
    ab_len = math.sqrt(ab_x * ab_x + ab_y * ab_y)

    # ── 特殊情况: A 和 B 重合 ──
    if ab_len < 1e-12:
        return math.sqrt((p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2)

    # ── 正常情况: 叉积法算垂距 ──
    ap_x = p[0] - a[0]            # px - x1
    ap_y = p[1] - a[1]            # py - y1

    cross = ab_x * ap_y - ab_y * ap_x    # AB x AP

    return abs(cross) / ab_len
```

**要点**：
- **模块级函数**（不在类里），谁都能调用
- 核心还是叉积 `ab_x * ap_y - ab_y * ap_x`，和上个项目一脉相承
- `abs(cross)` 取绝对值：距离不分正负
- `ab_len < 1e-12` 防零除

---

### A-2: Douglas-Peucker 递归

```python
def douglas_peucker(points, epsilon):
    """
    Douglas-Peucker 折线简化算法。

    参数:
        points:  list of (x, y) —— 原始折线的点序列
        epsilon: float —— 容差阈值

    返回:
        list of int —— 被保留的点的索引列表（升序）

    为什么返回索引:
        方便可视化标注"哪些点保留, 哪些丢弃"。
    """

    def _recurse(start, end):
        """递归内部函数, 处理 points[start..end]"""

        # ── 终止条件: 只剩首尾, 无法再分 ──
        if end - start <= 1:
            return [start]

        a = points[start]              # 首点
        b = points[end]                # 尾点

        # ── 找中间点中离首尾连线最远的 ──
        d_max = 0.0
        k = start

        for i in range(start + 1, end):  # 只遍历中间点
            d = point_to_segment_dist(points[i], a, b)  # 直接调用同模块函数
            if d > d_max:
                d_max = d
                k = i

        # ── 判断 ──
        if d_max > epsilon:
            # 超过容差 → 保留最远点, 递归两半
            left  = _recurse(start, k)
            right = _recurse(k, end)
            return left + right[1:]    # right[1:] 去掉重复的 k
        else:
            # 在容差内 → 中间全丢, 只留首点
            return [start]

    # ── 主调用 ──
    if len(points) <= 2:
        return list(range(len(points)))

    result = _recurse(0, len(points) - 1)
    result.append(len(points) - 1)     # 补上最后一个点
    return result
```

**关键细节**：
1. `_recurse` 是闭包——`points` 和 `epsilon` 不变, 不用每次传参
2. `range(start + 1, end)` 只扫描中间点, 不含首尾
3. `left + right[1:]` 去重合并——最容易出错的地方
4. 末尾 `result.append(...)` 补上最右端点

**`algorithm.py` 完毕，总共就两个函数。** 可以直接在终端验证：
```bash
python -c "from algorithm import *; print(douglas_peucker([(0,0),(1,1),(3,0.5),(5,3),(6,0)], 1.5))"
# 预期输出: [0, 3, 4]
```

---

## 4. 文件B: gui.py — 绘图界面

> 这个文件负责所有 Tkinter 和 Matplotlib 的界面代码。
> 通过 `from algorithm import ...` 调用算法, 自己不做任何数学计算。

---

### B-1: 导入依赖

```python
"""
gui.py —— Douglas-Peucker GUI 界面
调用 algorithm.py 中的算法函数, 自己只负责绑图和交互。
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv

# ── 从算法模块导入 ──
from algorithm import point_to_segment_dist, douglas_peucker
```

**关键一行**：`from algorithm import ...`——GUI 只认识这两个函数名, 不关心实现细节。

---

### B-2: 主窗口初始化

```python
class DPApp:
    """Douglas-Peucker 矢量数据压缩 GUI"""

    def __init__(self, root):
        self.root = root
        self.root.title("📐 Douglas-Peucker 矢量数据压缩")
        self.root.geometry("1200x700")
        self.root.minsize(900, 550)

        # ── 数据状态 ──
        self.points = []              # 原始点 [(x,y), ...]
        self.simplified = []          # 压缩后的点
        self.kept_indices = []        # 保留点的索引
        self.mode = 'pick'            # 'pick' / 'drag'
        self.lines_visible = False
        self.compressed = False

        # ── 拖动状态 ──
        self.drag_index = None
        self.drag_threshold = 0.3

        # ── ε 容差 (Tkinter变量, 双向绑定滑块) ──
        self.epsilon = tk.DoubleVar(value=1.0)

        # ── 搭建界面 ──
        self._build_toolbar()
        self._build_canvas()
        self._build_result_panel()
        self._build_statusbar()
        self._bindbindEvents()
```

**与上个项目的区别**：
- 新增 `simplified`, `kept_indices`——保存压缩结果
- 新增 `epsilon = tk.DoubleVar(value=1.0)`——与 `Scale` 滑块双向绑定
- `compressed` 替代了上个项目的 `analyzed`

---

### B-3: 工具栏搭建（含 ε 滑块）

```python
    def _build_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        btn_cfg = {'padx': 8, 'pady': 4, 'font': ('Microsoft YaHei', 9)}

        # ── 模式按钮 ──
        self.btn_pick = tk.Button(toolbar, text='📌 采点', command=self._mode_pick, relief=tk.SUNKEN, **btn_cfg)
        self.btn_pick.pack(side=tk.LEFT, padx=2)
        self.btn_drag = tk.Button(toolbar, text='✋ 拖动', command=self._mode_drag, **btn_cfg)
        self.btn_drag.pack(side=tk.LEFT, padx=2)

        # ── 功能按钮 ──
        tk.Button(toolbar, text='📐 连线', command=self.connect_lines, **btn_cfg).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text='🔍 压缩', command=self.run_compression, **btn_cfg).pack(side=tk.LEFT, padx=2)

        # ── 分隔线 ──
        tk.Frame(toolbar, width=2, bd=1, relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)

        # ══════════════════════════════
        #  ε 滑块（本项目新控件）
        # ══════════════════════════════
        tk.Label(toolbar, text="ε:", font=('Microsoft YaHei', 10, 'bold')).pack(side=tk.LEFT, padx=(4,0))

        self.eps_scale = tk.Scale(
            toolbar,
            variable=self.epsilon,     # 绑定到 DoubleVar
            from_=0.01,                # 最小值 (from_ 因为 from 是关键字)
            to=5.0,                    # 最大值
            resolution=0.01,           # 步进精度
            orient=tk.HORIZONTAL,      # 水平方向
            length=200,                # 滑块宽度 200px
            showvalue=True,            # 显示当前数值
            font=('Consolas', 9),
            command=self._on_epsilon_change  # 值变化回调 (B-11)
        )
        self.eps_scale.pack(side=tk.LEFT, padx=4)

        # ── 分隔线 + 文件按钮 ──
        tk.Frame(toolbar, width=2, bd=1, relief=tk.SUNKEN).pack(side=tk.LEFT, fill=tk.Y, padx=6, pady=2)
        tk.Button(toolbar, text='📂 导入', command=self.import_points, **btn_cfg).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text='💾 导出', command=self.export_results, **btn_cfg).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text='🗑️ 清空', command=self.clear_all, fg='red', **btn_cfg).pack(side=tk.RIGHT, padx=2)

    def _mode_pick(self):
        self.mode = 'pick'
        self.btn_pick.config(relief=tk.SUNKEN)
        self.btn_drag.config(relief=tk.RAISED)
        self._update_status("模式: 采点 | 左键采点, 右键撤销")

    def _mode_drag(self):
        self.mode = 'drag'
        self.btn_pick.config(relief=tk.RAISED)
        self.btn_drag.config(relief=tk.SUNKEN)
        self._update_status("模式: 拖动 | 左键按住拖动已有的点")
```

**`tk.Scale` 要点**：
- `variable=self.epsilon`：拖滑块 → `epsilon` 自动更新；`epsilon.set(2.0)` → 滑块自动跳
- `command` 的回调**必须接一个参数**（Scale 会传当前值字符串）
- `from_` 有下划线（`from` 是 Python 关键字）

---

### B-4: Matplotlib 画布嵌入

```python
    def _build_canvas(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7, 5), dpi=600)
        self.fig.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.08)
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 20)
        self.ax.set_aspect('equal')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.set_title("左键采点 | 右键撤销", fontsize=10, color='gray')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.ax.set_navigate(False)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
```

**直接复用上个项目。**

---

### B-5: 右侧结果面板

```python
    def _build_result_panel(self):
        result_frame = tk.LabelFrame(self.main_frame, text=' 📋 压缩结果 ',
                                     font=('Microsoft YaHei', 10, 'bold'), padx=5, pady=5)
        result_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0,5), pady=5)

        self.result_text = tk.Text(result_frame, width=28, font=('Consolas', 10),
                                   state=tk.DISABLED, bg='#FAFAFA', wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

        self.result_text.tag_config('kept',    foreground='#2E7D32')   # 保留 → 绿色
        self.result_text.tag_config('removed', foreground='#9E9E9E')   # 丢弃 → 灰色
        self.result_text.tag_config('header',  font=('Microsoft YaHei', 10, 'bold'))
        self.result_text.tag_config('stat',    foreground='#1565C0')   # 统计 → 蓝色
```

---

### B-6: 底部状态栏

```python
    def _build_statusbar(self):
        self.statusbar = tk.Label(self.root, text='📍 模式: 采点 | 已采集 0 个点',
                                  bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                  font=('Microsoft YaHei', 9), padx=10)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_status(self, text):
        n = len(self.points)
        self.statusbar.config(text=f"📍 {text} | 已采集 {n} 个点")
```

---

### B-7: 鼠标事件绑定

```python
    def _bindBindEvents(self):
        self.canvas.mpl_connect('button_press_event',   self._on_press)
        self.canvas.mpl_connect('motion_notify_event',  self._on_motion)
        self.canvas.mpl_connect('button_release_event', self._on_release)
```

---

### B-8: 采点 / 撤销 / 拖动

```python
    def _on_press(self, event):
        if event.inaxes != self.ax:
            return
        if self.mode == 'pick':
            self._handle_pick(event)
        elif self.mode == 'drag':
            self._handle_drag_start(event)

    def _handle_pick(self, event):
        if event.button == 1:
            self.points.append((event.xdata, event.ydata))
            self.lines_visible = False
            self.compressed = False
            self._redraw()
            self._update_status("模式: 采点 | 左键采点, 右键撤销")
        elif event.button == 3:
            self._handle_undo()

    def _handle_undo(self):
        if not self.points:
            self._update_status("没有可撤销的点")
            return
        removed = self.points.pop()
        self.lines_visible = False
        self.compressed = False
        self._redraw()
        self._update_status(f"已撤销 ({removed[0]:.1f}, {removed[1]:.1f})")

    def _handle_drag_start(self, event):
        if event.button != 1 or not self.points:
            return
        click = np.array([event.xdata, event.ydata])
        pts = np.array(self.points)
        distances = np.linalg.norm(pts - click, axis=1)
        min_idx = np.argmin(distances)
        self.drag_index = min_idx if distances[min_idx] < self.drag_threshold else None

    def _on_motion(self, event):
        if self.mode != 'drag' or self.drag_index is None or event.inaxes != self.ax:
            return
        self.points[self.drag_index] = (event.xdata, event.ydata)
        self._redraw()

    def _on_release(self, event):
        if self.mode == 'drag' and self.drag_index is not None:
            self.drag_index = None
            if self.compressed:
                self.run_compression()     # 拖动后自动重压缩
```

---

### B-9: 画布重绘

```python
    def _redraw(self):
        self.ax.cla()
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 20)
        self.ax.set_aspect('equal')
        self.ax.grid(True, linestyle='--', alpha=0.3)

        if not self.points:
            self.ax.set_title("左键采点 | 右键撤销", fontsize=10, color='gray')
            self.canvas.draw()
            return

        xs, ys = zip(*self.points)

        # ── 原始折线: 浅蓝色 ──
        if self.lines_visible:
            self.ax.plot(xs, ys, '-o', color='#90CAF9', linewidth=0.8,
                         markersize=3, markerfacecolor='#90CAF9',
                         markeredgecolor='#64B5F6', zorder=1, label='原始折线')

        # ── 压缩结果: 红线 + 绿点 + 灰× ──
        if self.compressed and self.simplified:
            sx, sy = zip(*self.simplified)
            self.ax.plot(sx, sy, '-', color='#E53935', linewidth=1.5, zorder=3, label='压缩后')
            self.ax.scatter(sx, sy, c='#2E7D32', s=40, zorder=4,
                            edgecolors='#1B5E20', linewidths=0.8, label='保留')

            kept_set = set(self.kept_indices)
            rm_x = [self.points[i][0] for i in range(len(self.points)) if i not in kept_set]
            rm_y = [self.points[i][1] for i in range(len(self.points)) if i not in kept_set]
            if rm_x:
                self.ax.scatter(rm_x, rm_y, c='#BDBDBD', s=30, marker='x',
                                zorder=2, linewidths=0.8, label='丢弃')
            self.ax.legend(loc='upper right', fontsize=7, framealpha=0.8)
        else:
            self.ax.scatter(xs, ys, c='red', s=40, zorder=2,
                            edgecolors='darkred', linewidths=0.8)

        # ── 点号标注 ──
        for i, (x, y) in enumerate(self.points):
            self.ax.annotate(f'P{i+1}', (x, y), textcoords="offset points",
                             xytext=(6, 6), fontsize=7, fontweight='bold',
                             color='#333333', zorder=5)

        # ── 标题 ──
        if self.compressed:
            n_o, n_k = len(self.points), len(self.simplified)
            self.ax.set_title(f"{n_o}->{n_k} 点 | 压缩率 {(1-n_k/n_o)*100:.1f}% | e={self.epsilon.get():.2f}",
                              fontsize=9, color='#333')
        else:
            self.ax.set_title(f"共 {len(self.points)} 个点", fontsize=10, color='gray')

        self.canvas.draw()
```

**可视化分层**：
```
图层5  点号标注 P1,P2...
图层4  保留的点 (绿●)
图层3  压缩折线 (红线)
图层2  丢弃的点 (灰×) / 未压缩时的红点
图层1  原始折线 (浅蓝)
```

---

### B-10: 压缩执行 + 结果面板写入

```python
    def run_compression(self):
        """执行 DP 压缩"""
        if len(self.points) < 3:
            messagebox.showwarning("提示", "至少需要 3 个点！")
            return

        # ── 调用 algorithm.py 的函数 ──
        eps = self.epsilon.get()
        self.kept_indices = douglas_peucker(self.points, eps)    # ← 算法调用
        self.simplified = [self.points[i] for i in self.kept_indices]

        self.lines_visible = True
        self.compressed = True
        self._redraw()
        self._write_result_panel()

        n_o, n_k = len(self.points), len(self.simplified)
        self._update_status(f"已压缩 | {n_o}->{n_k} 点 | 压缩率 {(1-n_k/n_o)*100:.1f}%")

    def _write_result_panel(self):
        """写入右侧结果面板"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)

        n_o, n_k = len(self.points), len(self.simplified)
        ratio = (1 - n_k / n_o) * 100

        self.result_text.insert(tk.END, "=== 压缩统计 ===\n\n", 'header')
        self.result_text.insert(tk.END, f"  原始点数:  {n_o}\n", 'stat')
        self.result_text.insert(tk.END, f"  保留点数:  {n_k}\n", 'stat')
        self.result_text.insert(tk.END, f"  丢弃点数:  {n_o - n_k}\n", 'stat')
        self.result_text.insert(tk.END, f"  压缩率:    {ratio:.1f}%\n", 'stat')
        self.result_text.insert(tk.END, f"  容差 e:    {self.epsilon.get():.2f}\n\n", 'stat')

        self.result_text.insert(tk.END, "=== 保留的点 ===\n\n", 'header')
        for idx in self.kept_indices:
            x, y = self.points[idx]
            self.result_text.insert(tk.END, f"  P{idx+1} ({x:.2f}, {y:.2f})\n", 'kept')

        self.result_text.insert(tk.END, "\n=== 丢弃的点 ===\n\n", 'header')
        kept_set = set(self.kept_indices)
        for i in range(n_o):
            if i not in kept_set:
                x, y = self.points[i]
                self.result_text.insert(tk.END, f"  P{i+1} ({x:.2f}, {y:.2f})\n", 'removed')

        self.result_text.config(state=tk.DISABLED)
```

**注意 `run_compression` 中的调用**：
```python
self.kept_indices = douglas_peucker(self.points, eps)
```
这就是 `gui.py` 和 `algorithm.py` 的**唯一接触点**。GUI 不知道递归怎么实现, 只知道"传入点和 ε, 拿回索引列表"。

---

### B-11: ε 滑块联动

```python
    def _on_epsilon_change(self, value):
        """ε 滑块变化回调。Scale 会传一个参数(当前值字符串), 必须接收。"""
        if self.compressed:
            self.run_compression()     # 已压缩过 → 用新 ε 重压缩
```

---

### B-12: 连线 / 清空 / 导入 / 导出

```python
    def connect_lines(self):
        if len(self.points) < 2:
            messagebox.showwarning("提示", "至少需要 2 个点！")
            return
        self.lines_visible = True
        self._redraw()
        self._update_status("已连线 | 点击 [🔍压缩] 或拖动 e 滑块")

    def clear_all(self):
        if self.points and not messagebox.askyesno("确认", "确定清空？"):
            return
        self.points.clear()
        self.simplified.clear()
        self.kept_indices.clear()
        self.lines_visible = False
        self.compressed = False
        self.drag_index = None
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self.result_text.config(state=tk.DISABLED)
        self._redraw()
        self._update_status("已清空 | 模式: 采点")

    def import_points(self):
        filepath = filedialog.askopenfilename(
            title="选择坐标文件",
            filetypes=[("CSV", "*.csv"), ("TXT", "*.txt"), ("All", "*.*")],
            initialdir="."
        )
        if not filepath:
            return
        try:
            new_pts = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if not row or row[0].strip().startswith('#'):
                        continue
                    try:
                        new_pts.append((float(row[0].strip()), float(row[1].strip())))
                    except (ValueError, IndexError):
                        continue
            if not new_pts:
                messagebox.showwarning("提示", "没有有效坐标！")
                return
            self.points = new_pts
            self.lines_visible = False
            self.compressed = False
            self.simplified.clear()
            self.kept_indices.clear()
            xs, ys = zip(*self.points)
            margin = max((max(xs)-min(xs))*0.15, (max(ys)-min(ys))*0.15, 0.5)
            self.ax.set_xlim(min(xs)-margin, max(xs)+margin)
            self.ax.set_ylim(min(ys)-margin, max(ys)+margin)
            self._redraw()
            self._update_status(f"已导入 {len(self.points)} 个点")
        except Exception as e:
            messagebox.showerror("导入失败", str(e))

    def export_results(self):
        if not self.points:
            messagebox.showwarning("提示", "没有数据！")
            return
        filepath = filedialog.asksaveasfilename(
            title="保存", defaultextension=".csv",
            filetypes=[("CSV", "*.csv")], initialfile="dp_result.csv"
        )
        if not filepath:
            return
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(['点序号', 'X', 'Y', '状态'])
                kept_set = set(self.kept_indices) if self.compressed else set()
                for i, (x, y) in enumerate(self.points):
                    status = '保留' if i in kept_set else ('丢弃' if self.compressed else '未压缩')
                    w.writerow([f'P{i+1}', f'{x:.4f}', f'{y:.4f}', status])
            self._update_status(f"已导出到 {filepath}")
        except Exception as e:
            messagebox.showerror("导出失败", str(e))
```

**`gui.py` 完毕。** 全部都是界面逻辑, 唯一调用算法的地方在 `run_compression` 里的一行 `douglas_peucker(...)`。

---

## 5. 文件C: main.py — 启动入口

```python
"""
main.py —— 程序启动入口
只做三件事: 配中文字体 → 创建窗口 → 运行
"""
import tkinter as tk
import matplotlib.pyplot as plt
from gui import DPApp


def main():
    root = tk.Tk()
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    app = DPApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
```

**运行方式**：
```bash
cd Douglas_Peucker
python main.py
```

---

## 6. 坐标文件格式

示例文件 `sample_coastline.csv`：

```csv
# 模拟海岸线数据 (20个点)
1.0, 2.0
2.0, 2.3
3.0, 2.1
4.0, 2.5
5.0, 4.0
6.0, 6.5
6.5, 7.0
7.0, 7.2
8.0, 7.0
9.0, 5.5
10.0, 5.0
11.0, 5.2
12.0, 5.1
13.0, 6.0
14.0, 8.0
14.5, 9.0
15.0, 9.2
16.0, 9.0
17.0, 7.5
18.0, 6.0
```

---

## 7. 手算验证练习

### 练习: 5 个点，ε = 1.5

```
P1(0, 0)   P2(1, 1)   P3(3, 0.5)   P4(5, 3)   P5(6, 0)
```

**第1轮**：首=P1(0,0)，尾=P5(6,0)

首尾连线就是 x 轴方向的线段，所以垂距就是 y 坐标的绝对值：

```
AB = (6, 0),  |AB| = 6

P2: cross = 6*1 - 0*1 = 6,     d = |6|/6 = 1.0
P3: cross = 6*0.5 - 0*3 = 3,   d = |3|/6 = 0.5
P4: cross = 6*3 - 0*5 = 18,    d = |18|/6 = 3.0  ← d_max
```

d_max = 3.0 > ε(1.5) → 保留 P4，分成 [P1..P4] 和 [P4..P5]

**第2轮左**：首=P1(0,0)，尾=P4(5,3)

```
AB = (5, 3),  |AB| = sqrt(34) = 5.831

P2: cross = 5*1 - 3*1 = 2,     d = 2/5.831 = 0.343
P3: cross = 5*0.5 - 3*3 = -6.5, d = 6.5/5.831 = 1.115
```

d_max = 1.115 ≤ ε(1.5) → 丢弃 P2, P3

**第2轮右**：首=P4(5,3)，尾=P5(6,0)

中间无点（相邻），直接返回 [P4]

**最终结果**：保留 P1, P4, P5（索引 [0, 3, 4]），丢弃 P2, P3

```
原始:   P1 ── P2 ── P3 ── P4 ── P5   (5个点)
压缩后: P1 ─────────── P4 ── P5      (3个点)
压缩率: 40%
```

在程序中输入这 5 个点，设 ε=1.5，验证结果是否一致。

---

## 8. 思考题

1. **ε = 0 时会发生什么？** 所有点都会保留吗？为什么？
   - 提示：看 `d_max > epsilon` 这个判断条件，0 距离的点怎么处理？

2. **ε 很大时（比如 100）会发生什么？**
   - 提示：所有中间点的距离都 < ε，最终只剩首尾两点

3. **这个算法是从两端向中间压缩的。如果换成从左向右逐点扫描（垂距法 §5.1.2），结果会一样吗？**
   - 提示：不一样。DP 算法是全局最优贪心（保证最大偏移 ≤ ε），逐点扫描是局部贪心

4. **如果折线是闭合的（首尾相连），算法需要怎么修改？**
   - 提示：选择折线上离首尾连线最远的点作为新的起始/终止点，然后拆成两段分别处理

5. **当前 `point_to_segment_dist` 算的是点到无限直线的距离。如果改成严格的点到线段距离（考虑垂足在线段外的情况），DP 结果会有区别吗？**
   - 提示：在 DP 算法中通常没区别，因为中间点的垂足总在首尾之间。但如果折线有剧烈折返，可能会出现差异

---

> 📌 写完三个文件后，`algorithm.py` + `gui.py` + `main.py` + `sample_coastline.csv` 一起提交到仓库。
