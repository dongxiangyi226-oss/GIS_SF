"""
zxpd1.py  ——  GIS 计算几何工具箱（入口）

组装 turning_algo（算法模块）和 turning_plot（绘图模块），
提供 Anthropic / Claude 风格的 Tkinter GUI 界面。

操作流程:
  1. Pick 模式: 左键放点, 右键撤销
  2. Link 模式: 点击任意两个已有点 → 连成一条线段
  3. Intersect Check: 检查所有已定义线段的两两相交关系
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt

from turning_algo import (
    analyze_all, load_points, save_results, segments_intersect,
)
from turning_plot import CanvasWidget, PALETTE


# ── Anthropic 风格色板 ──────────────────────────────────────────────────

BG          = '#FAF9F6'
BG_TOOLBAR  = '#F0EDE8'
BG_PANEL    = '#FFFFFF'
ACCENT      = '#D97757'
ACCENT_HVR  = '#C4654A'
TEXT        = '#1A1A1A'
TEXT_SEC    = '#8C8580'
BORDER      = '#E5E0DA'
GREEN       = '#4A8C6F'
RED         = '#C45B4A'
AMBER       = '#D4943A'

_TAG_MAP = {
    "左转 `↰`": 'left',
    "右转 ↱":   'right',
    "共线 →":   'collinear',
}


# ══════════════════════════════════════════════════════════════════════════
# 扁平按钮
# ══════════════════════════════════════════════════════════════════════════

class FlatButton(tk.Label):
    def __init__(self, parent, text, command=None, *,
                 fg=TEXT, bg=BG_TOOLBAR, hover_bg='#E6E1DA',
                 active_bg='#D9D3CB', font=None, padx=14, pady=6, **kw):
        font = font or ('Segoe UI', 9)
        super().__init__(
            parent, text=text, fg=fg, bg=bg,
            font=font, padx=padx, pady=pady, cursor='hand2', **kw,
        )
        self._command   = command
        self._bg        = bg
        self._hover_bg  = hover_bg
        self._active_bg = active_bg
        self.bind('<Enter>',           lambda e: self.config(bg=self._hover_bg))
        self.bind('<Leave>',           lambda e: self.config(bg=self._bg))
        self.bind('<ButtonPress-1>',   lambda e: self._press())
        self.bind('<ButtonRelease-1>', lambda e: self._release())

    def _press(self):
        self.config(bg=self._active_bg)

    def _release(self):
        self.config(bg=self._hover_bg)
        if self._command:
            self._command()

    def set_active(self, active):
        """切换按钮的选中态外观"""
        if active:
            self._bg = '#E6E1DA'
            self.config(bg='#E6E1DA')
        else:
            self._bg = BG_TOOLBAR
            self.config(bg=BG_TOOLBAR)


class AccentButton(FlatButton):
    def __init__(self, parent, text, command=None, **kw):
        super().__init__(
            parent, text=text, command=command,
            fg='#FFFFFF', bg=ACCENT, hover_bg=ACCENT_HVR,
            active_bg='#A8533C', font=('Segoe UI', 9, 'bold'), **kw,
        )

    def set_active(self, active):
        if active:
            self._bg = ACCENT_HVR
            self.config(bg=ACCENT_HVR)
        else:
            self._bg = ACCENT
            self.config(bg=ACCENT)


# ══════════════════════════════════════════════════════════════════════════
# 主应用类
# ══════════════════════════════════════════════════════════════════════════

class TurningApp:
    """GIS 计算几何工具箱"""

    # 吸附半径（数据坐标距离），Link 模式下点击多近算选中某个点
    SNAP_RADIUS = 8.0

    def __init__(self, root):
        self.root = root
        self.root.title('🌍 GIS Algorithms  —  Computational Geometry')
        self.root.geometry('1200x750')
        self.root.minsize(900, 550)
        self.root.configure(bg=BG)

        # ── 数据状态 ──
        self.points           = []       # 所有点 [(x,y), ...]
        self.segments         = []       # 已定义线段 [(pi, pj), ...]  索引对
        self.analysis_results = []
        self.mode             = 'pick'   # 'pick' | 'drag' | 'link'
        self.lines_visible    = False
        self.analyzed         = False
        self.drag_index       = None
        self.drag_threshold   = 0.3
        self.link_first       = None     # Link 模式：第一个选中点的索引
        self.xlim             = None
        self.ylim             = None

        # ── 搭建界面 ──
        self._build_toolbar()
        self._build_body()
        self._build_statusbar()
        self._bind_events()

    # ══════════════════════════════════════════════════════════════════════
    # 界面搭建
    # ══════════════════════════════════════════════════════════════════════

    def _build_toolbar(self):
        toolbar = tk.Frame(self.root, bg=BG_TOOLBAR, pady=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        left = tk.Frame(toolbar, bg=BG_TOOLBAR)
        left.pack(side=tk.LEFT, padx=8)

        # 三个模式按钮
        self.btn_pick = FlatButton(left, ' 📌 Pick ', self._mode_pick)
        self.btn_pick.pack(side=tk.LEFT, padx=2, pady=4)
        self.btn_pick.set_active(True)

        self.btn_drag = FlatButton(left, ' ✋ Drag ', self._mode_drag)
        self.btn_drag.pack(side=tk.LEFT, padx=2, pady=4)

        self.btn_link = FlatButton(left, ' 🔗 Link ', self._mode_link)
        self.btn_link.pack(side=tk.LEFT, padx=2, pady=4)

        # 分隔
        tk.Frame(left, width=1, bg=BORDER).pack(
            side=tk.LEFT, fill=tk.Y, padx=10, pady=6)

        FlatButton(left, ' 📐 Connect ', self.connect_lines).pack(
            side=tk.LEFT, padx=2, pady=4)
        AccentButton(left, ' 🔍 Analyze ', self.analyze_turning).pack(
            side=tk.LEFT, padx=2, pady=4)
        AccentButton(left, ' ✂️ Intersect ', self.check_intersection).pack(
            side=tk.LEFT, padx=2, pady=4)

        # 分隔
        tk.Frame(left, width=1, bg=BORDER).pack(
            side=tk.LEFT, fill=tk.Y, padx=10, pady=6)

        FlatButton(left, ' 📂 Import ', self.import_points).pack(
            side=tk.LEFT, padx=2, pady=4)
        FlatButton(left, ' 💾 Export ', self.export_results).pack(
            side=tk.LEFT, padx=2, pady=4)

        # 右侧
        right = tk.Frame(toolbar, bg=BG_TOOLBAR)
        right.pack(side=tk.RIGHT, padx=8)
        FlatButton(right, ' 🗑️ Clear ', self.clear_all, fg=RED).pack(
            side=tk.RIGHT, padx=2, pady=4)

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=(8, 0))

        canvas_frame = tk.Frame(body, bg=BORDER)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        canvas_inner = tk.Frame(canvas_frame, bg=BG_PANEL)
        canvas_inner.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        self.canvas_widget = CanvasWidget(canvas_inner)

        panel = tk.Frame(body, bg=BG, width=260)
        panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(12, 0))
        panel.pack_propagate(False)

        tk.Label(
            panel, text='📋 Results', bg=BG,
            font=('Segoe UI', 11, 'bold'), fg=TEXT, anchor=tk.W,
        ).pack(fill=tk.X, pady=(0, 6))

        result_border = tk.Frame(panel, bg=BORDER)
        result_border.pack(fill=tk.BOTH, expand=True)

        self.result_text = tk.Text(
            result_border, width=28, font=('Consolas', 10),
            state=tk.DISABLED, bg=BG_PANEL, fg=TEXT,
            bd=0, padx=12, pady=10, wrap=tk.WORD, relief=tk.FLAT,
            selectbackground=ACCENT, selectforeground='white',
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.result_text.tag_config('left',      foreground=GREEN)
        self.result_text.tag_config('right',     foreground=RED)
        self.result_text.tag_config('collinear', foreground=AMBER)
        self.result_text.tag_config('header', font=('Segoe UI', 10, 'bold'),
                                    foreground=TEXT)
        self.result_text.tag_config('hit',  foreground=RED,
                                    font=('Consolas', 10, 'bold'))
        self.result_text.tag_config('miss', foreground=TEXT_SEC)
        self.result_text.tag_config('info', foreground=TEXT_SEC,
                                    font=('Consolas', 9))

    def _build_statusbar(self):
        tk.Frame(self.root, bg=BORDER, height=1).pack(
            side=tk.BOTTOM, fill=tk.X)
        self.statusbar = tk.Label(
            self.root, text='✨ Ready  ·  📌 Pick mode  ·  0 points',
            bg=BG, fg=TEXT_SEC, anchor=tk.W,
            font=('Segoe UI', 9), padx=16, pady=6,
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _update_status(self, text):
        n = len(self.points)
        s = len(self.segments)
        self.statusbar.config(
            text=f"{text}  ·  {n} points  ·  {s} segments"
        )

    # ══════════════════════════════════════════════════════════════════════
    # 模式切换
    # ══════════════════════════════════════════════════════════════════════

    def _set_mode_buttons(self, active_btn):
        for btn in (self.btn_pick, self.btn_drag, self.btn_link):
            btn.set_active(btn is active_btn)

    def _mode_pick(self):
        self.mode = 'pick'
        self.link_first = None
        self._set_mode_buttons(self.btn_pick)
        self._redraw()
        self._update_status("📌 Pick mode  ·  Left = add, Right = undo")

    def _mode_drag(self):
        self.mode = 'drag'
        self.link_first = None
        self._set_mode_buttons(self.btn_drag)
        self._redraw()
        self._update_status("✋ Drag mode  ·  Click and drag points")

    def _mode_link(self):
        self.mode = 'link'
        self.link_first = None
        self._set_mode_buttons(self.btn_link)
        self._redraw_link()
        self._update_status("🔗 Link mode  ·  Click two points to form a segment")

    # ══════════════════════════════════════════════════════════════════════
    # 鼠标事件
    # ══════════════════════════════════════════════════════════════════════

    def _bind_events(self):
        self.canvas_widget.connect('button_press_event',   self._on_press)
        self.canvas_widget.connect('motion_notify_event',  self._on_motion)
        self.canvas_widget.connect('button_release_event', self._on_release)

    def _on_press(self, event):
        if event.inaxes != self.canvas_widget.ax:
            return
        if self.mode == 'pick':
            self._handle_pick(event)
        elif self.mode == 'drag':
            self._handle_drag_start(event)
        elif self.mode == 'link':
            self._handle_link(event)

    def _handle_pick(self, event):
        if event.button == 1:
            self.points.append((event.xdata, event.ydata))
            self.lines_visible    = False
            self.analyzed         = False
            self.analysis_results = []
            self._redraw()
            self._update_status("Pick mode  ·  Left = add, Right = undo")
        elif event.button == 3:
            self._handle_undo()

    def _handle_undo(self):
        if not self.points:
            self._update_status("Nothing to undo")
            return
        removed_idx = len(self.points) - 1
        removed = self.points.pop()
        # 删除引用了该点的线段，并修正索引
        new_segs = []
        for pi, pj in self.segments:
            if pi == removed_idx or pj == removed_idx:
                continue
            new_segs.append((pi, pj))
        self.segments = new_segs
        self.lines_visible    = False
        self.analyzed         = False
        self.analysis_results = []
        self._redraw()
        self._update_status(
            f"Undid P{removed_idx+1} ({removed[0]:.1f}, {removed[1]:.1f})"
        )

    def _handle_link(self, event):
        """Link 模式：点击已有点进行配对。"""
        if event.button == 3:
            # 右键：取消选中 / 删除最后一条线段
            if self.link_first is not None:
                self.link_first = None
                self._redraw_link()
                self._update_status("Link mode  ·  Selection cancelled")
            elif self.segments:
                removed = self.segments.pop()
                self._redraw_link()
                self._update_status(
                    f"Link mode  ·  Removed S{len(self.segments)+1} "
                    f"(P{removed[0]+1}-P{removed[1]+1})"
                )
            return

        if event.button != 1:
            return

        # 找最近的点
        idx = self._find_nearest_point(event.xdata, event.ydata)
        if idx is None:
            self._update_status("Link mode  ·  Click closer to an existing point")
            return

        if self.link_first is None:
            # 第一次点击：选中
            self.link_first = idx
            self._redraw_link()
            self._update_status(
                f"Link mode  ·  P{idx+1} selected, click another point"
            )
        else:
            # 第二次点击：配对成线段
            if idx == self.link_first:
                self._update_status("Link mode  ·  Same point, pick a different one")
                return

            new_seg = (self.link_first, idx)
            # 检查是否已存在相同线段
            for pi, pj in self.segments:
                if (pi == new_seg[0] and pj == new_seg[1]) or \
                   (pi == new_seg[1] and pj == new_seg[0]):
                    self.link_first = None
                    self._redraw_link()
                    self._update_status("Link mode  ·  Segment already exists")
                    return

            self.segments.append(new_seg)
            s_idx = len(self.segments)
            self.link_first = None
            self._redraw_link()
            self._update_status(
                f"Link mode  ·  S{s_idx} = P{new_seg[0]+1}-P{new_seg[1]+1} created"
            )

    def _find_nearest_point(self, x, y):
        """找距离 (x, y) 最近的点，在吸附半径内则返回索引，否则 None。"""
        if not self.points:
            return None
        click = np.array([x, y])
        pts   = np.array(self.points)
        dists = np.linalg.norm(pts - click, axis=1)
        min_idx = int(np.argmin(dists))

        # 动态吸附半径：取坐标范围的 3%
        ax = self.canvas_widget.ax
        x_range = ax.get_xlim()[1] - ax.get_xlim()[0]
        y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
        snap = max(x_range, y_range) * 0.04

        if dists[min_idx] < snap:
            return min_idx
        return None

    def _handle_drag_start(self, event):
        if event.button != 1 or not self.points:
            return
        click     = np.array([event.xdata, event.ydata])
        pts       = np.array(self.points)
        distances = np.linalg.norm(pts - click, axis=1)
        min_idx   = np.argmin(distances)
        self.drag_index = min_idx if distances[min_idx] < self.drag_threshold else None

    def _on_motion(self, event):
        if self.mode != 'drag' or self.drag_index is None:
            return
        if event.inaxes != self.canvas_widget.ax:
            return
        self.points[self.drag_index] = (event.xdata, event.ydata)
        self._redraw()

    def _on_release(self, event):
        if self.mode == 'drag' and self.drag_index is not None:
            self.drag_index = None
            if self.analyzed:
                self.analyze_turning()

    # ══════════════════════════════════════════════════════════════════════
    # 画面刷新
    # ══════════════════════════════════════════════════════════════════════

    def _redraw(self):
        """Pick / Drag 模式下的标准绘制"""
        self.canvas_widget.redraw(
            self.points,
            lines_visible    = self.lines_visible,
            analysis_results = self.analysis_results if self.analyzed else None,
            xlim             = self.xlim,
            ylim             = self.ylim,
        )

    def _redraw_link(self):
        """Link 模式下的绘制：显示点 + 已定义线段 + 选中高亮"""
        self.canvas_widget.draw_link_mode(
            self.points, self.segments,
            selected_idx=self.link_first,
            xlim=self.xlim, ylim=self.ylim,
        )

    # ══════════════════════════════════════════════════════════════════════
    # 业务逻辑
    # ══════════════════════════════════════════════════════════════════════

    def connect_lines(self):
        if len(self.points) < 2:
            messagebox.showwarning("Notice", "Need at least 2 points.")
            return
        self.lines_visible = True
        self._redraw()
        self._update_status("Lines connected")

    def analyze_turning(self):
        if len(self.points) < 3:
            messagebox.showwarning("Notice", "Need at least 3 points.")
            return
        self.lines_visible    = True
        self.analyzed         = True
        self.analysis_results = analyze_all(self.points)
        self._redraw()
        self._update_result_turning()
        self._update_status("Analysis complete  ·  Drag points to update")

    def check_intersection(self):
        """检查所有已定义线段的两两相交关系"""
        if len(self.segments) < 2:
            messagebox.showwarning(
                "Notice",
                "Need at least 2 segments.\n\n"
                "How to define segments:\n"
                "  1. Pick mode: place points\n"
                "  2. Link mode: click two points to link them\n"
                "  3. Click [Intersect Check]"
            )
            return

        # 两两检查
        intersect_pairs = []
        for i in range(len(self.segments)):
            for j in range(i + 1, len(self.segments)):
                pi1, pi2 = self.segments[i]
                pj1, pj2 = self.segments[j]
                a1, a2 = self.points[pi1], self.points[pi2]
                b1, b2 = self.points[pj1], self.points[pj2]
                if segments_intersect(a1, a2, b1, b2):
                    intersect_pairs.append((i, j))

        # 绘制结果
        self.canvas_widget.draw_segments_intersection(
            self.points, self.segments, intersect_pairs,
        )

        # 结果面板
        self._update_result_intersection(intersect_pairs)
        self._update_status(
            f"{len(self.segments)} segments,  "
            f"{len(intersect_pairs)} intersection(s)"
        )

    # ── 结果面板更新 ──────────────────────────────────────────────────────

    def _update_result_turning(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, "🔍 Turning Analysis\n\n", 'header')
        for r in self.analysis_results:
            i   = r['index']
            tag = _TAG_MAP.get(r['direction'], '')
            self.result_text.insert(
                tk.END,
                f"  P{i}\u2192P{i+1}\u2192P{i+2}   {r['direction']}\n", tag,
            )
        self.result_text.insert(tk.END, "\n📐 Cross Products\n\n", 'header')
        for r in self.analysis_results:
            i    = r['index']
            tag  = _TAG_MAP.get(r['direction'], '')
            sign = "+" if r['cross_val'] >= 0 else ""
            self.result_text.insert(
                tk.END, f"  P{i+1}:  {sign}{r['cross_val']:.4f}\n", tag,
            )
        self.result_text.config(state=tk.DISABLED)

    def _update_result_intersection(self, intersect_pairs):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, "✂️ Intersection Check\n\n", 'header')

        # 线段列表
        self.result_text.insert(tk.END, "📏 Segments:\n", 'info')
        for s_idx, (pi, pj) in enumerate(self.segments):
            a, b = self.points[pi], self.points[pj]
            self.result_text.insert(
                tk.END,
                f"  S{s_idx+1}  P{pi+1}({a[0]:.0f},{a[1]:.0f})"
                f" \u2192 P{pj+1}({b[0]:.0f},{b[1]:.0f})\n",
                'info',
            )

        self.result_text.insert(tk.END, "\n")

        # 两两结果
        n = len(self.segments)
        for i in range(n):
            for j in range(i + 1, n):
                if (i, j) in intersect_pairs:
                    self.result_text.insert(
                        tk.END, f"  S{i+1} \u00d7 S{j+1}  ✅ intersect\n", 'hit',
                    )
                else:
                    self.result_text.insert(
                        tk.END, f"  S{i+1} \u00d7 S{j+1}  ❌ no\n", 'miss',
                    )

        self.result_text.insert(tk.END, "\n")
        hit   = len(intersect_pairs)
        total = n * (n - 1) // 2
        self.result_text.insert(
            tk.END, f"  {hit}/{total} pairs intersect\n", 'header',
        )
        self.result_text.config(state=tk.DISABLED)

    # ── 清空 / 导入 / 导出 ───────────────────────────────────────────────

    def clear_all(self):
        if self.points or self.segments:
            if not messagebox.askyesno("Confirm", "Clear all points and segments?"):
                return
        self.points.clear()
        self.segments.clear()
        self.analysis_results.clear()
        self.lines_visible = False
        self.analyzed      = False
        self.drag_index    = None
        self.link_first    = None
        self.xlim          = None
        self.ylim          = None

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self.result_text.config(state=tk.DISABLED)

        self._redraw()
        self._update_status("Cleared  ·  Pick mode")

    def import_points(self):
        filepath = filedialog.askopenfilename(
            title="Import Points",
            filetypes=[("CSV", "*.csv"), ("Text", "*.txt"), ("All", "*.*")],
            initialdir=".",
        )
        if not filepath:
            return
        try:
            new_points = load_points(filepath)
            xs, ys = zip(*new_points)
            margin = max(
                (max(xs) - min(xs)) * 0.15,
                (max(ys) - min(ys)) * 0.15, 0.5,
            )
            self.xlim             = (min(xs) - margin, max(xs) + margin)
            self.ylim             = (min(ys) - margin, max(ys) + margin)
            self.points           = new_points
            self.segments.clear()
            self.lines_visible    = False
            self.analyzed         = False
            self.analysis_results = []
            self.link_first       = None
            self._redraw()
            self._update_status(f"Imported {len(self.points)} points")
        except ValueError as e:
            messagebox.showwarning("Notice", str(e))
        except Exception as e:
            messagebox.showerror("Import Error", f"Error reading file:\n{e}")

    def export_results(self):
        if not self.points:
            messagebox.showwarning("Notice", "No data to export.")
            return
        filepath = filedialog.asksaveasfilename(
            title="Export Results", defaultextension=".csv",
            filetypes=[("CSV", "*.csv")], initialfile="turning_result.csv",
        )
        if not filepath:
            return
        try:
            save_results(filepath, self.points)
            self._update_status(f"Exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error saving:\n{e}")


# ══════════════════════════════════════════════════════════════════════════

def main():
    root = tk.Tk()
    TurningApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
