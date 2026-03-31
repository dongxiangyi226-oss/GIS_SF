"""
turning_plot.py  ——  折线拐向绘图模块
Matplotlib 画布封装，负责所有可视化渲染，与 Tkinter 集成。
风格：Anthropic / Claude 暖色极简风。
"""
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import matplotlib.patches as patches


# ── 色板 ─────────────────────────────────────────────────────────────────

PALETTE = {
    'bg':          '#FAF9F6',
    'axes_bg':     '#FFFFFF',
    'grid':        '#E8E4DF',
    'text':        '#2D2D2D',
    'text_light':  '#8C8580',
    'accent':      '#D97757',
    'blue':        '#5B8DEF',
    'green':       '#4A8C6F',
    'red':         '#C45B4A',
    'amber':       '#D4943A',
    'purple':      '#7E6BAD',
    'teal':        '#3D8B8B',
    'brown':       '#8B6F5E',
    'pink':        '#C47A8F',
    'point_idle':  '#B0A99F',   # 未连接的点（灰色）
    'highlight':   '#D97757',   # 选中高亮
}

SEGMENT_COLORS = [
    PALETTE['blue'], PALETTE['accent'], PALETTE['green'],
    PALETTE['purple'], PALETTE['red'], PALETTE['teal'],
    PALETTE['amber'], PALETTE['brown'], PALETTE['pink'],
]

COLOR_MAP = {
    "左转 `↰`": PALETTE['green'],
    "右转 ↱":   PALETTE['red'],
    "共线 →":   PALETTE['amber'],
}


