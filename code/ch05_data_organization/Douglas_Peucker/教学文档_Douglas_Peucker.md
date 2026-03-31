# 📐 Douglas-Peucker 矢量数据压缩 —— 完整 GUI 教学文档

> **对应章节**：第5章 §5.1.3 道格拉斯-普克法
> **核心算法**：递归分治 + 点到线段垂距
> **技术栈**：Python 3.x + Tkinter + Matplotlib
> **前置知识**：第2章 §2.3 向量叉积（已在「折线段拐向判断」中学过）

---

## 📖 目录

1. [数学原理](#1-数学原理)
2. [项目结构](#2-项目结构)
3. [代码分块详解](#3-代码分块详解)
   - [Block 0: 导入依赖](#block-0-导入依赖)
   - [Block 1: 主窗口初始化](#block-1-主窗口初始化)
   - [Block 2: 工具栏搭建（含 ε 滑块）](#block-2-工具栏搭建含-ε-滑块)
   - [Block 3: Matplotlib 画布嵌入](#block-3-matplotlib-画布嵌入)
   - [Block 4: 右侧结果面板](#block-4-右侧结果面板)
   - [Block 5: 底部状态栏](#block-5-底部状态栏)
   - [Block 6: 鼠标事件绑定](#block-6-鼠标事件绑定)
   - [Block 7: 采点 / 撤销 / 拖动（复用）](#block-7-采点--撤销--拖动复用)
   - [Block 8: 点到线段的垂直距离（核心子算法）](#block-8-点到线段的垂直距离核心子算法)
   - [Block 9: Douglas-Peucker 递归（核心算法）](#block-9-douglas-peucker-递归核心算法)
   - [Block 10: 压缩执行 + 可视化](#block-10-压缩执行--可视化)
   - [Block 11: 画布重绘](#block-11-画布重绘)
   - [Block 12: ε 滑块联动](#block-12-ε-滑块联动)
   - [Block 13: 连线功能](#block-13-连线功能)
   - [Block 14: 清空重置](#block-14-清空重置)
   - [Block 15: 导入坐标文件](#block-15-导入坐标文件)
   - [Block 16: 导出结果](#block-16-导出结果)
   - [Block 17: 程序入口](#block-17-程序入口)
4. [坐标文件格式](#4-坐标文件格式)
5. [手算验证练习](#5-手算验证练习)
6. [思考题](#6-思考题)

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

## 2. 项目结构

```
Douglas_Peucker/
├── 教学文档_Douglas_Peucker.md    ← 你正在看的文件
├── dp_app.py                     ← 主程序（你来写）
└── sample_coastline.csv          ← 示例坐标文件
```

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

---

## 3. 代码分块详解

---

### Block 0: 导入依赖

```python
import tkinter as tk                      # GUI 框架
from tkinter import filedialog, messagebox  # 文件对话框, 弹出提示
import numpy as np                         # 数值计算
import matplotlib
matplotlib.use('TkAgg')                    # 指定 Matplotlib 使用 Tkinter 后端
import matplotlib.pyplot as plt            # 绑图 API
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # 嵌入桥梁
import csv                                 # 读写坐标文件
import math                                # sqrt, 用于距离计算
```

**与上个项目的区别**：
- 去掉了 `NavigationToolbar2Tk`（上个项目也没用到）
- 去掉了 `FancyArrowPatch`（这个项目不需要弧形箭头）
- 新增 `math` 模块用于 `sqrt`

---

### Block 1: 主窗口初始化

```python
class DPApp:
    """Douglas-Peucker 矢量数据压缩 GUI 应用"""

    def __init__(self, root):
        # ── Tkinter 根窗口 ──
        self.root = root
        self.root.title("📐 Douglas-Peucker 矢量数据压缩")
        self.root.geometry("1200x700")
        self.root.minsize(900, 550)

        # ── 数据状态 ──
        self.points = []              # 原始点列表 [(x,y), ...]
        self.simplified = []          # 压缩后的点列表（DP 算法输出）
        self.kept_indices = []        # 被保留的点在原始列表中的索引
        self.mode = 'pick'            # 'pick' 或 'drag'
        self.lines_visible = False    # 原始折线是否已绘制
        self.compressed = False       # 是否已执行过压缩

        # ── 拖动状态 ──
        self.drag_index = None
        self.drag_threshold = 0.3

        # ── ε 容差（默认值，后面会绑定到滑块） ──
        self.epsilon = tk.DoubleVar(value=1.0)  # Tkinter 变量，双向绑定滑块

        # ── 搭建界面 ──
        self._build_toolbar()         # Block 2
        self._build_canvas()          # Block 3
        self._build_result_panel()    # Block 4
        self._build_statusbar()       # Block 5
        self._bindbindEvents()              # Block 6
```

**与上个项目的区别**：
- 新增 `self.simplified` 和 `self.kept_indices`——保存压缩结果
- 新增 `self.epsilon = tk.DoubleVar(value=1.0)`——Tkinter 的特殊变量类型，可以与 `Scale` 滑块**双向绑定**：滑块动了变量自动更新，变量改了滑块也跟着动
- `self.compressed` 标记是否执行过压缩（控制画面显示）

---

### Block 2: 工具栏搭建（含 ε 滑块）

```python
    def _build_toolbar(self):
        """创建顶部工具栏"""
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        btn_cfg = {'padx': 8, 'pady': 4, 'font': ('Microsoft YaHei', 9)}

        # ── 模式按钮 ──
        self.btn_pick = tk.Button(
            toolbar, text='📌 采点',
            command=self._mode_pick,
            relief=tk.SUNKEN,        # 默认选中
            **btn_cfg
        )
        self.btn_pick.pack(side=tk.LEFT, padx=2)

        self.btn_drag = tk.Button(
            toolbar, text='✋ 拖动',
            command=self._mode_drag,
            **btn_cfg
        )
        self.btn_drag.pack(side=tk.LEFT, padx=2)

        # ── 功能按钮 ──
        tk.Button(
            toolbar, text='📐 连线',
            command=self.connect_lines,
            **btn_cfg
        ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            toolbar, text='🔍 压缩',
            command=self.run_compression,    # 执行 DP 压缩
            **btn_cfg
        ).pack(side=tk.LEFT, padx=2)

        # ── 分隔线 ──
        tk.Frame(toolbar, width=2, bd=1, relief=tk.SUNKEN).pack(
            side=tk.LEFT, fill=tk.Y, padx=6, pady=2
        )

        # ══════════════════════════════════════════════════
        #  ε 滑块 —— 这是本项目的新控件
        # ══════════════════════════════════════════════════

        # 标签 "ε:"
        tk.Label(
            toolbar,
            text="ε:",
            font=('Microsoft YaHei', 10, 'bold')
        ).pack(side=tk.LEFT, padx=(4, 0))

        # Scale 滑块控件
        self.eps_scale = tk.Scale(
            toolbar,
            variable=self.epsilon,     # 绑定到 self.epsilon (DoubleVar)
            from_=0.01,                # 滑块最小值
            to=5.0,                    # 滑块最大值
            resolution=0.01,           # 步进精度: 每次滑动变化 0.01
            orient=tk.HORIZONTAL,      # 水平方向
            length=200,                # 滑块长度 200 像素
            showvalue=True,            # 在滑块上方显示当前数值
            font=('Consolas', 9),
            command=self._on_epsilon_change  # 滑块值变化时的回调（Block 12）
        )
        self.eps_scale.pack(side=tk.LEFT, padx=4)

        # ── 分隔线 ──
        tk.Frame(toolbar, width=2, bd=1, relief=tk.SUNKEN).pack(
            side=tk.LEFT, fill=tk.Y, padx=6, pady=2
        )

        # ── 文件按钮 ──
        tk.Button(toolbar, text='📂 导入', command=self.import_points, **btn_cfg).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text='💾 导出', command=self.export_results, **btn_cfg).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text='🗑️ 清空', command=self.clear_all, fg='red', **btn_cfg).pack(side=tk.RIGHT, padx=2)

    # ── 模式切换（与上个项目完全相同） ──
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

**新控件 `tk.Scale`（滑块）详解**：
- `variable=self.epsilon`：双向绑定。拖滑块 → `self.epsilon` 自动更新；代码设 `self.epsilon.set(2.0)` → 滑块自动跳到 2.0
- `from_=0.01, to=5.0`：滑块范围。注意 `from_` 有下划线（因为 `from` 是 Python 关键字）
- `resolution=0.01`：最小步进。用户拖动时值以 0.01 为单位跳变
- `command=self._on_epsilon_change`：每次值变化都触发回调。注意 Scale 的 command 会传一个参数（当前值的字符串），所以回调函数要接收一个参数
- `showvalue=True`：在滑块上方显示当前数值，方便用户看到精确值

---

### Block 3: Matplotlib 画布嵌入

```python
    def _build_canvas(self):
        """创建 Matplotlib Figure 并嵌入"""
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7, 5), dpi=600)
        self.fig.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.08)

        # ── 坐标轴初始化 ──
        self.ax.set_xlim(0, 20)
        self.ax.set_ylim(0, 20)
        self.ax.set_aspect('equal')
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.set_title("左键采点 | 右键撤销", fontsize=10, color='gray')

        # ── 嵌入 Tkinter ──
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.ax.set_navigate(False)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
```

**与上个项目完全相同**，直接复用。

---

### Block 4: 右侧结果面板

```python
    def _build_result_panel(self):
        """创建右侧结果面板"""
        result_frame = tk.LabelFrame(
            self.main_frame,
            text=' 📋 压缩结果 ',
            font=('Microsoft YaHei', 10, 'bold'),
            padx=5, pady=5
        )
        result_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)

        self.result_text = tk.Text(
            result_frame,
            width=28,
            font=('Consolas', 10),
            state=tk.DISABLED,
            bg='#FAFAFA',
            wrap=tk.WORD
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)

        # ── 颜色标签 ──
        self.result_text.tag_config('kept',    foreground='#2E7D32')  # 保留的点 → 绿色
        self.result_text.tag_config('removed', foreground='#9E9E9E')  # 丢弃的点 → 灰色
        self.result_text.tag_config('header',  font=('Microsoft YaHei', 10, 'bold'))
        self.result_text.tag_config('stat',    foreground='#1565C0')  # 统计数字 → 蓝色
```

**与上个项目的区别**：
- tag 名称变了：`kept`（保留）/ `removed`（丢弃）替代 `left`/`right`/`collinear`
- 新增 `stat` 标签用于统计数字高亮

---

### Block 5: 底部状态栏

```python
    def _build_statusbar(self):
        """创建底部状态栏"""
        self.statusbar = tk.Label(
            self.root,
            text='📍 模式: 采点 | 已采集 0 个点',
            bd=1, relief=tk.SUNKEN, anchor=tk.W,
            font=('Microsoft YaHei', 9), padx=10
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_status(self, text):
        n = len(self.points)
        self.statusbar.config(text=f"📍 {text} | 已采集 {n} 个点")
```

**与上个项目完全相同。**

---

### Block 6: 鼠标事件绑定

```python
    def _bindBindEvents(self):
        """绑定 Matplotlib 画布的鼠标事件"""
        self.canvas.mpl_connect('button_press_event',   self._on_press)
        self.canvas.mpl_connect('motion_notify_event',  self._on_motion)
        self.canvas.mpl_connect('button_release_event', self._on_release)
```

**与上个项目完全相同。**

---

### Block 7: 采点 / 撤销 / 拖动（复用）

```python
    # ── 鼠标按下统一入口 ──
    def _on_press(self, event):
        if event.inaxes != self.ax:
            return
        if self.mode == 'pick':
            self._handle_pick(event)
        elif self.mode == 'drag':
            self._handle_drag_start(event)

    # ── 采点 ──
    def _handle_pick(self, event):
        if event.button == 1:          # 左键
            self.points.append((event.xdata, event.ydata))
            self.lines_visible = False
            self.compressed = False    # 新增点后压缩结果作废
            self._redraw()
            self._update_status("模式: 采点 | 左键采点, 右键撤销")
        elif event.button == 3:        # 右键
            self._handle_undo()

    # ── 撤销 ──
    def _handle_undo(self):
        if not self.points:
            self._update_status("没有可撤销的点")
            return
        removed = self.points.pop()
        self.lines_visible = False
        self.compressed = False
        self._redraw()
        self._update_status(f"已撤销 ({removed[0]:.1f}, {removed[1]:.1f})")

    # ── 拖动开始 ──
    def _handle_drag_start(self, event):
        if event.button != 1 or not self.points:
            return
        click = np.array([event.xdata, event.ydata])
        pts = np.array(self.points)
        distances = np.linalg.norm(pts - click, axis=1)
        min_idx = np.argmin(distances)
        if distances[min_idx] < self.drag_threshold:
            self.drag_index = min_idx
        else:
            self.drag_index = None

    # ── 拖动中 ──
    def _on_motion(self, event):
        if self.mode != 'drag' or self.drag_index is None or event.inaxes != self.ax:
            return
        self.points[self.drag_index] = (event.xdata, event.ydata)
        self._redraw()

    # ── 拖动结束 ──
    def _on_release(self, event):
        if self.mode == 'drag' and self.drag_index is not None:
            self.drag_index = None
            # 如果之前压缩过，拖动后自动重新压缩
            if self.compressed:
                self.run_compression()
```

**与上个项目几乎相同**，只有两处区别：
1. `self.analyzed` 换成了 `self.compressed`
2. 拖动结束后自动调用 `self.run_compression()` 而不是 `self.analyze_turning()`

---

### Block 8: 点到线段的垂直距离（核心子算法）

```python
    @staticmethod
    def point_to_segment_dist(p, a, b):
        """
        计算点 P 到线段 AB 的垂直距离。

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

            叉积的几何含义 = 平行四边形面积
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
            # 线段退化为点，直接算点到点的欧氏距离
            return math.sqrt(
                (p[0] - a[0]) ** 2 + (p[1] - a[1]) ** 2
            )

        # ── 正常情况: 叉积法算垂距 ──
        # 向量 AP
        ap_x = p[0] - a[0]            # px - x1
        ap_y = p[1] - a[1]            # py - y1

        # 叉积 = AB x AP = ab_x * ap_y - ab_y * ap_x
        cross = ab_x * ap_y - ab_y * ap_x

        # 垂距 = |叉积| / |AB|
        dist = abs(cross) / ab_len

        return dist
```

**要点**：
- 这个函数和上个项目的叉积计算**高度相关**——核心都是 `ax*by - ay*bx`
- `abs(cross)` 取绝对值：叉积正负只表示方向（左右），距离不分正负
- `ab_len < 1e-12` 防零除：首尾重合时退化为点到点距离
- 这里算的是点到**直线**（无限延伸）的距离，不是到线段的距离。DP 算法用直线距离就够了，因为分割点一定在首尾之间

---

### Block 9: Douglas-Peucker 递归（核心算法）

```python
    @staticmethod
    def douglas_peucker(points, epsilon):
        """
        Douglas-Peucker 折线简化算法。

        参数:
            points: list of (x, y) —— 原始折线的点序列
            epsilon: float —— 容差阈值（允许的最大垂距偏移）

        返回:
            list of int —— 被保留的点的索引列表（升序）

        算法流程:
            1. 连首尾为直线
            2. 找所有中间点到直线的最大垂距 d_max 及其索引 k
            3. d_max > epsilon → 保留 k, 递归左半和右半
            4. d_max <= epsilon → 中间全扔, 只返回首点索引

        为什么返回索引而不是点坐标:
            返回索引方便后续标注"哪些点保留了, 哪些被丢弃了",
            可视化时需要知道原始编号。
        """

        def _recurse(start, end):
            """
            递归内部函数。
            处理 points[start..end] 这一段（含两端）。

            参数:
                start: int —— 起始点索引
                end:   int —— 终止点索引

            返回:
                list of int —— 此段中被保留的点的索引
            """

            # ── 递归终止条件 ──
            # 如果这一段只有首和尾（中间没有点可检查），直接返回首点
            if end - start <= 1:
                return [start]

            # ── 步骤1: 首尾两点 ──
            a = points[start]          # 首点坐标
            b = points[end]            # 尾点坐标

            # ── 步骤2: 找中间点中离首尾连线最远的 ──
            d_max = 0.0                # 目前为止的最大距离
            k = start                  # 最远点的索引

            for i in range(start + 1, end):
                # i 从 start+1 到 end-1（不含 start 和 end 本身）
                d = DPApp.point_to_segment_dist(points[i], a, b)
                if d > d_max:
                    d_max = d
                    k = i

            # ── 步骤3: 判断是否需要保留 ──
            if d_max > epsilon:
                # 最远距离超过容差 → 保留这个点, 递归两半
                left  = _recurse(start, k)    # 左半段: start 到 k
                right = _recurse(k, end)      # 右半段: k 到 end
                # 合并: left 已包含 start..k, right 包含 k..end
                # 去掉 right 开头的 k（left 末尾已经有了）避免重复
                return left + right[1:]
            else:
                # 最远距离在容差内 → 中间点全部丢弃, 只保留首点
                return [start]

        # ── 主调用 ──
        if len(points) <= 2:
            # 2个点或更少，无法简化
            return list(range(len(points)))

        # 递归处理整条折线
        result = _recurse(0, len(points) - 1)

        # 补上最后一个点（递归过程只返回左端点, 最终末端需要手动加）
        result.append(len(points) - 1)

        return result
```

**逐行解析关键步骤**：

1. **为什么用闭包 `_recurse`**：
   - `epsilon` 和 `points` 在整个递归过程中不变，放在外层函数里让内部直接访问，避免每次递归都传这两个参数

2. **`for i in range(start + 1, end)`**：
   - 只遍历**中间点**，不包含首点 `start` 和尾点 `end`
   - 这些中间点是"候选丢弃"的点

3. **`return left + right[1:]`**：
   - `left` 的最后一个元素是 `k`
   - `right` 的第一个元素也是 `k`
   - `right[1:]` 跳过开头的 `k`，避免重复
   - 这是递归合并结果时最容易出错的地方

4. **末尾补 `result.append(len(points) - 1)`**：
   - `_recurse` 的 `return [start]` 只返回左端点
   - 整条折线的最右端点（最后一个点）永远不会被某个 `_recurse` 作为 `[start]` 返回
   - 所以最外层手动补上

---

### Block 10: 压缩执行 + 可视化

```python
    def run_compression(self):
        """执行 DP 压缩并更新可视化"""

        if len(self.points) < 3:
            messagebox.showwarning("提示", "至少需要 3 个点才能压缩！")
            return

        # ── 执行算法 ──
        eps = self.epsilon.get()                # 从滑块读取当前 ε 值
        self.kept_indices = self.douglas_peucker(self.points, eps)
        self.simplified = [self.points[i] for i in self.kept_indices]

        # ── 更新标志 ──
        self.lines_visible = True
        self.compressed = True

        # ── 重绘 ──
        self._redraw()

        # ── 写入结果面板 ──
        self._write_result_panel()

        # ── 更新状态栏 ──
        n_orig = len(self.points)
        n_kept = len(self.simplified)
        ratio = (1 - n_kept / n_orig) * 100
        self._update_status(
            f"已压缩 | {n_orig} -> {n_kept} 个点 | 压缩率 {ratio:.1f}% | 拖动滑块调整"
        )

    def _write_result_panel(self):
        """将压缩统计写入右侧面板"""

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)

        n_orig = len(self.points)
        n_kept = len(self.simplified)
        n_removed = n_orig - n_kept
        ratio = (1 - n_kept / n_orig) * 100
        eps = self.epsilon.get()

        # ── 统计信息 ──
        self.result_text.insert(tk.END, "=== 压缩统计 ===\n\n", 'header')
        self.result_text.insert(tk.END, f"  原始点数:  {n_orig}\n", 'stat')
        self.result_text.insert(tk.END, f"  保留点数:  {n_kept}\n", 'stat')
        self.result_text.insert(tk.END, f"  丢弃点数:  {n_removed}\n", 'stat')
        self.result_text.insert(tk.END, f"  压缩率:    {ratio:.1f}%\n", 'stat')
        self.result_text.insert(tk.END, f"  容差 e:    {eps:.2f}\n\n", 'stat')

        # ── 保留的点列表 ──
        self.result_text.insert(tk.END, "=== 保留的点 ===\n\n", 'header')
        for idx in self.kept_indices:
            x, y = self.points[idx]
            self.result_text.insert(
                tk.END,
                f"  P{idx+1} ({x:.2f}, {y:.2f})\n",
                'kept'
            )

        # ── 丢弃的点列表 ──
        self.result_text.insert(tk.END, "\n=== 丢弃的点 ===\n\n", 'header')
        kept_set = set(self.kept_indices)       # 转set，查找 O(1)
        for i in range(n_orig):
            if i not in kept_set:
                x, y = self.points[i]
                self.result_text.insert(
                    tk.END,
                    f"  P{i+1} ({x:.2f}, {y:.2f})\n",
                    'removed'
                )

        self.result_text.config(state=tk.DISABLED)
```

**要点**：
- `self.epsilon.get()` 从 Tkinter `DoubleVar` 读取当前值
- `kept_set = set(...)` 用集合来判断"是否被保留"——`in set` 是 O(1)，比 `in list` 的 O(n) 快
- 压缩率公式：`(1 - 保留数/原始数) × 100%`

---

### Block 11: 画布重绘

```python
    def _redraw(self):
        """清空并重绘画布"""
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

        # ══════════════════════════════════════
        #  原始折线（蓝色细线 + 蓝色小点）
        # ══════════════════════════════════════
        if self.lines_visible:
            self.ax.plot(
                xs, ys, '-o',              # '-o' = 实线 + 圆点标记
                color='#90CAF9',           # 浅蓝色（压缩后变成背景衬托色）
                linewidth=0.8,
                markersize=3,
                markerfacecolor='#90CAF9',
                markeredgecolor='#64B5F6',
                zorder=1,
                label='原始折线'
            )

        # ══════════════════════════════════════
        #  压缩结果（红色粗线 + 绿色大点 + 灰色 × ）
        # ══════════════════════════════════════
        if self.compressed and self.simplified:

            # ── 压缩后的折线: 红色粗线 ──
            sx, sy = zip(*self.simplified)
            self.ax.plot(
                sx, sy, '-',
                color='#E53935',           # 红色
                linewidth=1.5,
                zorder=3,
                label='压缩后'
            )

            # ── 保留的点: 绿色大圆 ──
            self.ax.scatter(
                sx, sy,
                c='#2E7D32',               # 深绿色
                s=40,
                zorder=4,
                edgecolors='#1B5E20',
                linewidths=0.8,
                label='保留'
            )

            # ── 丢弃的点: 灰色 × ──
            kept_set = set(self.kept_indices)
            removed_x = [self.points[i][0] for i in range(len(self.points)) if i not in kept_set]
            removed_y = [self.points[i][1] for i in range(len(self.points)) if i not in kept_set]
            if removed_x:
                self.ax.scatter(
                    removed_x, removed_y,
                    c='#BDBDBD',           # 浅灰色
                    s=30,
                    marker='x',            # × 形标记
                    zorder=2,
                    linewidths=0.8,
                    label='丢弃'
                )

            # ── 图例 ──
            self.ax.legend(
                loc='upper right',
                fontsize=7,
                framealpha=0.8
            )

        else:
            # ── 未压缩时: 只画红色圆点 ──
            self.ax.scatter(
                xs, ys,
                c='red', s=40, zorder=2,
                edgecolors='darkred', linewidths=0.8
            )

        # ── 标注点号 ──
        for i, (x, y) in enumerate(self.points):
            self.ax.annotate(
                f'P{i+1}', (x, y),
                textcoords="offset points", xytext=(6, 6),
                fontsize=7, fontweight='bold', color='#333333', zorder=5
            )

        # ── 标题 ──
        if self.compressed:
            n_orig = len(self.points)
            n_kept = len(self.simplified)
            ratio = (1 - n_kept / n_orig) * 100
            self.ax.set_title(
                f"{n_orig} -> {n_kept} 点 | 压缩率 {ratio:.1f}% | e={self.epsilon.get():.2f}",
                fontsize=9, color='#333'
            )
        else:
            self.ax.set_title(f"共 {len(self.points)} 个点", fontsize=10, color='gray')

        self.canvas.draw()
```

**与上个项目 `_redraw` 的主要区别**：
- 分两层画：先画原始（浅蓝色背景），再画压缩结果（红线+绿点+灰×）叠在上面
- `self.compressed` 标志控制是否显示压缩结果层
- 丢弃的点用 `marker='x'` 灰色叉号，直观表示"被删除"
- 加了 `legend` 图例帮助区分
- 标题显示压缩统计

---

### Block 12: ε 滑块联动

```python
    def _on_epsilon_change(self, value):
        """
        ε 滑块值变化时的回调。
        如果已经执行过压缩，自动重新压缩并更新显示。

        参数:
            value: str —— Scale 控件传来的当前值（字符串格式）
                   实际上我们不需要用这个参数，
                   因为 self.epsilon (DoubleVar) 已经自动更新了。
        """
        if self.compressed:
            # 已经压缩过 → 用新的 ε 重新压缩
            self.run_compression()
        # 如果还没压缩过，滑块变化不触发任何动作（等用户点"压缩"按钮）
```

**要点**：
- Scale 的 `command` 回调**必须接收一个参数**（当前值的字符串），即使你不用它
- 这里只在 `self.compressed == True` 时才重新压缩——避免用户还没采完点就触发
- 效果：滑块一拖动，画面实时更新压缩结果（非常直观）

---

### Block 13: 连线功能

```python
    def connect_lines(self):
        """连线"""
        if len(self.points) < 2:
            messagebox.showwarning("提示", "至少需要 2 个点才能连线！")
            return
        self.lines_visible = True
        self._redraw()
        self._update_status("已连线 | 点击 [🔍压缩] 或拖动 e 滑块")
```

**与上个项目完全相同。**

---

### Block 14: 清空重置

```python
    def clear_all(self):
        """清空所有数据"""
        if self.points:
            if not messagebox.askyesno("确认", "确定清空所有数据？"):
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
```

**与上个项目相比**，多清理了 `simplified` 和 `kept_indices`。

---

### Block 15: 导入坐标文件

```python
    def import_points(self):
        """从 CSV 文件导入坐标"""
        filepath = filedialog.askopenfilename(
            title="选择坐标文件",
            filetypes=[("CSV 文件", "*.csv"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialdir="."
        )
        if not filepath:
            return

        try:
            new_points = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row or row[0].strip().startswith('#'):
                        continue
                    try:
                        x = float(row[0].strip())
                        y = float(row[1].strip())
                        new_points.append((x, y))
                    except (ValueError, IndexError):
                        continue

            if not new_points:
                messagebox.showwarning("提示", "文件中没有有效坐标！")
                return

            self.points = new_points
            self.lines_visible = False
            self.compressed = False
            self.simplified.clear()
            self.kept_indices.clear()

            # 自动调整坐标轴
            xs, ys = zip(*self.points)
            margin = max((max(xs)-min(xs))*0.15, (max(ys)-min(ys))*0.15, 0.5)
            self.ax.set_xlim(min(xs)-margin, max(xs)+margin)
            self.ax.set_ylim(min(ys)-margin, max(ys)+margin)

            self._redraw()
            self._update_status(f"已导入 {len(self.points)} 个点")
            messagebox.showinfo("导入成功", f"导入 {len(self.points)} 个点")

        except Exception as e:
            messagebox.showerror("导入失败", f"出错:\n{e}")
```

**与上个项目基本相同**，多了清理压缩结果的两行。

---

### Block 16: 导出结果

```python
    def export_results(self):
        """导出压缩结果"""
        if not self.points:
            messagebox.showwarning("提示", "没有数据！")
            return

        filepath = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv")],
            initialfile="dp_result.csv"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['点序号', 'X', 'Y', '状态'])

                kept_set = set(self.kept_indices) if self.compressed else set()
                for i, (x, y) in enumerate(self.points):
                    if not self.compressed:
                        status = '未压缩'
                    elif i in kept_set:
                        status = '保留'
                    else:
                        status = '丢弃'
                    writer.writerow([f'P{i+1}', f'{x:.4f}', f'{y:.4f}', status])

            self._update_status(f"已导出到 {filepath}")
            messagebox.showinfo("导出成功", f"已保存到:\n{filepath}")
        except Exception as e:
            messagebox.showerror("导出失败", f"出错:\n{e}")
```

---

### Block 17: 程序入口

```python
def main():
    root = tk.Tk()
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    app = DPApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
```

---

## 4. 坐标文件格式

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

## 5. 手算验证练习

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

## 6. 思考题

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

> 📌 写完代码后，把 `dp_app.py` 和 `sample_coastline.csv` 放在本目录下提交到仓库。
