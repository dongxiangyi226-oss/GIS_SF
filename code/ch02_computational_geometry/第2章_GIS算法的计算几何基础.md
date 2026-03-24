# 第 2 章 GIS 算法的计算几何基础

> 本章是 GIS 空间分析的数学根基。从最基本的向量运算出发，逐步构建出
> 点/线/面/矩形/圆之间的**包含判断、相交判断、交点计算、几何构造**等完整算法体系。

---

## 📖 目录

- [2.1 维数扩展的 9 交集模型](#21-维数扩展的-9-交集模型)
- [2.2 矢量的概念](#22-矢量的概念)
- [2.3 折线段的拐向判断](#23-折线段的拐向判断)
- [2.4 判断点是否在线段上](#24-判断点是否在线段上)
- [2.5 判断两线段是否相交](#25-判断两线段是否相交)
- [2.6 判断矩形是否包含点](#26-判断矩形是否包含点)
- [2.7 判断线段、折线、多边形是否在矩形中](#27-判断线段折线多边形是否在矩形中)
- [2.8 判断矩形是否在矩形中](#28-判断矩形是否在矩形中)
- [2.9 判断圆是否在矩形中](#29-判断圆是否在矩形中)
- [2.10 判断点是否在多边形内](#210-判断点是否在多边形内)
  - [2.10.1 射线法](#2101-射线法)
  - [2.10.2 转角法](#2102-转角法)
- [2.11 判断线段是否在多边形内](#211-判断线段是否在多边形内)
- [2.12 判断折线是否在多边形内](#212-判断折线是否在多边形内)
- [2.13 判断多边形是否在多边形内](#213-判断多边形是否在多边形内)
- [2.14 判断矩形是否在多边形内](#214-判断矩形是否在多边形内)
- [2.15 判断圆是否在多边形内](#215-判断圆是否在多边形内)
- [2.16 判断点是否在圆内](#216-判断点是否在圆内)
- [2.17 判断线段、折线、矩形、多边形是否在圆内](#217-判断线段折线矩形多边形是否在圆内)
- [2.18 判断圆是否在圆内](#218-判断圆是否在圆内)
- [2.19 计算两条共线的线段的交点](#219-计算两条共线的线段的交点)
- [2.20 计算线段或直线与线段的交点](#220-计算线段或直线与线段的交点)
- [2.21 求线段或直线与圆的交点](#221-求线段或直线与圆的交点)
- [2.22 中心点的计算](#222-中心点的计算)
- [2.23 过点作垂线](#223-过点作垂线)
- [2.24 作平行线](#224-作平行线)
- [2.25 过点作平行线](#225-过点作平行线)
- [2.26 线段延长](#226-线段延长)
- [2.27 三点画圆](#227-三点画圆)
- [2.28 线段打断](#228-线段打断)
- [2.29 前方交会](#229-前方交会)
- [2.30 距离交会](#230-距离交会)
- [2.31 极坐标作点](#231-极坐标作点)
- [思考题](#思考题)

---

## 🏗️ 代码模块结构说明

本章所有算法的代码实现都围绕现有的三个文件展开：

```
GIS_SF/
├── turning_algo.py    ← 算法模块：所有几何计算函数都添加到这里
├── turning_plot.py    ← 绘图模块：可视化渲染方法添加到 CanvasWidget 类中
└── zxpd1.py           ← 主程序：GUI 交互、按钮、业务流程添加到 TurningApp 类中
```

**修改原则：**

| 文件 | 职责 | 添加什么 |
|------|------|---------|
| `turning_algo.py` | 纯数学计算，不依赖任何 UI | 每个算法对应一个函数，如 `point_on_segment()`, `segments_intersect()` 等 |
| `turning_plot.py` | Matplotlib 绑定的绘图逻辑 | 在 `CanvasWidget` 中添加绘制方法，如 `_draw_rectangle()`, `_draw_circle()` 等 |
| `zxpd1.py` | Tkinter GUI 和业务协调 | 在 `TurningApp` 中添加按钮、菜单和事件处理 |

**在 `turning_algo.py` 头部添加依赖：**

```python
# turning_algo.py 顶部（已有 import csv，新增 math）
import csv
import math
```

---

## 2.1 维数扩展的 9 交集模型

### 问题背景

GIS 中两个空间对象之间的**拓扑关系**（相离、相邻、相交、包含……）需要一个
严密的数学模型来描述和分类。Egenhofer 提出的 **DE-9IM**
（Dimensionally Extended 9-Intersection Model）正是这一基础。

### 基本概念

任何空间对象 A 都可以分解为三个部分：

| 符号 | 名称 | 含义 |
|:----:|------|------|
| A° | 内部（Interior） | 对象的"里面"，不含边界 |
| ∂A | 边界（Boundary） | 对象的边缘 |
| Aᵉ | 外部（Exterior） | 对象之外的所有空间 |

不同维度对象的分解方式：

```
点 P ：  内部 = P 本身      边界 = 空集       外部 = 平面 - {P}
线段 L： 内部 = 线段去端点   边界 = 两个端点    外部 = 平面 - L
多边形： 内部 = 面积部分     边界 = 围成的环    外部 = 平面 - 多边形
```

### 9 交集矩阵

两个对象 A、B 的空间关系用一个 **3×3 矩阵** 描述：

```
         B°       ∂B       Bᵉ
      ┌────────┬────────┬────────┐
  A°  │ A°∩B°  │ A°∩∂B  │ A°∩Bᵉ │
      ├────────┼────────┼────────┤
  ∂A  │ ∂A∩B°  │ ∂A∩∂B  │ ∂A∩Bᵉ │
      ├────────┼────────┼────────┤
  Aᵉ  │ Aᵉ∩B° │ Aᵉ∩∂B │ Aᵉ∩Bᵉ │
      └────────┴────────┴────────┘
```

矩阵中每个元素取值为交集的**最高维数**：
- `-1` 或 `F`（False）：空集
- `0`：交集是点
- `1`：交集是线
- `2`：交集是面
- `T`（True）：非空（不关心具体维数）
- `*`：任意（不做约束）

### 八种基本拓扑关系

| 关系 | 含义 | 9IM 特征（简化） |
|------|------|-----------------|
| 相离（Disjoint） | 无公共点 | A°∩B° = F, ∂A∩∂B = F |
| 相接（Touches） | 仅边界接触 | A°∩B° = F, ∂A∩∂B ≠ F |
| 交叉（Crosses） | 穿过但不完全重叠 | 内部相交，维度降低 |
| 重叠（Overlaps） | 部分重叠，同维度 | A°∩B° ≠ F |
| 包含（Contains） | B 完全在 A 内 | B°⊂A°, B 不碰 Aᵉ |
| 被包含（Within） | A 完全在 B 内 | Contains 的逆 |
| 相等（Equals） | 完全重合 | A = B |
| 覆盖（Covers） | A 覆盖 B | B 在 A 内，边界可接触 |

### GIS 应用

DE-9IM 是 OGC 标准中空间谓词（`ST_Intersects`、`ST_Contains`、`ST_Within` 等）的
理论基础。后续各节的包含判断算法，本质上都是在计算 9 交集矩阵的特定元素。

### 代码实现 — `turning_algo.py` 中添加

DE-9IM 本身是理论模型，我们用一个简单的数据结构来表示 9IM 矩阵：

```python
# ── DE-9IM 拓扑关系描述（添加到 turning_algo.py）──────────────────────

def de9im_matrix(interior, boundary, exterior):
    """
    构造 DE-9IM 矩阵的字符串表示。

    参数:
        interior, boundary, exterior: 各为长度 3 的字符串，
        每个字符取 'T','F','0','1','2','*'
    返回:
        9 字符的 DE-9IM 字符串，如 'T*F**FFF*' 表示 Contains

    用法示例:
        >>> de9im_matrix('T*F', '**F', 'FF*')
        'T*F**FFF*'
    """
    return interior + boundary + exterior


def de9im_matches(matrix_str, pattern):
    """
    检查一个 DE-9IM 矩阵是否匹配给定模式。

    参数:
        matrix_str: 9 字符 DE-9IM 字符串，如 'FF2F01FF2'
        pattern:    9 字符模式串，如 'T*F**FFF*'
    返回:
        bool

    匹配规则:
        'T' 匹配 '0','1','2'（非空）
        'F' 匹配 'F'（空集）
        '*' 匹配任意
        '0','1','2' 精确匹配
    """
    for m, p in zip(matrix_str, pattern):
        if p == '*':
            continue
        if p == 'T' and m in ('0', '1', '2'):
            continue
        if p == 'F' and m == 'F':
            continue
        if p == m:
            continue
        return False
    return True


# 八种拓扑关系的 DE-9IM 模式
DE9IM_PATTERNS = {
    'Disjoint':  'FF*FF****',
    'Touches':   'FT*******',   # 或 'F**T*****' 或 'F***T****'
    'Contains':  'T*****FF*',
    'Within':    'T*F**F***',
    'Equals':    'T*F**FFF*',
    'Crosses':   'T*T******',   # 线-线交叉
    'Overlaps':  'T*T***T**',   # 同维重叠
}
```

> **教学说明**：DE-9IM 在本章后续算法中是理论基础，不直接参与绘图。
> `turning_plot.py` 和 `zxpd1.py` 暂无需修改。

---

## 2.2 矢量的概念

### 定义

矢量（向量）是一个既有**大小**又有**方向**的量。在二维平面中用有序数对表示：

```
→
v = (vₓ, v_y)
```

由起点 A(x₁, y₁) 到终点 B(x₂, y₂) 构造的向量：

```
→
AB = (x₂ - x₁,  y₂ - y₁)
```

### 基本运算

**向量加法**：

```
→   →
a + b = (aₓ + bₓ,  a_y + b_y)
```

**数乘**：

```
    →
k · a = (k·aₓ,  k·a_y)
```

**向量模（长度）**：

```
→
|a| = √(aₓ² + a_y²)
```

### 点积（内积 / 数量积）

```
→   →
a · b = aₓ·bₓ + a_y·b_y = |a|·|b|·cos θ
```

| 点积值 | 含义 |
|:------:|------|
| `> 0` | 夹角 θ < 90°（同向） |
| `= 0` | θ = 90°（**垂直**） |
| `< 0` | θ > 90°（反向） |

应用：判断垂直、求投影长度、计算夹角。

### 代码实现 — `turning_algo.py` 中添加向量基础函数

```python
# ── 向量基础运算（添加到 turning_algo.py）──────────────────────────────

def vec(a, b):
    """从点 a 到点 b 的向量"""
    return (b[0] - a[0], b[1] - a[1])


def vec_add(u, v):
    """向量加法"""
    return (u[0] + v[0], u[1] + v[1])


def vec_scale(k, v):
    """数乘 k·v"""
    return (k * v[0], k * v[1])


def vec_length(v):
    """向量的模（长度）"""
    return math.sqrt(v[0] ** 2 + v[1] ** 2)


def vec_unit(v):
    """单位向量（归一化）"""
    length = vec_length(v)
    if length < 1e-15:
        return (0.0, 0.0)
    return (v[0] / length, v[1] / length)


def dot(u, v):
    """点积（内积）"""
    return u[0] * v[0] + u[1] * v[1]


def cross2d(u, v):
    """二维叉积（返回标量）"""
    return u[0] * v[1] - u[1] * v[0]


def vec_normal(v):
    """法向量（逆时针旋转 90°）"""
    return (-v[1], v[0])
```

> **教学说明**：这些是整个项目最核心的"工具函数"。后续所有算法都会调用
> `vec()`, `dot()`, `cross2d()`, `vec_unit()` 等。现有的 `cross_product()` 函数
> 内部逻辑与 `cross2d()` 等价，但新的函数更加通用和模块化。

### 叉积（外积 / 向量积）

二维叉积返回一个**标量**（实际是三维叉积的 z 分量）：

```
→   →
a × b = aₓ·b_y - a_y·bₓ = |a|·|b|·sin θ
```

| 叉积值 | 含义 |
|:------:|------|
| `> 0` | b 在 a 的**逆时针方向**（左转） |
| `= 0` | a 与 b **共线**（平行） |
| `< 0` | b 在 a 的**顺时针方向**（右转） |

几何意义：叉积的绝对值等于以 a、b 为边的**平行四边形面积**。

### 单位向量与法向量

**单位向量**（归一化）：

```
→      →     →
â = a / |a| = (aₓ/|a|,  a_y/|a|)
```

**法向量**（垂直于原向量）：

```
→                     →
a = (aₓ, a_y)  →  n = (-a_y, aₓ)    （逆时针旋转 90°）
                    →
                或  n = (a_y, -aₓ)    （顺时针旋转 90°）
```

---

## 2.3 折线段的拐向判断

### 问题

给定折线上连续三点 P₁、P₂、P₃，判断在 P₂ 处的行进方向是左转、右转还是直行。

### 算法

构造两个向量并计算叉积：

```
→              →
a = P₂ - P₁    b = P₃ - P₂

cross = aₓ · b_y - a_y · bₓ
```

判断规则（数学坐标系，y 轴朝上）：

| cross | 拐向 |
|:-----:|------|
| `> 0` | **左转**（逆时针） |
| `< 0` | **右转**（顺时针） |
| `= 0` | **共线**（直行） |

### 图解

```
        P₃                      P₁
       ↗                          ↘
      /   cross > 0                 \   cross < 0
     /    左转 ↰                      \  右转 ↱
P₁ → → P₂                    P₃ ← ← P₂

        P₁ → → P₂ → → P₃
            cross = 0, 共线 →
```

### 浮点容差

计算机浮点运算有精度限制，引入容差 `ε = 10⁻¹⁰`：
- `cross > ε`：左转
- `cross < -ε`：右转
- `|cross| ≤ ε`：共线

### 应用

- 判断多边形的绕行方向（顶点顺/逆时针排列）
- 判断凸多边形（所有拐角同向）
- 是后续线段相交、点在多边形内等算法的基础工具

### 代码实现 — `turning_algo.py`（已有）

`turning_algo.py` 中 **已存在** `cross_product()` 和 `analyze_all()` 函数：

```python
# ── 已有代码，无需修改 ─────────────────────────────────────────────────

def cross_product(p1, p2, p3):
    """
    计算三点叉积，判断折线在 p2 处的拐向。
    返回: (cross_value, direction)
    """
    ax_ = p2[0] - p1[0];  ay_ = p2[1] - p1[1]
    bx_ = p3[0] - p2[0];  by_ = p3[1] - p2[1]
    cross = ax_ * by_ - ay_ * bx_
    eps = 1e-10
    if   cross >  eps: direction = "左转 ↰"
    elif cross < -eps: direction = "右转 ↱"
    else:              direction = "共线 →"
    return cross, direction


def analyze_all(points):
    """对折线所有内部顶点执行拐向分析。"""
    results = []
    for i in range(1, len(points) - 1):
        cross_val, direction = cross_product(
            points[i - 1], points[i], points[i + 1]
        )
        results.append({
            'index': i, 'cross_val': cross_val, 'direction': direction
        })
    return results
```

> **教学说明**：这两个函数已经实现并在 GUI 中正常工作。
> 后续§2.5跨立实验会复用 `cross_product()` 中的叉积逻辑。
> 可以用新的 `cross2d(vec(p1,p2), vec(p2,p3))` 得到相同结果。

---

## 2.4 判断点是否在线段上

### 问题

给定点 Q 和线段 P₁P₂，判断 Q 是否在线段 P₁P₂ 上。

### 算法（两步法）

**第一步：共线检验**

计算 P₁Q 和 P₁P₂ 的叉积，若为零则三点共线：

```
→              →
a = Q - P₁     b = P₂ - P₁

cross = aₓ · b_y - a_y · bₓ

若 |cross| > ε → Q 不在直线 P₁P₂ 上 → 不在线段上
```

**第二步：范围检验**

共线只说明 Q 在直线上，还需确认 Q 在线段的端点之间：

```
min(P₁.x, P₂.x) ≤ Q.x ≤ max(P₁.x, P₂.x)
    且
min(P₁.y, P₂.y) ≤ Q.y ≤ max(P₁.y, P₂.y)
```

两步都满足 → Q 在线段 P₁P₂ 上。

### 图解

```
          Q₁ (叉积≠0，不共线 → 不在线段上)
         ·
P₁ ───Q₂──── P₂    Q₂ 叉积=0，且在范围内 → ✅ 在线段上
                Q₃  Q₃ 叉积=0，但超出范围 → ❌ 在直线上，不在线段上
```

### 等价方法：参数法

也可用参数 t 判断：

```
→           →
Q = P₁ + t·(P₂ - P₁)

解 t：若 0 ≤ t ≤ 1，则 Q 在线段上
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.4 判断点是否在线段上（添加到 turning_algo.py）─────────────────

def point_on_segment(q, p1, p2, eps=1e-10):
    """
    判断点 q 是否在线段 p1p2 上。

    参数:
        q, p1, p2: tuple (x, y)
        eps: 浮点容差
    返回:
        bool
    """
    # 第一步：共线检验（叉积为 0）
    cross = cross2d(vec(p1, q), vec(p1, p2))
    if abs(cross) > eps:
        return False

    # 第二步：范围检验（q 在 p1p2 的包围盒内）
    if q[0] < min(p1[0], p2[0]) - eps or q[0] > max(p1[0], p2[0]) + eps:
        return False
    if q[1] < min(p1[1], p2[1]) - eps or q[1] > max(p1[1], p2[1]) + eps:
        return False
    return True
```

### 如何在 GUI 中使用 — `zxpd1.py` 修改思路

如果想在 GUI 中实现"点击判断点是否在某条线段上"的功能：

```python
# zxpd1.py 中：
# 1. 在文件顶部的导入行中添加 point_on_segment
from turning_algo import analyze_all, load_points, save_results, point_on_segment

# 2. 在 TurningApp 类中添加一个新方法
def check_point_on_segment(self):
    """检查最后采集的点是否在第一条线段上"""
    if len(self.points) < 3:
        messagebox.showwarning("提示", "至少需要 3 个点（2个定线段 + 1个待判断）")
        return
    p1, p2 = self.points[0], self.points[1]
    q = self.points[-1]     # 最后一个点作为待判断点
    result = point_on_segment(q, p1, p2)
    msg = f"点 ({q[0]:.2f}, {q[1]:.2f}) "
    msg += "在线段上 ✅" if result else "不在线段上 ❌"
    messagebox.showinfo("判断结果", msg)

# 3. 在 _build_toolbar() 中添加按钮
# tk.Button(toolbar, text='📌 点在线段?', command=self.check_point_on_segment, **btn_cfg).pack(side=tk.LEFT, padx=2)
```

---

## 2.5 判断两线段是否相交

### 问题

给定线段 P₁P₂ 和线段 Q₁Q₂，判断它们是否相交。

### 算法：跨立实验（Straddle Test）

两线段相交的充要条件是**互相跨立**：

**条件一：Q₁Q₂ 跨立 P₁P₂ 所在直线**

```
d₁ = cross(P₁P₂, P₁Q₁)     ← Q₁ 在 P₁P₂ 的哪一侧
d₂ = cross(P₁P₂, P₁Q₂)     ← Q₂ 在 P₁P₂ 的哪一侧

若 d₁ · d₂ < 0 → Q₁Q₂ 跨立 P₁P₂（两点在直线两侧）
若 d₁ · d₂ = 0 → 有端点在直线上（边界情况）
```

**条件二：P₁P₂ 跨立 Q₁Q₂ 所在直线**

```
d₃ = cross(Q₁Q₂, Q₁P₁)
d₄ = cross(Q₁Q₂, Q₁P₂)

若 d₃ · d₄ < 0 → P₁P₂ 跨立 Q₁Q₂
```

**两个条件都满足 → 两线段相交。**

### 图解

```
     Q₁                    Q₁
      \   相交 ✅            |   不相交 ❌
P₁ ────×──── P₂    P₁ ────────── P₂
        \                   |
         Q₂                Q₂

Q₁,Q₂ 在 P₁P₂ 两侧 ✅   Q₁,Q₂ 在 P₁P₂ 同侧 ❌
P₁,P₂ 在 Q₁Q₂ 两侧 ✅
```

### 特殊情况处理

1. **端点在另一条线段上**（d₁·d₂ = 0）：需额外用 §2.4 判断点是否在线段上
2. **两线段共线**（所有叉积都为 0）：需判断投影区间是否重叠
3. **退化情况**（线段长度为 0）：退化为点，用 §2.4 判断

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.5 判断两线段是否相交（添加到 turning_algo.py）─────────────────

def segments_intersect(p1, p2, q1, q2, eps=1e-10):
    """
    判断线段 p1p2 与线段 q1q2 是否相交（跨立实验）。

    参数:
        p1, p2: 线段1的端点 (x, y)
        q1, q2: 线段2的端点 (x, y)
    返回:
        bool
    """
    # 计算四个叉积
    d1 = cross2d(vec(p1, p2), vec(p1, q1))   # q1 在 p1p2 的哪侧
    d2 = cross2d(vec(p1, p2), vec(p1, q2))   # q2 在 p1p2 的哪侧
    d3 = cross2d(vec(q1, q2), vec(q1, p1))   # p1 在 q1q2 的哪侧
    d4 = cross2d(vec(q1, q2), vec(q1, p2))   # p2 在 q1q2 的哪侧

    # 标准情况：互相跨立
    if d1 * d2 < -eps and d3 * d4 < -eps:
        return True

    # 边界情况：端点在另一条线段上
    if abs(d1) <= eps and point_on_segment(q1, p1, p2, eps):
        return True
    if abs(d2) <= eps and point_on_segment(q2, p1, p2, eps):
        return True
    if abs(d3) <= eps and point_on_segment(p1, q1, q2, eps):
        return True
    if abs(d4) <= eps and point_on_segment(p2, q1, q2, eps):
        return True

    return False


def segments_proper_intersect(p1, p2, q1, q2, eps=1e-10):
    """
    判断两线段是否"规范相交"（在各自内部有交点，不含端点接触）。
    后续 §2.11 判断线段是否在多边形内时会用到。
    """
    d1 = cross2d(vec(p1, p2), vec(p1, q1))
    d2 = cross2d(vec(p1, p2), vec(p1, q2))
    d3 = cross2d(vec(q1, q2), vec(q1, p1))
    d4 = cross2d(vec(q1, q2), vec(q1, p2))
    return d1 * d2 < -eps and d3 * d4 < -eps
```

### 如何在 GUI 中使用 — `zxpd1.py` 修改思路

```python
# zxpd1.py 中添加：
from turning_algo import (analyze_all, load_points, save_results,
                          point_on_segment, segments_intersect)

# 在 TurningApp 类中添加：
def check_intersection(self):
    """检查前两条线段是否相交（需要至少4个点）"""
    if len(self.points) < 4:
        messagebox.showwarning("提示", "至少需要 4 个点（P1P2 和 P3P4 两条线段）")
        return
    p1, p2 = self.points[0], self.points[1]
    q1, q2 = self.points[2], self.points[3]
    result = segments_intersect(p1, p2, q1, q2)
    msg = "两线段相交 ✅" if result else "两线段不相交 ❌"
    messagebox.showinfo("相交判断", msg)
```

### 如何可视化 — `turning_plot.py` 修改思路

```python
# turning_plot.py 的 CanvasWidget 类中添加：
def draw_two_segments(self, p1, p2, q1, q2, intersects):
    """绘制两条线段，用颜色标记是否相交"""
    color = '#2E7D32' if intersects else '#C62828'  # 绿=相交, 红=不相交
    self._ax.plot([p1[0], p2[0]], [p1[1], p2[1]], '-o', color='#1565C0', linewidth=2)
    self._ax.plot([q1[0], q2[0]], [q1[1], q2[1]], '-o', color='#E65100', linewidth=2)
    # 在交点或中心位置显示结果文字
    cx = (p1[0] + p2[0] + q1[0] + q2[0]) / 4
    cy = (p1[1] + p2[1] + q1[1] + q2[1]) / 4
    label = "相交 ✅" if intersects else "不相交 ❌"
    self._ax.annotate(label, (cx, cy), fontsize=12, fontweight='bold',
                      color=color, ha='center')
```

---

## 2.6 判断矩形是否包含点

### 问题

给定轴对齐矩形 R = (xmin, ymin, xmax, ymax) 和点 Q(x, y)，判断 Q 是否在 R 内。

### 算法

```
Q 在 R 内 ⟺ xmin ≤ Q.x ≤ xmax  且  ymin ≤ Q.y ≤ ymax
```

### 边界约定

| 约定 | 条件 |
|------|------|
| 包含边界（闭区间） | `≤` |
| 不含边界（开区间） | `<` |
| 含左下不含右上 | 左下 `≤`，右上 `<`（某些GIS系统的约定） |

### 图解

```
         xmin         xmax
    ymax  ┌───────────┐
          │  Q₁ ✅    │  Q₂ ❌
          │           │
    ymin  └───────────┘
            Q₃ ❌
```

### GIS 应用

这是空间查询中最基本最高效的过滤操作。在 R 树索引中，
每个节点的 MBR（最小外接矩形）都用这个判断做**粗过滤**。

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.6 判断矩形是否包含点（添加到 turning_algo.py）─────────────────

def rect_contains_point(rect, q):
    """
    判断轴对齐矩形是否包含点。

    参数:
        rect: (xmin, ymin, xmax, ymax)
        q:    (x, y)
    返回:
        bool
    """
    xmin, ymin, xmax, ymax = rect
    return xmin <= q[0] <= xmax and ymin <= q[1] <= ymax
```

---

## 2.7 判断线段、折线、多边形是否在矩形中

### 通用原则

**线段 P₁P₂ 在矩形 R 内**的条件：

```
P₁ 在 R 内  且  P₂ 在 R 内
```

注意：这对凸区域（矩形是凸的）成立——线段两端点都在凸区域内，
则整个线段都在内。

**折线在矩形内**的条件：

```
折线的所有顶点都在 R 内
```

同理，每条子线段的两个端点都在 R 内。

**多边形在矩形内**的条件：

```
多边形的所有顶点都在 R 内
```

因为矩形是凸的，所有顶点在内就保证所有边和面积部分都在内。

### 关键推论

> 对于**凸包含区域**，"所有顶点在内"是几何对象在内的充要条件。
> 这一结论对矩形成立，但对凹多边形**不成立**（见 §2.11）。

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.7 判断线段/折线/多边形是否在矩形中（添加到 turning_algo.py）───

def segment_in_rect(rect, p1, p2):
    """线段 p1p2 是否完全在矩形内（两端点都在内即可）"""
    return rect_contains_point(rect, p1) and rect_contains_point(rect, p2)


def polyline_in_rect(rect, points):
    """折线的所有顶点是否都在矩形内"""
    return all(rect_contains_point(rect, p) for p in points)


def polygon_in_rect(rect, vertices):
    """多边形的所有顶点是否都在矩形内（矩形是凸的，顶点在内即整体在内）"""
    return all(rect_contains_point(rect, v) for v in vertices)
```

---

## 2.8 判断矩形是否在矩形中

### 问题

给定外矩形 R₁ = (xmin₁, ymin₁, xmax₁, ymax₁)
和内矩形 R₂ = (xmin₂, ymin₂, xmax₂, ymax₂)，
判断 R₂ 是否完全在 R₁ 内。

### 算法

```
R₂ ⊂ R₁ ⟺ xmin₁ ≤ xmin₂  且  xmax₂ ≤ xmax₁
            且  ymin₁ ≤ ymin₂  且  ymax₂ ≤ ymax₁
```

等价于：R₂ 的四个角点都在 R₁ 内。但直接比较四个边界值更高效（4 次比较 vs 8 次比较）。

### 图解

```
R₁  ┌─────────────────┐
    │                 │
    │   R₂ ┌─────┐   │   ✅ R₂ ⊂ R₁
    │      │     │   │
    │      └─────┘   │
    └─────────────────┘

R₁  ┌─────────────┐
    │          ┌──┼──┐   ❌ R₂ 超出 R₁
    │          │  │  │
    └──────────┼──┘  │
               └─────┘ R₂
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.8 判断矩形是否在矩形中（添加到 turning_algo.py）───────────────

def rect_in_rect(outer, inner):
    """
    判断内矩形 inner 是否完全在外矩形 outer 内。

    参数:
        outer: (xmin1, ymin1, xmax1, ymax1)
        inner: (xmin2, ymin2, xmax2, ymax2)
    返回:
        bool
    """
    return (outer[0] <= inner[0] and inner[2] <= outer[2] and
            outer[1] <= inner[1] and inner[3] <= outer[3])
```

---

## 2.9 判断圆是否在矩形中

### 问题

给定轴对齐矩形 R = (xmin, ymin, xmax, ymax) 和
圆 C（圆心 O(cx, cy)，半径 r），判断 C 是否完全在 R 内。

### 算法

```
C ⊂ R ⟺ cx - r ≥ xmin   （圆的最左点不超出左边界）
         且 cx + r ≤ xmax   （圆的最右点不超出右边界）
         且 cy - r ≥ ymin   （圆的最低点不超出下边界）
         且 cy + r ≤ ymax   （圆的最高点不超出上边界）
```

等价于：圆心到矩形四条边的距离都 ≥ r。

### 图解

```
         xmin              xmax
    ymax  ┌──────────────────┐
          │                  │
          │    ╭──╮          │
          │    │ O│  ← 圆心   │   检查圆心到四边的距离是否都 ≥ r
          │    ╰──╯          │
    ymin  └──────────────────┘
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.9 判断圆是否在矩形中（添加到 turning_algo.py）─────────────────

def circle_in_rect(rect, center, radius):
    """
    判断圆是否完全在轴对齐矩形内。

    参数:
        rect:   (xmin, ymin, xmax, ymax)
        center: (cx, cy) 圆心坐标
        radius: float 半径
    返回:
        bool
    """
    xmin, ymin, xmax, ymax = rect
    cx, cy = center
    return (cx - radius >= xmin and cx + radius <= xmax and
            cy - radius >= ymin and cy + radius <= ymax)
```

### 如何在 GUI 中可视化矩形和圆 — `turning_plot.py` 修改思路

```python
# turning_plot.py 的 CanvasWidget 类中添加绘制方法：

import matplotlib.patches as patches   # 文件顶部添加

# 在 CanvasWidget 类中添加：
def draw_rect(self, rect, color='#1565C0', label=None):
    """绘制轴对齐矩形"""
    xmin, ymin, xmax, ymax = rect
    width, height = xmax - xmin, ymax - ymin
    r = patches.Rectangle((xmin, ymin), width, height,
                           linewidth=2, edgecolor=color,
                           facecolor=color, alpha=0.1)
    self._ax.add_patch(r)
    if label:
        self._ax.text(xmin + width/2, ymax + 1, label,
                      ha='center', fontsize=9, color=color)

def draw_circle(self, center, radius, color='#E65100', label=None):
    """绘制圆"""
    c = patches.Circle(center, radius,
                       linewidth=2, edgecolor=color,
                       facecolor=color, alpha=0.1)
    self._ax.add_patch(c)
    if label:
        self._ax.text(center[0], center[1] + radius + 1, label,
                      ha='center', fontsize=9, color=color)
```

---

## 2.10 判断点是否在多边形内

这是计算几何中最经典的问题之一，有两种主流算法。

---

### 2.10.1 射线法

#### 原理

从待判断点 Q 向任意方向发出一条射线（通常取水平向右），
计算射线与多边形各边的**交点个数**：

```
交点个数为奇数 → Q 在多边形内
交点个数为偶数 → Q 在多边形外
```

这就是 **Jordan 曲线定理**的离散应用。

#### 图解

```
        ┌──────────┐
        │          │
  Q₁ ─ ─│─ ─ ─ ─ ─│─ → →    穿过 2 条边（偶数）→ Q₁ 在外
        │          │
        │  Q₂ ─ ─ ─│─ → →    穿过 1 条边（奇数）→ Q₂ 在内
        │          │
        └──────────┘
```

#### 算法步骤

```
输入: Q(x, y), 多边形顶点 V₁V₂...Vₙ（首尾不重复，隐含 Vₙ→V₁ 的闭合边）
count = 0

对每条边 VᵢVᵢ₊₁:
    1. 判断 Q.y 是否在边的 y 范围内（min(Vᵢ.y, Vᵢ₊₁.y) ≤ Q.y < max(...)）
    2. 若在范围内，计算射线（Q 水平向右）与该边所在直线的交点 x 坐标
    3. 若交点 x > Q.x（在 Q 右侧），count += 1

若 count 为奇数 → Q 在多边形内
```

#### 特殊情况

1. **射线过多边形顶点**：统一规则——射线经过的顶点只在边的"上端点"处计数，
   "下端点"不计数（即 y 范围取半开区间 `[ymin, ymax)`）
2. **点在多边形边上**：叉积为 0 且在线段范围内 → 视为边界，按需定义在内/在外
3. **凹多边形完全适用**：这是射线法的优势

#### 代码实现 — `turning_algo.py` 中添加（射线法）

```python
# ── §2.10.1 射线法：判断点是否在多边形内（添加到 turning_algo.py）────

def point_in_polygon_ray(q, polygon):
    """
    射线法判断点 q 是否在多边形内（水平向右发射线）。

    参数:
        q:       (x, y) 待判断点
        polygon: [(x1,y1), (x2,y2), ...] 多边形顶点（不需首尾重复）
    返回:
        bool  True=在内部, False=在外部
    """
    x, y = q
    n = len(polygon)
    count = 0

    for i in range(n):
        # 当前边: polygon[i] → polygon[(i+1) % n]
        x1, y1 = polygon[i]
        x2, y2 = polygon[(i + 1) % n]

        # 判断 q.y 是否在边的 y 范围内（半开区间 [ymin, ymax)）
        if y1 <= y < y2 or y2 <= y < y1:
            # 计算射线与该边所在直线的交点的 x 坐标
            x_intersect = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            # 交点在 q 右侧则计数
            if x_intersect > x:
                count += 1

    return count % 2 == 1   # 奇数=在内
```

---

### 2.10.2 转角法

#### 原理

以点 Q 为观察点，沿多边形边界走一圈，计算多边形边界绕 Q 转过的**总角度**：

```
总转角 = ±2π → Q 在多边形内
总转角 = 0   → Q 在多边形外
```

#### 计算方法

对每条边 VᵢVᵢ₊₁，计算从 Q 看去的张角：

```
→                →
a = Vᵢ - Q       b = Vᵢ₊₁ - Q

θᵢ = atan2(a × b, a · b)      ← 带符号的夹角

总转角 W = Σ θᵢ
```

转角数（Winding Number）= `W / (2π)`：
- `|转角数| = 1`：Q 在多边形内
- `转角数 = 0`：Q 在多边形外

#### 射线法 vs 转角法

| | 射线法 | 转角法 |
|--|--------|--------|
| 原理 | 交点计数 | 角度累加 |
| 实现难度 | 较简单 | 需要 atan2 |
| 特殊情况 | 顶点/边上需特殊处理 | 自然处理 |
| 自相交多边形 | 可能出错 | 正确处理 |
| 效率 | O(n) | O(n) |

一般情况推荐**射线法**（简单高效），自相交多边形用**转角法**。

#### 代码实现 — `turning_algo.py` 中添加（转角法）

```python
# ── §2.10.2 转角法：判断点是否在多边形内（添加到 turning_algo.py）────

def point_in_polygon_winding(q, polygon):
    """
    转角法（Winding Number）判断点 q 是否在多边形内。

    参数:
        q:       (x, y) 待判断点
        polygon: [(x1,y1), ...] 多边形顶点
    返回:
        bool  True=在内部
    """
    total_angle = 0.0
    n = len(polygon)

    for i in range(n):
        a = vec(q, polygon[i])
        b = vec(q, polygon[(i + 1) % n])

        # atan2(叉积, 点积) = 带符号的夹角
        cross = cross2d(a, b)
        d = dot(a, b)
        angle = math.atan2(cross, d)
        total_angle += angle

    # 转角数 = total_angle / (2π)，接近 ±1 则在内部
    winding_number = total_angle / (2 * math.pi)
    return abs(winding_number) > 0.5
```

### 如何在 GUI 中使用 — `zxpd1.py` 修改思路

```python
# zxpd1.py 中添加多边形内点判断功能：
from turning_algo import (..., point_in_polygon_ray)

# 在 TurningApp 类中：
def check_point_in_polygon(self):
    """最后一个点是否在前面点构成的多边形内"""
    if len(self.points) < 4:
        messagebox.showwarning("提示", "至少需要 4 个点（3个定多边形 + 1个待判断）")
        return
    polygon = self.points[:-1]   # 前 n-1 个点组成多边形
    q = self.points[-1]          # 最后一个点
    result = point_in_polygon_ray(q, polygon)
    msg = f"点 ({q[0]:.2f}, {q[1]:.2f}) "
    msg += "在多边形内 ✅" if result else "在多边形外 ❌"
    messagebox.showinfo("判断结果", msg)
```

### 可视化多边形 — `turning_plot.py` 修改思路

```python
# turning_plot.py 的 CanvasWidget 类中添加：
from matplotlib.patches import Polygon as MplPolygon

def draw_polygon(self, vertices, color='#1565C0', alpha=0.15):
    """绘制填充的多边形"""
    poly = MplPolygon(vertices, closed=True,
                      edgecolor=color, facecolor=color,
                      alpha=alpha, linewidth=2)
    self._ax.add_patch(poly)
```

---

## 2.11 判断线段是否在多边形内

### 问题

给定线段 P₁P₂ 和多边形 Poly，判断线段是否完全在多边形内部。

### 算法

与矩形不同，多边形可能是**凹的**，仅判断端点在内是不够的：

```
        ┌─────┐
        │     │
 P₁ ────│─────│──── P₂     端点都在内，但线段穿过了凹处！❌
        │     │
    ┌───┘     └───┐
    │             │
    └─────────────┘
```

### 正确条件（三条同时满足）

```
① P₁ 在多边形内（§2.10）
② P₂ 在多边形内（§2.10）
③ 线段 P₁P₂ 与多边形的任何一条边都不**规范相交**
   （允许端点相接，不允许穿过）
```

规范相交（Proper Intersection）：两线段在各自的内部有交点，不是端点处的接触。

### 算法步骤

```
1. 若 P₁ 或 P₂ 不在多边形内 → 返回 False
2. 对多边形的每条边 E：
       若 线段 P₁P₂ 与 E 规范相交 → 返回 False
3. 返回 True
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.11 判断线段是否在多边形内（添加到 turning_algo.py）─────────────

def segment_in_polygon(p1, p2, polygon):
    """
    判断线段 p1p2 是否完全在多边形内部。

    条件（三个同时满足）:
      ① p1 在多边形内
      ② p2 在多边形内
      ③ 线段与多边形任何边都不规范相交
    """
    if not point_in_polygon_ray(p1, polygon):
        return False
    if not point_in_polygon_ray(p2, polygon):
        return False

    n = len(polygon)
    for i in range(n):
        e1 = polygon[i]
        e2 = polygon[(i + 1) % n]
        if segments_proper_intersect(p1, p2, e1, e2):
            return False
    return True
```

---

## 2.12 判断折线是否在多边形内

### 算法

将折线拆解为多条线段，**每条子线段都在多边形内**即可：

```
折线 L₁L₂...Lₖ 在多边形内
⟺ 对每个 i，线段 LᵢLᵢ₊₁ 在多边形内（§2.11）
```

### 优化

- 先快速判断折线所有顶点是否在多边形内（§2.10），若有点在外则直接返回 False
- 再逐段判断是否与多边形边相交

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.12 判断折线是否在多边形内（添加到 turning_algo.py）─────────────

def polyline_in_polygon(polyline, polygon):
    """
    判断折线是否完全在多边形内。
    将折线拆为多条线段，每条都必须在多边形内。
    """
    for i in range(len(polyline) - 1):
        if not segment_in_polygon(polyline[i], polyline[i + 1], polygon):
            return False
    return True
```

---

## 2.13 判断多边形是否在多边形内

### 问题

给定多边形 A 和多边形 B，判断 A 是否完全在 B 内。

### 算法

```
多边形 A 在多边形 B 内
⟺ A 的所有顶点都在 B 内（§2.10）
  且 A 的任何边都不与 B 的任何边规范相交（§2.5）
```

### 注意

- 如果 B 是凸多边形，则只需判断 A 的所有顶点在 B 内即可
- 如果 B 是凹多边形，必须额外检查边的相交情况（与 §2.11 同理）

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.13 判断多边形是否在多边形内（添加到 turning_algo.py）───────────

def polygon_in_polygon(inner_poly, outer_poly):
    """
    判断多边形 inner_poly 是否完全在 outer_poly 内部。

    条件:
      ① inner_poly 的所有顶点都在 outer_poly 内
      ② inner_poly 的任何边都不与 outer_poly 的任何边规范相交
    """
    # 条件①：所有顶点在外多边形内
    for v in inner_poly:
        if not point_in_polygon_ray(v, outer_poly):
            return False

    # 条件②：边不规范相交
    n_in = len(inner_poly)
    n_out = len(outer_poly)
    for i in range(n_in):
        a1 = inner_poly[i]
        a2 = inner_poly[(i + 1) % n_in]
        for j in range(n_out):
            b1 = outer_poly[j]
            b2 = outer_poly[(j + 1) % n_out]
            if segments_proper_intersect(a1, a2, b1, b2):
                return False
    return True
```

---

## 2.14 判断矩形是否在多边形内

### 算法

矩形是特殊的多边形（4 个顶点），直接套用 §2.13：

```
矩形 R 在多边形 Poly 内
⟺ R 的 4 个角点都在 Poly 内（§2.10）
  且 R 的 4 条边都不与 Poly 的任何边规范相交（§2.5）
```

对凸多边形 Poly，四角点在内即可。

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.14 判断矩形是否在多边形内（添加到 turning_algo.py）─────────────

def rect_in_polygon(rect, polygon):
    """
    判断轴对齐矩形是否完全在多边形内。
    矩形是特殊的四边形，直接调用 polygon_in_polygon。

    参数:
        rect:    (xmin, ymin, xmax, ymax)
        polygon: [(x,y), ...] 多边形顶点
    """
    xmin, ymin, xmax, ymax = rect
    # 矩形的 4 个角点构成的多边形
    rect_poly = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    return polygon_in_polygon(rect_poly, polygon)
```

---

## 2.15 判断圆是否在多边形内

### 问题

给定圆 C（圆心 O，半径 r）和多边形 Poly，判断 C 是否完全在 Poly 内。

### 算法

```
圆 C 在多边形 Poly 内
⟺ ① 圆心 O 在 Poly 内（§2.10）
  且 ② O 到 Poly 每条边的距离 ≥ r
```

**点到线段的距离**计算方法：

```
给定点 Q 和线段 P₁P₂：

     →           →
t = (Q-P₁)·(P₂-P₁) / |P₂-P₁|²     ← 投影参数

若 t < 0：距离 = |Q - P₁|           ← 最近点是 P₁
若 t > 1：距离 = |Q - P₂|           ← 最近点是 P₂
若 0 ≤ t ≤ 1：
    投影点 H = P₁ + t·(P₂-P₁)
    距离 = |Q - H|                   ← 最近点是垂足
```

### 图解

```
    ┌───────────────┐
    │               │
    │    ╭───╮      │   圆心在内 ✅
    │    │ O │      │   O 到每条边的距离 ≥ r ✅
    │    ╰───╯      │   → 圆在多边形内 ✅
    └───────────────┘
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── 辅助函数：点到线段的距离（§2.15、§2.23 共用）─────────────────────

def point_to_segment_dist(q, p1, p2):
    """
    计算点 q 到线段 p1p2 的最短距离。
    原理：先求投影参数 t，再根据 t 确定最近点。
    """
    d = vec(p1, p2)
    len_sq = dot(d, d)
    if len_sq < 1e-20:          # 线段退化为点
        return vec_length(vec(p1, q))

    t = dot(vec(p1, q), d) / len_sq   # 投影参数

    if t < 0:                   # 最近点是 p1
        return vec_length(vec(p1, q))
    elif t > 1:                 # 最近点是 p2
        return vec_length(vec(p2, q))
    else:                       # 最近点是垂足 H
        h = vec_add(p1, vec_scale(t, d))   # H = p1 + t * d
        return vec_length(vec(h, q))


# ── §2.15 判断圆是否在多边形内（添加到 turning_algo.py）───────────────

def circle_in_polygon(center, radius, polygon):
    """
    判断圆是否完全在多边形内部。

    条件:
      ① 圆心在多边形内
      ② 圆心到多边形每条边的距离 ≥ r
    """
    if not point_in_polygon_ray(center, polygon):
        return False

    n = len(polygon)
    for i in range(n):
        e1 = polygon[i]
        e2 = polygon[(i + 1) % n]
        dist = point_to_segment_dist(center, e1, e2)
        if dist < radius - 1e-10:
            return False
    return True
```

---

## 2.16 判断点是否在圆内

### 算法

```
点 Q 在圆 C(O, r) 内
⟺ |Q - O| ≤ r
⟺ (Q.x - O.x)² + (Q.y - O.y)² ≤ r²
```

实际编程中，比较**距离的平方**与 **r²**，避免开方运算：

```
dx = Q.x - O.x
dy = Q.y - O.y
Q 在圆内 ⟺ dx² + dy² ≤ r²
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.16 判断点是否在圆内（添加到 turning_algo.py）───────────────────

def point_in_circle(q, center, radius):
    """
    判断点 q 是否在圆内（比较距离平方，避免开方）。

    参数:
        q:      (x, y) 待判断点
        center: (cx, cy) 圆心
        radius: float 半径
    返回:
        bool
    """
    dx = q[0] - center[0]
    dy = q[1] - center[1]
    return dx * dx + dy * dy <= radius * radius
```

---

## 2.17 判断线段、折线、矩形、多边形是否在圆内

### 通用原则

圆是**凸区域**，因此：

```
几何对象在圆内 ⟺ 该对象的所有顶点都在圆内
```

具体而言：

| 对象 | 条件 |
|------|------|
| 线段 P₁P₂ | P₁ 在圆内 且 P₂ 在圆内 |
| 折线 L₁...Lₖ | 所有顶点 Lᵢ 在圆内 |
| 矩形 R | R 的 4 个角点在圆内 |
| 多边形 Poly | 所有顶点在圆内 |

### 原理

因为圆是凸的，如果两个点都在圆内，则连接它们的线段也必然在圆内。
推广到多个点：所有顶点在圆内 → 凸包在圆内 → 更小的多边形必然在圆内。

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.17 判断几何对象是否在圆内（添加到 turning_algo.py）─────────────

def points_all_in_circle(points, center, radius):
    """判断一组点是否都在圆内（通用：线段、折线、矩形、多边形）"""
    return all(point_in_circle(p, center, radius) for p in points)


def segment_in_circle(p1, p2, center, radius):
    """线段在圆内 ⟺ 两端点都在圆内"""
    return point_in_circle(p1, center, radius) and point_in_circle(p2, center, radius)


def rect_in_circle(rect, center, radius):
    """矩形在圆内 ⟺ 四角点都在圆内"""
    xmin, ymin, xmax, ymax = rect
    corners = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    return points_all_in_circle(corners, center, radius)
```

---

## 2.18 判断圆是否在圆内

### 算法

给定外圆 C₁(O₁, r₁) 和内圆 C₂(O₂, r₂)：

```
C₂ 在 C₁ 内 ⟺ |O₁ - O₂| + r₂ ≤ r₁
```

即两圆心距 + 内圆半径 ≤ 外圆半径。

### 图解

```
        ╭───────────────╮
       ╱                 ╲
      ╱    ╭──╮           ╲
     │     │O₂│            │
     │     ╰──╯            │
     │          O₁         │
      ╲                   ╱
       ╲                 ╱
        ╰───────────────╯

    d = |O₁O₂|
    C₂ ⊂ C₁ ⟺ d + r₂ ≤ r₁
```

### 编程优化

避免开方：

```
d + r₂ ≤ r₁
→ d ≤ r₁ - r₂
→ d² ≤ (r₁ - r₂)²    （前提：r₁ ≥ r₂，否则直接返回 False）
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.18 判断圆是否在圆内（添加到 turning_algo.py）───────────────────

def circle_in_circle(c1_center, c1_radius, c2_center, c2_radius):
    """
    判断圆2(c2)是否完全在圆1(c1)内。

    条件: |O₁O₂| + r₂ ≤ r₁
    优化: 避免开方，用平方比较（前提 r₁ ≥ r₂）
    """
    if c1_radius < c2_radius:
        return False
    dx = c1_center[0] - c2_center[0]
    dy = c1_center[1] - c2_center[1]
    dist_sq = dx * dx + dy * dy
    return dist_sq <= (c1_radius - c2_radius) ** 2
```

---

## 2.19 计算两条共线的线段的交点

### 问题

已知两条线段 P₁P₂ 和 Q₁Q₂ **共线**（在同一直线上），求它们的重叠部分。

### 前提

两线段共线意味着 `cross(P₁P₂, P₁Q₁) = 0` 且 `cross(P₁P₂, P₁Q₂) = 0`。

### 算法

将两条线段投影到一维坐标轴上（选 x 轴或 y 轴，取较长的那个），
求区间交集：

```
线段1: 投影区间 [a₁, a₂]，确保 a₁ ≤ a₂
线段2: 投影区间 [b₁, b₂]，确保 b₁ ≤ b₂

重叠区间: [max(a₁,b₁), min(a₂,b₂)]

若 max(a₁,b₁) > min(a₂,b₂) → 无重叠
若 max(a₁,b₁) = min(a₂,b₂) → 重叠为一个点
若 max(a₁,b₁) < min(a₂,b₂) → 重叠为一段线段
```

### 图解

```
P₁ ─────────── P₂
        Q₁ ─────────── Q₂

重叠: Q₁ ────── P₂
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.19 计算两条共线线段的交点/重叠（添加到 turning_algo.py）────────

def collinear_overlap(p1, p2, q1, q2):
    """
    两条共线线段的重叠区间（假设已确认共线）。

    返回:
        None           → 无重叠
        (pt,)          → 重叠为一个点
        (pt_a, pt_b)   → 重叠为一段线段
    """
    # 选投影轴：取 x 或 y 中跨度更大的
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])

    if dx >= dy:   # 投影到 x 轴
        pts = sorted([(p1[0], p1), (p2[0], p2), (q1[0], q1), (q2[0], q2)])
    else:          # 投影到 y 轴
        pts = sorted([(p1[1], p1), (p2[1], p2), (q1[1], q1), (q2[1], q2)])

    # 排序后 [a, b, c, d]，重叠区间 = [b, c]（如果 b 属于两条线段各一个端点）
    # 更简单的方式：用区间交集
    if dx >= dy:
        a1, a2 = min(p1[0], p2[0]), max(p1[0], p2[0])
        b1, b2 = min(q1[0], q2[0]), max(q1[0], q2[0])
    else:
        a1, a2 = min(p1[1], p2[1]), max(p1[1], p2[1])
        b1, b2 = min(q1[1], q2[1]), max(q1[1], q2[1])

    lo = max(a1, b1)
    hi = min(a2, b2)

    eps = 1e-10
    if lo > hi + eps:
        return None              # 无重叠

    # 根据投影值反算坐标
    d = vec(p1, p2)
    length_sq = dot(d, d)
    if length_sq < 1e-20:
        return (p1,)

    t_lo = (lo - (p1[0] if dx >= dy else p1[1])) / (d[0] if dx >= dy else d[1])
    t_hi = (hi - (p1[0] if dx >= dy else p1[1])) / (d[0] if dx >= dy else d[1])

    pt_lo = vec_add(p1, vec_scale(t_lo, d))
    pt_hi = vec_add(p1, vec_scale(t_hi, d))

    if abs(lo - hi) < eps:
        return (pt_lo,)          # 重叠为一个点
    return (pt_lo, pt_hi)        # 重叠为线段
```

---

## 2.20 计算线段或直线与线段的交点

### 问题

给定线段（或直线）L 和线段 S，求交点。

### 算法：参数化求交

设线段 S 的两个端点为 P₁、P₂，另一条为 Q₁、Q₂。
用参数方程表示：

```
线段 S 上的点: P(t) = P₁ + t·(P₂ - P₁),   t ∈ [0,1]
线段 L 上的点: Q(s) = Q₁ + s·(Q₂ - Q₁),   s ∈ [0,1]（直线则 s ∈ ℝ）
```

令 P(t) = Q(s)，解方程组：

```
P₁.x + t·(P₂.x - P₁.x) = Q₁.x + s·(Q₂.x - Q₁.x)
P₁.y + t·(P₂.y - P₁.y) = Q₁.y + s·(Q₂.y - Q₁.y)
```

设：

```
→        →
d₁ = P₂ - P₁,   d₂ = Q₂ - Q₁,   d₀ = Q₁ - P₁

分母 denom = d₁ × d₂ = d₁.x · d₂.y - d₁.y · d₂.x
```

若 `denom = 0`：两线段平行（可能共线，参见 §2.19）。

否则：

```
t = (d₀ × d₂) / denom = (d₀.x · d₂.y - d₀.y · d₂.x) / denom
s = (d₀ × d₁) / denom = (d₀.x · d₁.y - d₀.y · d₁.x) / denom
```

**对线段与线段**：交点存在 ⟺ `0 ≤ t ≤ 1` 且 `0 ≤ s ≤ 1`
**对直线与线段**：交点存在 ⟺ `0 ≤ t ≤ 1`（s 无限制）

交点坐标：

```
X = P₁.x + t · d₁.x
Y = P₁.y + t · d₁.y
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.20 计算线段/直线与线段的交点（添加到 turning_algo.py）──────────

def line_segment_intersection(p1, p2, q1, q2, segment_mode=True):
    """
    计算两条线段（或直线与线段）的交点。

    参数:
        p1, p2: 第一条线段的端点
        q1, q2: 第二条线段的端点
        segment_mode: True=线段-线段, False=直线(p1p2)-线段(q1q2)
    返回:
        (x, y) 交点坐标，或 None（平行/无交点）
    """
    d1 = vec(p1, p2)       # P₂ - P₁
    d2 = vec(q1, q2)       # Q₂ - Q₁
    d0 = vec(p1, q1)       # Q₁ - P₁

    denom = cross2d(d1, d2)   # d₁ × d₂

    if abs(denom) < 1e-15:
        return None           # 平行（可能共线，见 §2.19）

    t = cross2d(d0, d2) / denom   # (d₀ × d₂) / denom
    s = cross2d(d0, d1) / denom   # (d₀ × d₁) / denom

    if segment_mode:
        # 线段-线段：t 和 s 都必须在 [0, 1]
        if t < -1e-10 or t > 1 + 1e-10 or s < -1e-10 or s > 1 + 1e-10:
            return None
    else:
        # 直线-线段：只检查 s（线段 q1q2 的参数）
        if s < -1e-10 or s > 1 + 1e-10:
            return None

    # 交点坐标
    x = p1[0] + t * d1[0]
    y = p1[1] + t * d1[1]
    return (x, y)
```

### 如何在 GUI 中使用 — `zxpd1.py` 修改思路

```python
# zxpd1.py 中添加交点计算功能：
from turning_algo import (..., line_segment_intersection)

def calc_intersection_point(self):
    """计算两条线段的交点并标记"""
    if len(self.points) < 4:
        messagebox.showwarning("提示", "至少需要 4 个点")
        return
    p1, p2 = self.points[0], self.points[1]
    q1, q2 = self.points[2], self.points[3]
    pt = line_segment_intersection(p1, p2, q1, q2)
    if pt:
        messagebox.showinfo("交点", f"交点坐标: ({pt[0]:.4f}, {pt[1]:.4f})")
    else:
        messagebox.showinfo("交点", "两线段无交点（平行或不相交）")
```

### 可视化交点 — `turning_plot.py` 修改思路

```python
# turning_plot.py 的 CanvasWidget 类中添加：
def draw_intersection_point(self, pt, label="交点"):
    """在画布上标记交点"""
    self._ax.scatter([pt[0]], [pt[1]], c='gold', s=120, zorder=5,
                     edgecolors='black', linewidths=2, marker='*')
    self._ax.annotate(f'{label}\n({pt[0]:.2f},{pt[1]:.2f})', pt,
                      textcoords="offset points", xytext=(10, 10),
                      fontsize=9, color='#E65100', fontweight='bold')
```

---

## 2.21 求线段或直线与圆的交点

### 问题

给定线段 P₁P₂（或直线）和圆 C(O, r)，求交点。

### 算法

**第一步**：将问题转化为参数方程。

线段上的点 P(t) = P₁ + t·d，其中 d = P₂ - P₁。

代入圆方程 |P(t) - O|² = r²：

```
|P₁ + t·d - O|² = r²
```

设 f = P₁ - O，展开：

```
|f + t·d|² = r²
(d·d)t² + 2(f·d)t + (f·f - r²) = 0
```

即一元二次方程 `At² + Bt + C = 0`：

```
A = d·d = dₓ² + d_y²       （d 的模的平方）
B = 2(f·d) = 2(fₓdₓ + f_yd_y)
C = f·f - r² = fₓ² + f_y² - r²
```

**第二步**：计算判别式。

```
Δ = B² - 4AC

Δ < 0 → 不相交
Δ = 0 → 相切（一个交点）
Δ > 0 → 相交（两个交点）
```

**第三步**：求参数值。

```
t₁ = (-B - √Δ) / (2A)
t₂ = (-B + √Δ) / (2A)
```

**对线段**：只保留 `0 ≤ t ≤ 1` 范围内的参数值。
**对直线**：t 无限制。

**第四步**：回代得交点坐标。

```
交点 = P₁ + t · d
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.21 线段/直线与圆的交点（添加到 turning_algo.py）────────────────

def line_circle_intersection(p1, p2, center, radius, segment_mode=True):
    """
    计算线段（或直线）与圆的交点。

    参数:
        p1, p2:       线段端点
        center:       (cx, cy) 圆心
        radius:       半径
        segment_mode: True=线段, False=直线
    返回:
        list of (x, y)  交点列表（0、1 或 2 个点）
    """
    d = vec(p1, p2)
    f = vec(center, p1)     # f = P₁ - O

    a = dot(d, d)           # A = d·d
    b = 2 * dot(f, d)       # B = 2(f·d)
    c = dot(f, f) - radius * radius   # C = f·f - r²

    discriminant = b * b - 4 * a * c

    if discriminant < -1e-10:
        return []             # 不相交

    results = []
    if abs(discriminant) < 1e-10:
        # 相切：一个交点
        t = -b / (2 * a)
        if not segment_mode or -1e-10 <= t <= 1 + 1e-10:
            results.append(vec_add(p1, vec_scale(t, d)))
    else:
        # 相交：两个交点
        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)
        for t in [t1, t2]:
            if not segment_mode or -1e-10 <= t <= 1 + 1e-10:
                results.append(vec_add(p1, vec_scale(t, d)))

    return results
```

---

## 2.22 中心点的计算

### 问题

给定一组点 P₁, P₂, ..., Pₙ（或多边形顶点），求中心点。

### 方法一：重心（算术平均）

```
Gₓ = (P₁.x + P₂.x + ... + Pₙ.x) / n
G_y = (P₁.y + P₂.y + ... + Pₙ.y) / n
```

这是**点集的几何中心**，对离散点总是适用。

### 方法二：多边形几何重心

对于多边形（有面积的区域），几何重心需要考虑面积分布：

```
先计算有符号面积：
A = ½ · Σᵢ (xᵢ · yᵢ₊₁ - xᵢ₊₁ · yᵢ)

再计算重心坐标：
Cₓ = 1/(6A) · Σᵢ (xᵢ + xᵢ₊₁)(xᵢ · yᵢ₊₁ - xᵢ₊₁ · yᵢ)
C_y = 1/(6A) · Σᵢ (yᵢ + yᵢ₊₁)(xᵢ · yᵢ₊₁ - xᵢ₊₁ · yᵢ)
```

其中下标 i+1 在最后一项时回到 1（闭合）。

### 方法三：线段中点

两点的中心点即中点：

```
M = ((P₁.x + P₂.x)/2,  (P₁.y + P₂.y)/2)
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.22 中心点的计算（添加到 turning_algo.py）───────────────────────

def centroid_points(points):
    """
    点集的几何中心（算术平均）。

    参数:
        points: [(x1,y1), (x2,y2), ...] 至少1个点
    返回:
        (cx, cy)
    """
    n = len(points)
    cx = sum(p[0] for p in points) / n
    cy = sum(p[1] for p in points) / n
    return (cx, cy)


def centroid_polygon(vertices):
    """
    多边形的几何重心（考虑面积分布）。

    参数:
        vertices: [(x1,y1), ...] 多边形顶点（逆时针或顺时针）
    返回:
        (cx, cy)
    """
    n = len(vertices)
    signed_area = 0.0
    cx = 0.0
    cy = 0.0

    for i in range(n):
        x0, y0 = vertices[i]
        x1, y1 = vertices[(i + 1) % n]
        a = x0 * y1 - x1 * y0
        signed_area += a
        cx += (x0 + x1) * a
        cy += (y0 + y1) * a

    signed_area *= 0.5
    if abs(signed_area) < 1e-15:
        return centroid_points(vertices)   # 退化为点集平均

    cx /= (6.0 * signed_area)
    cy /= (6.0 * signed_area)
    return (cx, cy)


def midpoint(p1, p2):
    """两点的中点"""
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
```

---

## 2.23 过点作垂线

### 问题

给定直线 L（由两点 A、B 确定）和直线外一点 P，
过 P 作 L 的垂线，求垂足 H。

### 算法

```
→
d = B - A         ← 直线方向向量

     →     →
t = (P-A)·d / (d·d)     ← 投影参数

垂足 H = A + t · d
```

### 图解

```
A ─────────H─────────── B      直线 L
            │
            │  （垂线）
            │
            P
```

### 点到直线的距离

```
     →     →
dist = |(P-A) × d| / |d|

     = |cross(P-A, d)| / |d|
```

叉积的绝对值除以方向向量的模 = 垂直距离。

### 点到线段的距离

需额外限制参数 t 的范围：

```
若 t < 0 → 最近点是 A，距离 = |P - A|
若 t > 1 → 最近点是 B，距离 = |P - B|
若 0 ≤ t ≤ 1 → 最近点是垂足 H，距离 = |P - H|
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.23 过点作垂线（添加到 turning_algo.py）─────────────────────────

def perpendicular_foot(p, a, b):
    """
    过点 p 向直线 AB 作垂线，求垂足 H。

    参数:
        p:    (x, y) 直线外一点
        a, b: (x, y) 直线上两点
    返回:
        (hx, hy) 垂足坐标
    """
    d = vec(a, b)
    t = dot(vec(a, p), d) / dot(d, d)
    return vec_add(a, vec_scale(t, d))


def point_to_line_dist(p, a, b):
    """
    点 p 到直线 AB 的距离（用叉积计算）。
    dist = |cross(AP, AB)| / |AB|
    """
    return abs(cross2d(vec(a, p), vec(a, b))) / vec_length(vec(a, b))
```

> **教学说明**：`point_to_segment_dist()`（§2.15 已实现）是点到**线段**的距离，
> 需要限制 t 在 [0,1]。这里的 `point_to_line_dist()` 是点到**直线**的距离，t 无限制。

---

## 2.24 作平行线

### 问题

给定直线 L（由两点 A、B 确定）和距离 d，
求 L 的平行线 L'。

### 算法

**第一步**：求 L 的单位法向量。

```
→
方向向量 v = B - A = (Δx, Δy)

→                               →
法向量 n = (-Δy, Δx)       单位法向量 n̂ = n / |n|
```

**第二步**：沿法向量偏移。

```
A' = A + d · n̂
B' = B + d · n̂
```

平行线 L' 过 A' 和 B'。

### 注意

法向量有两个方向（左侧/右侧），d 取正值为左侧偏移，负值为右侧偏移
（具体取决于法向量的选取方向）。

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.24 作平行线（添加到 turning_algo.py）───────────────────────────

def parallel_line(a, b, dist):
    """
    给定直线 AB 和偏移距离 dist，求平行线上的两个点。

    正 dist = 左侧偏移（法向量方向），负 dist = 右侧偏移。

    返回:
        (a_new, b_new)  平行线上的两个点
    """
    d = vec(a, b)
    n = vec_normal(d)              # 法向量 (-dy, dx)
    n_hat = vec_unit(n)            # 单位法向量
    offset = vec_scale(dist, n_hat)
    a_new = vec_add(a, offset)
    b_new = vec_add(b, offset)
    return (a_new, b_new)
```

### 图解

```
A' ──────────────────── B'    ← 平行线 L'（偏移 d）
         ↑ d
A  ──────────────────── B     ← 原直线 L
```

---

## 2.25 过点作平行线

### 问题

给定直线 L（由 A、B 确定）和一个点 P，过 P 作 L 的平行线。

### 算法

平行线与 L 方向相同，过 P 即可确定：

```
→
方向向量 d = B - A

平行线上两点：P 和 P + d
    即 P₁ = P
       P₂ = (P.x + d.x,  P.y + d.y)
```

或参数方程：`Q(t) = P + t · d`，t ∈ ℝ。

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.25 过点作平行线（添加到 turning_algo.py）───────────────────────

def parallel_through_point(a, b, p):
    """
    过点 p 作直线 AB 的平行线。

    返回:
        (p1, p2)  平行线上的两个点（p 和 p + AB方向向量）
    """
    d = vec(a, b)
    return (p, vec_add(p, d))
```

---

## 2.26 线段延长

### 问题

给定线段 P₁P₂，将其沿方向延长指定长度 ΔL，求新端点 P₂'。

### 算法

```
→                        →
方向向量 d = P₂ - P₁    单位向量 d̂ = d / |d|

新端点 P₂' = P₂ + ΔL · d̂
```

若要**反向延长**（从 P₁ 方向延长）：

```
新端点 P₁' = P₁ - ΔL · d̂
```

### 图解

```
P₁ ────────── P₂ ─ ─ ─ → P₂'
                    ΔL
```

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.26 线段延长（添加到 turning_algo.py）───────────────────────────

def extend_segment(p1, p2, delta_length):
    """
    将线段 p1p2 从 p2 方向延长 delta_length。

    参数:
        p1, p2:       线段端点
        delta_length: 延长距离（正=从p2方向延长，负=从p1方向延长）
    返回:
        (x, y) 新端点坐标
    """
    d = vec(p1, p2)
    d_hat = vec_unit(d)
    return vec_add(p2, vec_scale(delta_length, d_hat))


def extend_segment_reverse(p1, p2, delta_length):
    """将线段从 p1 方向反向延长"""
    d = vec(p1, p2)
    d_hat = vec_unit(d)
    return vec_add(p1, vec_scale(-delta_length, d_hat))
```

---

## 2.27 三点画圆

### 问题

给定不共线的三点 P₁(x₁,y₁)、P₂(x₂,y₂)、P₃(x₃,y₃)，
求过三点的圆（外接圆）的圆心和半径。

### 原理

圆心 O 是三个点的**外心**，到三个点的距离相等。
O 位于任意两条弦的**垂直平分线**的交点。

### 算法

由 |OP₁|² = |OP₂|² = |OP₃|²，展开消去得线性方程组：

```
设圆心 O(a, b)：

(x₁² - x₂²) + (y₁² - y₂²) = 2a(x₁ - x₂) + 2b(y₁ - y₂)  ... ①
(x₂² - x₃²) + (y₂² - y₃²) = 2a(x₂ - x₃) + 2b(y₂ - y₃)  ... ②
```

整理为标准形式 `2(x₁-x₂)a + 2(y₁-y₂)b = x₁²-x₂²+y₁²-y₂²`，
用克莱姆法则或消元法求解 (a, b)。

**具体公式**（设中间变量简化书写）：

```
A₁ = 2(x₂ - x₁),  B₁ = 2(y₂ - y₁),  C₁ = x₂² + y₂² - x₁² - y₁²
A₂ = 2(x₃ - x₂),  B₂ = 2(y₃ - y₂),  C₂ = x₃² + y₃² - x₂² - y₂²

D = A₁·B₂ - A₂·B₁    （若 D = 0 → 三点共线，无法画圆）

圆心: a = (C₁·B₂ - C₂·B₁) / D
      b = (A₁·C₂ - A₂·C₁) / D

半径: r = √((x₁-a)² + (y₁-b)²)
```

### 退化情况

三点共线时（D = 0），无有限半径的圆经过三点（退化为直线）。

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.27 三点画圆（添加到 turning_algo.py）───────────────────────────

def circumscribed_circle(p1, p2, p3):
    """
    过三点画圆（外接圆），求圆心和半径。

    参数:
        p1, p2, p3: (x, y) 不共线的三个点
    返回:
        ((cx, cy), radius)  圆心坐标和半径
    异常:
        ValueError: 三点共线
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    A1 = 2 * (x2 - x1)
    B1 = 2 * (y2 - y1)
    C1 = x2*x2 + y2*y2 - x1*x1 - y1*y1

    A2 = 2 * (x3 - x2)
    B2 = 2 * (y3 - y2)
    C2 = x3*x3 + y3*y3 - x2*x2 - y2*y2

    D = A1 * B2 - A2 * B1
    if abs(D) < 1e-12:
        raise ValueError("三点共线，无法画圆")

    cx = (C1 * B2 - C2 * B1) / D
    cy = (A1 * C2 - A2 * C1) / D
    radius = math.sqrt((x1 - cx)**2 + (y1 - cy)**2)

    return ((cx, cy), radius)
```

### 如何在 GUI 中使用 — `zxpd1.py` 修改思路

```python
# zxpd1.py 中添加三点画圆功能：
from turning_algo import (..., circumscribed_circle)

def draw_circumscribed_circle(self):
    """用前 3 个点画外接圆"""
    if len(self.points) < 3:
        messagebox.showwarning("提示", "至少需要 3 个点")
        return
    try:
        center, radius = circumscribed_circle(
            self.points[0], self.points[1], self.points[2]
        )
        # 调用绘图模块的 draw_circle 方法
        self.canvas_widget.draw_circle(center, radius, color='#7B1FA2')
        self.canvas_widget._canvas.draw()
        messagebox.showinfo("三点画圆",
            f"圆心: ({center[0]:.4f}, {center[1]:.4f})\n半径: {radius:.4f}")
    except ValueError as e:
        messagebox.showwarning("提示", str(e))
```

---

## 2.28 线段打断

### 问题

在线段 P₁P₂ 上的指定位置将其打断为两段。

### 方法一：按比例打断

给定比例 t（0 < t < 1），打断点：

```
M = P₁ + t · (P₂ - P₁) = ((1-t)·x₁ + t·x₂,  (1-t)·y₁ + t·y₂)
```

原线段变为：P₁→M 和 M→P₂ 两段。

### 方法二：按距离打断

给定从 P₁ 起的距离 d：

```
t = d / |P₂ - P₁|
M = P₁ + t · (P₂ - P₁)
```

### 方法三：在指定点处打断

给定一个已知在线段上的点 M（可由 §2.4 验证），
直接以 M 为分界点，将 P₁P₂ 拆为 P₁M 和 MP₂。

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.28 线段打断（添加到 turning_algo.py）───────────────────────────

def break_segment_by_ratio(p1, p2, t):
    """
    按比例 t (0 < t < 1) 打断线段 p1p2。
    返回打断点 M 和两条新线段。

    返回:
        (M, (p1, M), (M, p2))
    """
    d = vec(p1, p2)
    m = vec_add(p1, vec_scale(t, d))
    return (m, (p1, m), (m, p2))


def break_segment_by_distance(p1, p2, dist):
    """
    从 p1 起按距离 dist 打断线段。
    返回打断点 M 和两条新线段。
    """
    total = vec_length(vec(p1, p2))
    if total < 1e-15:
        return (p1, (p1, p1), (p1, p2))
    t = dist / total
    return break_segment_by_ratio(p1, p2, t)


def break_segment_at_point(p1, p2, m):
    """
    在指定点 M 处打断线段（假设 M 已在线段上）。
    返回两条新线段。
    """
    return ((p1, m), (m, p2))
```

---

## 2.29 前方交会

### 问题

在两个已知控制点 A、B 上分别观测到未知点 P 的**方位角**
（或与 AB 基线的夹角 α、β），求 P 的坐标。

这是测量学（大地测量）中的经典问题。

### 几何原理

```
            P
           / \
          /   \
         / α   \ β
        /       \
A ─────────────── B
```

已知 A、B 的坐标和角度 α（从 A 观测 P 的方向）、β（从 B 观测 P 的方向），
求 P 的坐标。

### 算法

**方法：三角公式法**

```
AB 基线方位角: φ_AB = atan2(B.y - A.y, B.x - A.x)
AB 基线长度:   D_AB = |B - A|

从 A 到 P 的方位角: φ_AP = φ_AB + α
从 B 到 P 的方位角: φ_BP = φ_AB + π + β    （或 φ_BA + β）

两条方向线的交点即为 P。
```

用参数化方法：

```
A 出发的射线: P = A + t₁·(cos φ_AP, sin φ_AP)
B 出发的射线: P = B + t₂·(cos φ_BP, sin φ_BP)

解线性方程组得 t₁（或 t₂），代回得 P 坐标。
```

**正弦定理法**：

在三角形 ABP 中，角 A = α，角 B = β，则角 P = π - α - β。

```
AP / sin B = AB / sin P
AP = AB · sin β / sin(α + β)

P.x = A.x + AP · cos(φ_AP)
P.y = A.y + AP · sin(φ_AP)
```

### 退化情况

- α + β = 0 或 π：三点共线，无交会解
- α + β ≈ π：交角过大，P 离基线太近，精度差
- α + β ≈ 0：P 离基线太远，精度差

经验法则：α + β 在 30°~150° 之间时，交会精度较好。

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.29 前方交会（添加到 turning_algo.py）───────────────────────────

def forward_intersection(a, b, alpha, beta):
    """
    前方交会：从控制点 A、B 分别以角度 α、β 观测未知点 P。

    参数:
        a, b:    (x, y) 两个已知控制点
        alpha:   从 A 观测 P 的角度（与 AB 基线的夹角，弧度）
        beta:    从 B 观测 P 的角度（与 BA 基线的夹角，弧度）
    返回:
        (px, py) 未知点 P 的坐标
    异常:
        ValueError: α + β 无法交会
    """
    # AB 基线方位角
    phi_ab = math.atan2(b[1] - a[1], b[0] - a[0])
    d_ab = vec_length(vec(a, b))

    # A 到 P 的方位角
    phi_ap = phi_ab + alpha

    # 正弦定理: AP / sin(β) = AB / sin(π - α - β)
    angle_sum = alpha + beta
    if abs(math.sin(angle_sum)) < 1e-12:
        raise ValueError("α + β 导致退化（三点共线），无法交会")

    ap = d_ab * math.sin(beta) / math.sin(angle_sum)

    px = a[0] + ap * math.cos(phi_ap)
    py = a[1] + ap * math.sin(phi_ap)
    return (px, py)
```

---

## 2.30 距离交会

### 问题

从两个已知控制点 A、B 分别测量到未知点 P 的**距离** d₁、d₂，求 P 的坐标。

### 几何原理

以 A 为圆心 d₁ 为半径画圆，以 B 为圆心 d₂ 为半径画圆，
两圆的交点即为 P 的可能位置。

```
       P₁
      ╱  ╲
     ╱    ╲
A ──╱──────╲── B
     ╲    ╱
      ╲  ╱
       P₂
```

两圆相交通常有**两个解**（P₁ 和 P₂），需要附加条件（如方向）选取正确的点。

### 算法

设 A(x_A, y_A)，B(x_B, y_B)，d_AB = |AB|。

```
① 求交点连线到 AB 的投影距离:

   a = (d₁² - d₂² + d_AB²) / (2·d_AB)     ← A 到中线的距离

② 求交点到 AB 的垂直距离:

   h = √(d₁² - a²)

③ 求中线基点 M（在 AB 上）:

   M = A + a/d_AB · (B - A)

④ 求两个交点:

   →
   n = AB 的单位法向量 = (-(B.y-A.y)/d_AB, (B.x-A.x)/d_AB)

   P₁ = M + h · n
   P₂ = M - h · n
```

### 解的个数

| 条件 | 解的个数 |
|------|:--------:|
| d₁ + d₂ < d_AB | 0（两圆不相交） |
| d₁ + d₂ = d_AB | 1（外切） |
| \|d₁ - d₂\| < d_AB < d₁ + d₂ | **2** |
| d_AB = \|d₁ - d₂\| | 1（内切） |
| d_AB < \|d₁ - d₂\| | 0（一圆在另一圆内） |

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.30 距离交会（添加到 turning_algo.py）───────────────────────────

def distance_intersection(a, b, d1, d2):
    """
    距离交会：从控制点 A、B 分别测得到 P 的距离 d1、d2，求 P。

    参数:
        a, b:  (x, y) 两个已知控制点
        d1:    A 到 P 的距离
        d2:    B 到 P 的距离
    返回:
        [(p1x, p1y), (p2x, p2y)]  两个可能的交会点
        或 [(px, py)]              一个交点（相切）
        或 []                      无解
    """
    d_ab = vec_length(vec(a, b))

    # 检查有解条件
    if d_ab > d1 + d2 + 1e-10:
        return []                     # 两圆不相交
    if d_ab < abs(d1 - d2) - 1e-10:
        return []                     # 一圆在另一圆内

    # ① A 到中线基点 M 的距离
    a_dist = (d1*d1 - d2*d2 + d_ab*d_ab) / (2 * d_ab)

    # ② 交点到 AB 的垂直距离
    h_sq = d1*d1 - a_dist*a_dist
    if h_sq < 0:
        h_sq = 0    # 数值误差修正
    h = math.sqrt(h_sq)

    # ③ 中线基点 M
    ab_unit = vec_unit(vec(a, b))
    m = vec_add(a, vec_scale(a_dist, ab_unit))

    # ④ AB 的单位法向量
    n = vec_unit(vec_normal(vec(a, b)))

    if h < 1e-10:
        return [m]                    # 相切，一个解

    p1 = vec_add(m, vec_scale(h, n))
    p2 = vec_add(m, vec_scale(-h, n))
    return [p1, p2]
```

---

## 2.31 极坐标作点

### 问题

已知一个起始点 A 和一个**方位角 θ**（从正北/正东起算）以及**距离 d**，
求目标点 P 的坐标。

这是极坐标定点（Polar Coordinate Construction）的基本操作。

### 算法

**数学坐标系**（角度从 x 轴正方向逆时针度量）：

```
P.x = A.x + d · cos θ
P.y = A.y + d · sin θ
```

**测量坐标系**（方位角从正北顺时针度量）：

```
P.x = A.x + d · sin θ    ← 注意 sin/cos 对调
P.y = A.y + d · cos θ
```

### 图解（数学坐标系）

```
          P
         ╱
        ╱ d
       ╱
      ╱ θ
A ───────→ x 轴
```

### 图解（测量坐标系，方位角从北起算）

```
      N（y 轴）
      ↑
      │ ╲  θ
      │   ╲
      │     P
      │   ╱ d
      │ ╱
A ────┼──── E（x 轴）
```

### 应用

- 极坐标放样：根据全站仪的测量数据定出实地点位
- 导线测量中的坐标推算
- 与 §2.29 前方交会互为补充

### 代码实现 — `turning_algo.py` 中添加

```python
# ── §2.31 极坐标作点（添加到 turning_algo.py）─────────────────────────

def polar_point_math(a, theta, dist):
    """
    数学坐标系下的极坐标作点（角度从 x 轴正方向逆时针度量）。

    参数:
        a:     (x, y) 起始点
        theta: 方位角（弧度，从 x 轴逆时针）
        dist:  距离
    返回:
        (px, py) 目标点
    """
    px = a[0] + dist * math.cos(theta)
    py = a[1] + dist * math.sin(theta)
    return (px, py)


def polar_point_survey(a, theta, dist):
    """
    测量坐标系下的极坐标作点（方位角从正北顺时针度量）。

    注意：测量坐标系中 sin/cos 与数学坐标系对调。

    参数:
        a:     (x, y) 起始点
        theta: 方位角（弧度，从正北顺时针）
        dist:  距离
    返回:
        (px, py) 目标点
    """
    px = a[0] + dist * math.sin(theta)
    py = a[1] + dist * math.cos(theta)
    return (px, py)
```

---

## 思考题

1. **DE-9IM 实践**：线段 AB 的一个端点恰好在多边形的边上，
   请写出此时的 9 交集矩阵。这属于八种基本拓扑关系中的哪一种？

2. **跨立实验的退化**：两条线段共线且部分重叠时，
   四个叉积都是 0，跨立实验失效。如何处理这种情况？
   提示：回退到 §2.19 的区间重叠判断。

3. **射线法的优化**：对一个有 1000 条边的复杂多边形，
   如何减少射线法中每次都遍历所有边的开销？
   提示：先用 MBR（§2.6）快速排除，再对边做空间分桶。

4. **凸性判断**：利用叉积，如何判断一个多边形是否为凸多边形？
   提示：遍历所有顶点，叉积全正或全负 → 凸。

5. **三点画圆 vs 最小外接圆**：三点画圆（§2.27）求的是过三点的圆。
   如果给你一组 n 个点，如何求包住所有点的**最小外接圆**？
   提示：Welzl 算法，随机增量法。

6. **前方交会 vs 距离交会**：分别在什么测量场景下使用？
   各自对仪器精度有什么要求？
   - 前方交会需要精确的**测角仪器**（经纬仪、全站仪）
   - 距离交会需要精确的**测距仪器**（EDM、钢尺）

7. **圆在多边形内（§2.15）的优化**：对于凸多边形，
   "点到每条边的距离"可以用叉积快速计算而不需要投影参数 t。
   具体怎么做？

8. **综合题**：给定一个任意多边形和一个圆，
   如何判断它们"相交但互不包含"？请用本章学过的算法组合出完整流程。

---

> 📌 本章算法是所有 GIS 空间分析的基石。掌握了向量叉积和点积这两个基本工具后，
> 绝大部分包含判断、相交判断、交点计算都可以自然推导出来。
> 后续章节的叠加分析、缓冲区分析、网络分析等高级算法，都建立在这些基础之上。

---

## 🔧 完整修改指南：如何将本章算法集成到项目中

### 第一步：修改 `turning_algo.py`

在文件顶部添加 `import math`，然后将本章所有函数按顺序追加到文件末尾：

```python
# ════════════════════════════════════════════════════════════════════════
# turning_algo.py 修改清单
# ════════════════════════════════════════════════════════════════════════
#
# 1. 文件顶部添加：
import math
#
# 2. 在已有的 save_results() 函数后面，依次添加以下函数：
#
# ── §2.2 向量基础 ──
#   vec(a, b)                    → 两点构成向量
#   vec_add(u, v)                → 向量加法
#   vec_scale(k, v)              → 数乘
#   vec_length(v)                → 模
#   vec_unit(v)                  → 单位向量
#   dot(u, v)                    → 点积
#   cross2d(u, v)                → 二维叉积
#   vec_normal(v)                → 法向量
#
# ── §2.4 点在线段上 ──
#   point_on_segment(q, p1, p2)
#
# ── §2.5 线段相交 ──
#   segments_intersect(p1, p2, q1, q2)
#   segments_proper_intersect(p1, p2, q1, q2)
#
# ── §2.6-2.9 矩形包含 ──
#   rect_contains_point(rect, q)
#   segment_in_rect(rect, p1, p2)
#   polyline_in_rect(rect, points)
#   polygon_in_rect(rect, vertices)
#   rect_in_rect(outer, inner)
#   circle_in_rect(rect, center, radius)
#
# ── §2.10 点在多边形内 ──
#   point_in_polygon_ray(q, polygon)
#   point_in_polygon_winding(q, polygon)
#
# ── §2.11-2.15 多边形包含 ──
#   segment_in_polygon(p1, p2, polygon)
#   polyline_in_polygon(polyline, polygon)
#   polygon_in_polygon(inner_poly, outer_poly)
#   rect_in_polygon(rect, polygon)
#   point_to_segment_dist(q, p1, p2)
#   circle_in_polygon(center, radius, polygon)
#
# ── §2.16-2.18 圆包含 ──
#   point_in_circle(q, center, radius)
#   points_all_in_circle(points, center, radius)
#   segment_in_circle(p1, p2, center, radius)
#   rect_in_circle(rect, center, radius)
#   circle_in_circle(c1_center, c1_radius, c2_center, c2_radius)
#
# ── §2.19-2.21 交点计算 ──
#   collinear_overlap(p1, p2, q1, q2)
#   line_segment_intersection(p1, p2, q1, q2, segment_mode=True)
#   line_circle_intersection(p1, p2, center, radius, segment_mode=True)
#
# ── §2.22-2.31 几何构造 ──
#   centroid_points(points)
#   centroid_polygon(vertices)
#   midpoint(p1, p2)
#   perpendicular_foot(p, a, b)
#   point_to_line_dist(p, a, b)
#   parallel_line(a, b, dist)
#   parallel_through_point(a, b, p)
#   extend_segment(p1, p2, delta_length)
#   extend_segment_reverse(p1, p2, delta_length)
#   circumscribed_circle(p1, p2, p3)
#   break_segment_by_ratio(p1, p2, t)
#   break_segment_by_distance(p1, p2, dist)
#   break_segment_at_point(p1, p2, m)
#   forward_intersection(a, b, alpha, beta)
#   distance_intersection(a, b, d1, d2)
#   polar_point_math(a, theta, dist)
#   polar_point_survey(a, theta, dist)
```

### 第二步：修改 `turning_plot.py`

在 `CanvasWidget` 类中添加通用几何图形绘制方法：

```python
# ════════════════════════════════════════════════════════════════════════
# turning_plot.py 修改清单
# ════════════════════════════════════════════════════════════════════════
#
# 1. 文件顶部添加：
import matplotlib.patches as patches
from matplotlib.patches import Polygon as MplPolygon
#
# 2. 在 CanvasWidget 类中添加以下方法：

def draw_rect(self, rect, color='#1565C0', label=None):
    """绘制轴对齐矩形"""
    xmin, ymin, xmax, ymax = rect
    r = patches.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                           linewidth=2, edgecolor=color,
                           facecolor=color, alpha=0.1)
    self._ax.add_patch(r)
    if label:
        self._ax.text((xmin+xmax)/2, ymax + 1, label,
                      ha='center', fontsize=9, color=color)

def draw_circle(self, center, radius, color='#E65100', label=None):
    """绘制圆"""
    c = patches.Circle(center, radius,
                       linewidth=2, edgecolor=color,
                       facecolor=color, alpha=0.1)
    self._ax.add_patch(c)
    if label:
        self._ax.text(center[0], center[1] + radius + 1, label,
                      ha='center', fontsize=9, color=color)

def draw_polygon_fill(self, vertices, color='#1565C0', alpha=0.15):
    """绘制填充多边形"""
    poly = MplPolygon(vertices, closed=True,
                      edgecolor=color, facecolor=color,
                      alpha=alpha, linewidth=2)
    self._ax.add_patch(poly)

def draw_intersection_point(self, pt, label="交点"):
    """在画布上标记特殊点（如交点、垂足、圆心）"""
    self._ax.scatter([pt[0]], [pt[1]], c='gold', s=120, zorder=5,
                     edgecolors='black', linewidths=2, marker='*')
    self._ax.annotate(f'{label}\n({pt[0]:.2f},{pt[1]:.2f})', pt,
                      textcoords="offset points", xytext=(10, 10),
                      fontsize=9, color='#E65100', fontweight='bold')
```

### 第三步：修改 `zxpd1.py`

在主程序中添加新功能按钮和对应的处理方法：

```python
# ════════════════════════════════════════════════════════════════════════
# zxpd1.py 修改清单
# ════════════════════════════════════════════════════════════════════════
#
# 1. 修改导入行：
from turning_algo import (
    analyze_all, load_points, save_results,
    # §2.4-2.5
    point_on_segment, segments_intersect, line_segment_intersection,
    # §2.6
    rect_contains_point,
    # §2.10
    point_in_polygon_ray,
    # §2.16
    point_in_circle,
    # §2.22
    centroid_points, centroid_polygon,
    # §2.27
    circumscribed_circle,
    # ... 按需添加更多
)
#
# 2. 在 _build_toolbar() 中添加一个"算法工具"菜单按钮：

def _build_algo_menu(self):
    """创建算法工具下拉菜单"""
    menubar = tk.Menu(self.root)
    self.root.config(menu=menubar)

    algo_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="📐 算法工具", menu=algo_menu)

    algo_menu.add_command(label="判断点是否在线段上 (§2.4)",
                          command=self.check_point_on_segment)
    algo_menu.add_command(label="判断两线段是否相交 (§2.5)",
                          command=self.check_intersection)
    algo_menu.add_command(label="计算两线段交点 (§2.20)",
                          command=self.calc_intersection_point)
    algo_menu.add_separator()
    algo_menu.add_command(label="判断点是否在多边形内 (§2.10)",
                          command=self.check_point_in_polygon)
    algo_menu.add_separator()
    algo_menu.add_command(label="计算重心 (§2.22)",
                          command=self.show_centroid)
    algo_menu.add_command(label="三点画圆 (§2.27)",
                          command=self.draw_circumscribed_circle)
#
# 3. 在 __init__ 中调用 self._build_algo_menu()
#
# 4. 添加各功能方法（前面各节已展示），关键方法汇总如下：

def show_centroid(self):
    """显示当前所有点的重心"""
    if len(self.points) < 1:
        messagebox.showwarning("提示", "至少需要 1 个点")
        return
    c = centroid_points(self.points)
    self.canvas_widget.draw_intersection_point(c, label="重心")
    self.canvas_widget._canvas.draw()
    messagebox.showinfo("重心", f"重心坐标: ({c[0]:.4f}, {c[1]:.4f})")
```

### 函数依赖关系图

```
vec(), cross2d(), dot()                    ← §2.2 基础工具（被所有函数调用）
    │
    ├── cross_product(), analyze_all()     ← §2.3 拐向判断（已有）
    │
    ├── point_on_segment()                 ← §2.4
    │       │
    │       └── segments_intersect()       ← §2.5
    │               │
    │               ├── segments_proper_intersect()
    │               │       │
    │               │       ├── segment_in_polygon()    ← §2.11
    │               │       ├── polygon_in_polygon()    ← §2.13
    │               │       └── rect_in_polygon()       ← §2.14
    │               │
    │               └── line_segment_intersection()     ← §2.20
    │
    ├── rect_contains_point()              ← §2.6
    │       │
    │       ├── segment_in_rect()          ← §2.7
    │       ├── polyline_in_rect()         ← §2.7
    │       ├── rect_in_rect()             ← §2.8
    │       └── circle_in_rect()           ← §2.9
    │
    ├── point_in_polygon_ray()             ← §2.10
    │       │
    │       ├── segment_in_polygon()       ← §2.11
    │       ├── polyline_in_polygon()      ← §2.12
    │       ├── circle_in_polygon()        ← §2.15
    │       └── polygon_in_polygon()       ← §2.13
    │
    ├── point_in_circle()                  ← §2.16
    │       └── points_all_in_circle()     ← §2.17
    │
    ├── vec_unit(), vec_normal()
    │       ├── parallel_line()            ← §2.24
    │       ├── extend_segment()           ← §2.26
    │       ├── distance_intersection()    ← §2.30
    │       └── polar_point_math/survey()  ← §2.31
    │
    └── circumscribed_circle()             ← §2.27
```