class CanvasWidget:
    """将 Matplotlib Figure 嵌入 Tkinter 的画布封装类。"""

    _DEFAULT_XLIM = (0, 200)
    _DEFAULT_YLIM = (0, 200)

    def __init__(self, parent):
        plt.rcParams.update({
            'font.sans-serif':     ['Microsoft YaHei', 'SimHei', 'Arial'],
            'axes.unicode_minus':  False,
            'figure.facecolor':    PALETTE['bg'],
            'axes.facecolor':      PALETTE['axes_bg'],
            'axes.edgecolor':      PALETTE['grid'],
            'axes.labelcolor':     PALETTE['text'],
            'xtick.color':         PALETTE['text_light'],
            'ytick.color':         PALETTE['text_light'],
            'grid.color':          PALETTE['grid'],
            'grid.alpha':          0.6,
            'grid.linestyle':      '--',
            'text.color':          PALETTE['text'],
        })

        self.fig, self._ax = plt.subplots(figsize=(7, 5), dpi=100)
        self.fig.subplots_adjust(left=0.08, right=0.95, top=0.93, bottom=0.08)
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible  = False
        self._ax.set_navigate(False)
        self._init_axes()

        self._canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True,
        )

    # ── 公开接口 ──────────────────────────────────────────────────────────

    @property
    def ax(self):
        return self._ax

    def connect(self, event_name, callback):
        return self._canvas.mpl_connect(event_name, callback)

    # ── 1) 基本绘制（采点 / 折线拐向） ───────────────────────────────────

    def redraw(self, points, *, lines_visible=False,
               analysis_results=None, xlim=None, ylim=None):
        self._ax.cla()
        self._ax.set_xlim(*(xlim or self._DEFAULT_XLIM))
        self._ax.set_ylim(*(ylim or self._DEFAULT_YLIM))
        self._ax.set_aspect('equal')
        self._ax.grid(True)

        if not points:
            self._ax.set_title(
                "Left click to add  |  Right click to undo",
                fontsize=10, color=PALETTE['text_light'], style='italic',
            )
            self._canvas.draw()
            return

        xs, ys = zip(*points)

        if lines_visible:
            self._ax.plot(
                xs, ys, '-', color=PALETTE['accent'],
                linewidth=1.8, alpha=0.8, zorder=1,
            )

        self._ax.scatter(
            xs, ys, c=PALETTE['accent'], s=55, zorder=2,
            edgecolors='white', linewidths=1.5,
        )
        self._draw_point_labels(points)

        if analysis_results:
            self._draw_analysis(points, analysis_results)

        self._ax.set_title(
            f"{len(points)} points", fontsize=10, color=PALETTE['text_light'],
        )
        self._canvas.draw()

    # ── 2) Link 模式绘制（点 + 已连线段 + 选中高亮） ─────────────────────

    def draw_link_mode(self, points, segments, selected_idx=None,
                       xlim=None, ylim=None):
        """
        Link 模式下的画布：显示所有点 + 已定义的线段 + 当前选中点的高亮。

        参数:
            points       : list of (x, y)
            segments     : list of (pi, pj)  pi/pj 是 points 中的索引
            selected_idx : 当前选中的点索引（高亮显示），None = 没选
        """
        self._ax.cla()
        self._ax.set_xlim(*(xlim or self._DEFAULT_XLIM))
        self._ax.set_ylim(*(ylim or self._DEFAULT_YLIM))
        self._ax.set_aspect('equal')
        self._ax.grid(True)

        if not points:
            self._canvas.draw()
            return

        # 找出哪些点已被某条线段使用
        linked = set()
        for pi, pj in segments:
            linked.add(pi)
            linked.add(pj)

        xs, ys = zip(*points)

        # 绘制已定义的线段
        for s_idx, (pi, pj) in enumerate(segments):
            c = SEGMENT_COLORS[s_idx % len(SEGMENT_COLORS)]
            ax_, ay_ = points[pi]
            bx_, by_ = points[pj]
            self._ax.plot(
                [ax_, bx_], [ay_, by_], '-',
                color=c, linewidth=2.5, alpha=0.85, zorder=2,
                label=f'S{s_idx+1} (P{pi+1}-P{pj+1})',
            )

        # 绘制所有点
        for i, (x, y) in enumerate(points):
            if i == selected_idx:
                # 选中点：大号橙色 + 光环
                self._ax.scatter(
                    [x], [y], c=PALETTE['highlight'], s=120, zorder=5,
                    edgecolors=PALETTE['highlight'], linewidths=2.5, alpha=0.3,
                )
                self._ax.scatter(
                    [x], [y], c=PALETTE['highlight'], s=55, zorder=6,
                    edgecolors='white', linewidths=1.5,
                )
            elif i in linked:
                # 已连接的点：用所属线段的颜色
                self._ax.scatter(
                    [x], [y], c=PALETTE['accent'], s=55, zorder=4,
                    edgecolors='white', linewidths=1.5,
                )
            else:
                # 空闲点：灰色
                self._ax.scatter(
                    [x], [y], c=PALETTE['point_idle'], s=45, zorder=3,
                    edgecolors='white', linewidths=1.5,
                )

        # 点号标注
        for i, (x, y) in enumerate(points):
            color = PALETTE['highlight'] if i == selected_idx else PALETTE['text']
            self._ax.annotate(
                f'P{i+1}', (x, y),
                textcoords="offset points", xytext=(8, 8),
                fontsize=9, fontweight='bold', color=color, zorder=7,
            )

        n_seg = len(segments)
        if selected_idx is not None:
            title = f"P{selected_idx+1} selected  —  click another point to link"
        else:
            title = f"{len(points)} points,  {n_seg} segments defined"

        self._ax.set_title(title, fontsize=10, color=PALETTE['text_light'])
        if segments:
            self._ax.legend(fontsize=8, framealpha=0.7, edgecolor=PALETTE['grid'])
        self._canvas.draw()

    # ── 3) 相交结果绘制 ──────────────────────────────────────────────────

    def draw_segments_intersection(self, points, segments, intersect_pairs):
        """
        绘制相交判断的结果。

        参数:
            points          : list of (x, y)  所有点坐标
            segments        : list of (pi, pj)  线段（点索引对）
            intersect_pairs : list of (si, sj)  相交的线段对索引
        """
        self._ax.cla()
        self._ax.set_aspect('equal')
        self._ax.grid(True)

        # 自适应坐标范围
        all_x = [points[i][0] for seg in segments for i in seg]
        all_y = [points[i][1] for seg in segments for i in seg]
        margin = max(
            (max(all_x) - min(all_x)),
            (max(all_y) - min(all_y)),
        ) * 0.15
        margin = max(margin, 5)
        self._ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        self._ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

        # 哪些线段参与了相交
        hit_set = set()
        for si, sj in intersect_pairs:
            hit_set.add(si)
            hit_set.add(sj)

        for s_idx, (pi, pj) in enumerate(segments):
            c  = SEGMENT_COLORS[s_idx % len(SEGMENT_COLORS)]
            ax_, ay_ = points[pi]
            bx_, by_ = points[pj]
            lw    = 2.8 if s_idx in hit_set else 1.8
            alpha = 1.0 if s_idx in hit_set else 0.5

            self._ax.plot(
                [ax_, bx_], [ay_, by_], '-o',
                color=c, linewidth=lw, alpha=alpha,
                markersize=7, markeredgecolor='white', markeredgewidth=1.5,
                label=f'S{s_idx+1} (P{pi+1}-P{pj+1})', zorder=3,
            )
            self._ax.annotate(
                f'P{pi+1}', (ax_, ay_), textcoords="offset points",
                xytext=(8, 8), fontsize=8, fontweight='bold', color=c, zorder=4,
            )
            self._ax.annotate(
                f'P{pj+1}', (bx_, by_), textcoords="offset points",
                xytext=(8, 8), fontsize=8, fontweight='bold', color=c, zorder=4,
            )

        # 相交标注
        for si, sj in intersect_pairs:
            pi1, pi2 = segments[si]
            pj1, pj2 = segments[sj]
            cx = (points[pi1][0] + points[pi2][0] +
                  points[pj1][0] + points[pj2][0]) / 4
            cy = (points[pi1][1] + points[pi2][1] +
                  points[pj1][1] + points[pj2][1]) / 4
            self._ax.annotate(
                f'S{si+1} \u00d7 S{sj+1}', (cx, cy),
                fontsize=10, fontweight='bold', color=PALETTE['red'],
                ha='center',
                bbox=dict(
                    boxstyle='round,pad=0.4', facecolor=PALETTE['red'],
                    alpha=0.12, edgecolor=PALETTE['red'], linewidth=0.8,
                ),
                zorder=5,
            )

        n_seg = len(segments)
        n_hit = len(intersect_pairs)
        self._ax.legend(fontsize=8, framealpha=0.7, edgecolor=PALETTE['grid'])
        self._ax.set_title(
            f"{n_seg} segments,  {n_hit} intersection{'s' if n_hit != 1 else ''}",
            fontsize=10, color=PALETTE['text_light'],
        )
        self._canvas.draw()

    # ── 内部方法 ──────────────────────────────────────────────────────────

    def _init_axes(self):
        self._ax.set_xlim(*self._DEFAULT_XLIM)
        self._ax.set_ylim(*self._DEFAULT_YLIM)
        self._ax.set_aspect('equal')
        self._ax.grid(True)
        self._ax.set_title(
            "Left click to add  |  Right click to undo",
            fontsize=10, color=PALETTE['text_light'], style='italic',
        )

    def _draw_point_labels(self, points):
        for i, (x, y) in enumerate(points):
            self._ax.annotate(
                f'P{i+1}', (x, y),
                textcoords="offset points", xytext=(8, 8),
                fontsize=9, fontweight='bold', color=PALETTE['text'], zorder=3,
            )
            self._ax.annotate(
                f'({x:.1f},{y:.1f})', (x, y),
                textcoords="offset points", xytext=(8, -12),
                fontsize=7, color=PALETTE['text_light'],
            )

    def _draw_analysis(self, points, analysis_results):
        for r in analysis_results:
            i         = r['index']
            x, y      = points[i]
            direction = r['direction']
            color     = COLOR_MAP.get(direction, PALETTE['text_light'])
            self._ax.annotate(
                direction, (x, y),
                textcoords="offset points", xytext=(-20, -22),
                fontsize=10, fontweight='bold', color=color,
                bbox=dict(
                    boxstyle='round,pad=0.3', facecolor=color,
                    alpha=0.12, edgecolor=color, linewidth=0.8,
                ),
                zorder=4,
            )
    # 绘制轴对齐矩形
    def draw_rect(self,rect,color = '#1565C0',label = None):
        xmin,ymin,xmax,ymax = rect
        width,height = xmax - xmin,ymax-ymin
        r = patches.Rectangle((xmin,ymin),width,height,
                              linewidth = 2,edgecolor = '#FF0000' ,
                              facecolor = color,alpha = 0.1)
        self._ax.add_patch(r)
        if label:
            self._ax.text(xmin + width/2,ymax + 1,label,
                          ha = 'center',fontsize = 9,color = color)
    
    # 绘制圆
    def draw_circle(self,center,radius,color = '#E65100',label = None):
        c = patches.Circle(center,radius,
                           linewidth = 2,edgecolor = color,
                           facecolor = color,alpha = 0.1)
        self._ax.add_patch(c)
        if label:
            self._ax.text(center[0],center[1] + radius + 1,label,
                          ha = 'center',fontsize = 9,color = color)