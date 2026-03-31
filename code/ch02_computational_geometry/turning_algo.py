"""
turning_algo.py  ——  折线拐向算法模块
纯计算逻辑，不依赖任何 UI 框架。
"""
import csv
import math
eps = 1e-10

#=========   a,b转换为向量
def vec(a,b):
    return (b[0] - a[0],b[1] - a[1])

# ======== 叉积计算
def cross2d(u,v):
    return u[0] * v[1] - u[1] * v[0]

# =========  点在线段上

def point_on_segment(p,a,b,eps = 1e-10):
    return (min(a[0],b[0]) - eps <= p[0] <= max(a[0],b[0]) + eps and
            min(a[1],b[1]) - eps <= p[1] <= max(a[1],b[1]) + eps)

# ── 核心算法 ──────────────────────────────────────────────────────────────

def cross_product(p1, p2, p3):
    """
    计算三点叉积，判断折线在 p2 处的拐向。

    数学公式:
        a = P2 - P1,  b = P3 - P2
        cross = ax·by - ay·bx

    参数:
        p1, p2, p3: tuple (x, y)

    返回:
        (cross_value: float, direction: str)
        direction ∈ {"左转 ↰", "右转 ↱", "共线 →"}
    """
    ax_ = p2[0] - p1[0];  ay_ = p2[1] - p1[1]
    bx_ = p3[0] - p2[0];  by_ = p3[1] - p2[1]
    cross = ax_ * by_ - ay_ * bx_

    if   cross >  eps: direction = "左转 `↰`"
    elif cross < -eps: direction = "右转 ↱"
    else:              direction = "共线 →"
    return cross, direction


def analyze_all(points):
    """
    对折线所有内部顶点执行拐向分析。

    参数:
        points: list of (x, y)，至少 3 个点

    返回:
        list of dict，每项包含:
            index     : 顶点在 points 中的索引 (1 … n-2)
            cross_val : 叉积数值
            direction : 拐向字符串
    """
    results = []
    n = len(points)
    for i in range(1, n - 1):
        cross_val, direction = cross_product(
            points[i - 1], points[i], points[i + 1]
        )
        results.append({
            'index':     i,
            'cross_val': cross_val,
            'direction': direction,
        })
    return results




# ── 文件 I/O ──────────────────────────────────────────────────────────────

def load_points(filepath):
    """
    从 CSV/TXT 文件读取坐标点。
    每行格式: x,y（支持 # 注释行和表头自动跳过）

    返回:
        list of (x, y)

    异常:
        ValueError —— 若文件中无有效坐标
        IOError    —— 由调用方处理
    """
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
                continue   # 跳过表头或格式异常行

    if not new_points:
        raise ValueError("文件中没有找到有效坐标！")
    return new_points


def save_results(filepath, points):
    """
    将点坐标与拐向分析结果写入 CSV。

    参数:
        filepath : 保存路径（.csv）
        points   : list of (x, y)
    """
    result_map = {r['index']: r for r in analyze_all(points)}

    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        # utf-8-sig: 带 BOM 头，Excel 打开不乱码
        writer = csv.writer(f)
        writer.writerow(['点序号', 'X', 'Y', '拐向', '叉积值'])

        for i, (x, y) in enumerate(points):
            if i in result_map:
                r = result_map[i]
                writer.writerow([
                    f'P{i+1}', f'{x:.4f}', f'{y:.4f}',
                    r['direction'], f"{r['cross_val']:.6f}"
                ])
            else:
                writer.writerow([f'P{i+1}', f'{x:.4f}', f'{y:.4f}', '端点', '-'])




# 判断两线段是否相交

def segments_intersect(p1, p2, q1, q2, eps=1e-10):
    d1 = cross2d(vec(p1,p2),vec(p1,q1))
    d2 = cross2d(vec(p1,p2),vec(p1,q2))
    d3 = cross2d(vec(q1,q2),vec(q1,p1))
    d4 = cross2d(vec(q1,q2),vec(q1,p2))

    if d1*d2 < -eps and d3*d4 < -eps:
        return True
    if abs(d1) <= eps and point_on_segment(q1,p1,p2,eps):
        return True
    if abs(d2) <= eps and point_on_segment(q2,p1,p2,eps):
        return True
    if abs(d3) <= eps and point_on_segment(p1,q1,q2,eps):
        return True
    if abs(d4) <= eps and point_on_segment(p2,q1,q2,eps):
        return True
    
    return False

def segments_proper_intersect(p1, p2, q1, q2, eps=1e-10):
    d1 = cross2d(vec(p1,p2),vec(p1,q1))
    d2 = cross2d(vec(p1,p2),vec(p1,q2))
    d3 = cross2d(vec(q1,q2),vec(q1,p1))
    d4 = cross2d(vec(q1,q2),vec(q1,p2))    
    return d1*d2 < -eps and d3*d4 < -eps

# 判断点是否在矩形中

def rect_contains_point(rect, q):
    xmin,ymin,xmax,ymax = rect  # 赋值给元组
    return xmin <= q[0] <= xmax and ymin <= q[1] <= ymax

# 判断线段/折线/多边形是否在矩形中——因为矩形属于🤮多边形，所以只需要判断所有的点是否在矩形中

def segment_in_rect(rect, p1, p2): # 判断线段
    return rect_contains_point(rect,p1) and rect_contains_point(rect,p2)

def polyline_in_rect(rect, points): # 判断折线
    return all(rect_contains_point(rect,p) for p in points)

def polygon_in_rect(rect, vertices): # 判断多边形
    return all(rect_contains_point(rect,v) for v in vertices)

def rect_in_rect(outer, inner): # 判断矩形是否在矩形中
    return (outer[0] <= inner[0] and inner[2] <= outer[2] and inner[3] <= outer[3] and outer[1] <= inner[1])

def circle_in_rect(rect, center, radius): # 判断⚪是否在矩形内
    xmin,ymin,xmax,ymax = rect
    cx,cy = center
    return (cx - radius >= xmin and cx + radius <= xmax and cy - radius >= ymin and cy + radius <= ymax)




