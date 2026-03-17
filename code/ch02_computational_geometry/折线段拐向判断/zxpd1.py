## ===== 依赖 ==== ##
import tkinter as tk
from tkinter import filedialog,messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import(
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from matplotlib.patches import FancyArrowPatch
import csv

## =======  窗口初始化  =========

class TurningApp:
    def __init__(self,root):
        #——保存 Tkinter 根窗口引用——
        self.root = root
        self.root.title('📐 折线段拐向判断——向量叉积法')    # 窗口标题

        self.root.geometry('1100x700')  # 初始化窗口大小
        self.root.minsize(800,500)  # 最小可缩放尺寸，防止被挤压

        # 数据状态变量

        self.points = []  #存储采点
        self.mode = 'pick' # pick采点，drag拖动
        self.lines_visible = False

        self.analyzed = False
        self.drag_index = None
        self.drag_threshold = 0.3 # 拖动吸附阈值

        # 搭建界面
        self._build_toolbar()
        self._build_canvas()
        self._build_result_panel()
        self._build_statusbar()
        self._bind_events()

    ## ====== 工具栏搭建 =======

    def _build_toolbar(self):
        # 创建工具栏容器
        toolbar = tk.Frame(
            self.root,
            bd = 1, #边框宽度1像素
            relief = tk.RAISED # 边框样式：凸起效果，看起来像工具栏
        )

        toolbar.pack(
            side = tk.TOP, # 放在窗口顶部
            fill = tk.X  # 水平方向填满窗口宽度
        )

        # # ── 按钮样式配置 ──
        btn_cfg = {
            'padx':8,
            'pady':4,
            'font': ('Microsoft YaHei',9)
        }

        # ── 逐个创建按钮 ──
        # 📌 采点模式按钮
        self.btn_pick = tk.Button(
            toolbar,
            text = '📌 采点',   # 按钮显示文字
            command = self._mode_pick,  # 点击时调用的方法
            relief = tk.SUNKEN, # 初始状态为按下
            **btn_cfg
        )
        self.btn_pick.pack(side = tk.LEFT,padx = 2) # 靠左排列，按钮间距2px

        # ✋ 拖动模式按钮
        self.btn_drag = tk.Button(
            toolbar,
            text = '✋ 拖动',
            command = self._mode_drag, # 点击后执行拖动
            **btn_cfg
        )
        self.btn_drag.pack(side = tk.LEFT,padx = 2)

        # 📐 连线按钮
        tk.Button(
            toolbar,
            text = '📐 连线',
            command = self.connect_lines,  # 点击后执行连线
            **btn_cfg
        ).pack(side = tk.LEFT,padx = 2)

        # 🔍 分析拐向按钮
        tk.Button(
            toolbar,
            text = '🔍 分析拐向',
            command = self.analyze_turning, # 点击后在执行拐向分析
            **btn_cfg
        ).pack(side = tk.LEFT,padx = 2)

        # ── 分隔线 ──
        # Separator 用竖线分隔"操作按钮"和"文件按钮"
        ttk_sep = tk.Frame(toolbar,width = 2,bd = 1,relief = tk.SUNKEN)
        ttk_sep.pack(side = tk.LEFT,fill = tk.Y,padx = 6,pady = 2)

        # 📂 导入坐标文件按钮
        tk.Button(
            toolbar,
            text = '📂 导入',
            command = self.import_points,
            **btn_cfg
        ).pack(side = tk.LEFT,padx = 2)

        # 💾 导出结果按钮
        tk.Button(
            toolbar,
            text = '💾 导出',
            command = self.export_results,
            **btn_cfg
        ).pack(side = tk.LEFT,padx = 2)

        # 🗑️ 清空按钮（放最右边，用红色警示）
        tk.Button(
            toolbar,
            text = '🗑️ 清空',
            command = self.clear_all,
            fg = 'red', # 红色文字，危险操作
            **btn_cfg
        ).pack(side = tk.RIGHT,padx = 2)

    def _mode_pick(self):
        """切换到采点模式"""
        self.mode = 'pick' # 设置模式标志
        self.btn_pick.config(relief = tk.SUNKEN)  # 采点按钮显示"按下"状态
        self.btn_drag.config(relief = tk.RAISED)  # 拖动按钮显示"弹起"状态
        self._update_status("模式: 采点 | 左键点击画布采点,右键撤销")

    def _mode_drag(self):
        """切换到拖动模式"""
        self.mode = 'drag'
        self.btn_pick.config(relief = tk.RAISED)
        self.btn_drag.config(relief = tk.SUNKEN)
        self._update_status("模式: 拖动 | 左键按住拖动已有的点")

    # =========  Matplotlib画布嵌入  ============
    def _build_canvas(self):
        """创建 Matplotlib Figure 并嵌入 Tkinter 窗口"""
        # ── 创建中部容器 ──
        # 这个 Frame 水平排列"画布"和"结果面板"
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(
            side = tk.TOP, # 紧接工具栏下方
            fill = tk.BOTH, # 水平 + 垂直都填满
            expand = True   # 窗口缩放时，这个区域跟着缩放
        )

        # —— 创建 Matplotlib Figure 和 Axes ──

        self.fig,self.ax = plt.subplots(
            figsize = (7,5),
            dpi = 100
        )
        self.fig.subplots_adjust(
            left = 0.08,
            right = 0.95,
            top = 0.95,
            bottom = 0.08
        )

        # ── 初始化坐标轴 ──
        self.ax.set_xlim(0,200)
        self.ax.set_ylim(0,200)
        self.ax.set_aspect('equal')  # 等比例坐标轴
        self.ax.grid(True,linestyle = '--',alpha = 0.3) # 显示网格线: 虚线, 30%透明度
        self.ax.set_title("左键采点 | 右键撤销",fontsize = 10,color = 'gray')

        # ── 把 Figure 嵌入 Tkinter ──
        # FigureCanvasTkAgg 是 Matplotlib 与 Tkinter 的桥梁
        self.canvas = FigureCanvasTkAgg(
            self.fig,  # 要嵌入的 Matplotlib Figure 对象
            master = self.main_frame  # 嵌入到哪个 Tkinter 容器中
        )

        # 关闭 Matplotlib 默认的导航工具栏交互（缩放/平移），防止点击时出现选区框
        self.fig.canvas.toolbar_visible = False
        self.fig.canvas.header_visible = False
        self.ax.set_navigate(False)

        # draw() 首次渲染画布
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(
            side = tk.LEFT,
            fill = tk.BOTH,
            expand = True
        )

    # ======== 右侧结果面板 =========

    def _build_result_panel(self):
        """创建右侧的分析结果显示面板"""

        # ---- 结果面板容器 ----
        result_frame = tk.LabelFrame(
            self.main_frame,
            text = ' 📋 分析结果 ',
            font = ('Microsoft YaHei', 10, 'bold'),
            padx = 5,
            pady = 5
        )
        result_frame.pack(
            side = tk.RIGHT,
            fill = tk.Y,
            padx = (0,5),
            pady = 5
        )

        # ── 结果文本框 ──
        self.result_text = tk.Text(
            result_frame,
            width = 28,
            font = ('Consolas',10),
            state = tk.DISABLED,
            bg = '#FAFAFA',
            wrap = tk.WORD
        )
        self.result_text.pack(fill = tk.BOTH,expand = True)

        # —— 为结果文本定义颜色标签 ——
        # Tkinter Text  控件可以给不同文字片段设置不同的样式（通过tag)

        self.result_text.tag_config('left',    foreground = '#2E7D32') # 左转——绿色
        self.result_text.tag_config('right',    foreground = '#C62828') # 右转——红色
        self.result_text.tag_config('collinear',    foreground = '#F57F17') # 共线——黄色
        self.result_text.tag_config('header',    font = ('Microsoft YaHei', 10, 'bold')) # 标题加粗

    # ==========  底部状态栏  ============
    def _build_statusbar(self):
        """创建底部状态栏"""
        self.statusbar = tk.Label(
            self.root,
            text = '📍 模式: 采点 | 已采集 0 个点 | 左键点击画布采点',
            bd = 1,  # 边框宽度
            relief = tk.SUNKEN,  # 凹陷边框（状态栏经典样式）
            anchor = tk.W,
            font = ('Microsoft YaHei', 9),
            padx= 10
        )
        self.statusbar.pack(
            side = tk.BOTTOM,
            fill = tk.X
        )

    def _update_status(self, text):
        """更新状态栏文字的便捷方法"""
        # 拼接上点数信息
        n = len(self.points)
        full_text = f"📍 {text} | 已采集 {n} 个点"
        self.statusbar.config(text = full_text) # config() 可动态修改控件属性

    # ========= 鼠标事件绑定 ==========
    def _bind_events(self):
        """将 Matplotlib 画布的鼠标事件连接到对应处理方法"""

        # Matplotlib 有自己的事件系统，用 mpl_connect 注册回调函数
        # 注意: 这里绑定的是 Matplotlib 的 figure canvas，不是 Tkinter 的

        # 鼠标按下事件 —— 用于采点 和 开始拖动
        self.canvas.mpl_connect(
            'button_press_event',
            self._on_press
        )

        # 鼠标移动事件 —— 用于拖动过程中实时更新点的位置
        self.canvas.mpl_connect(
            'motion_notify_event',
            self._on_motion
        )

        # 鼠标释放事件 —— 用于结束拖动
        self.canvas.mpl_connect(
            'button_release_event',
            self._on_release
        )

    # ========= 采点逻辑 =============
    def _on_press(self, event):
        """
        鼠标按下事件的统一入口。
        根据当前模式(self.mode)分发到采点或拖动。
        """

        # ── 前置检查 ──
        if event.inaxes != self.ax:
            # 鼠标不在坐标轴区域内（比如点在了边框上），直接忽略
            return
        if self.mode == 'pick':
            # -- 采点模式
            self._handle_pick(event)
        elif self.mode == 'drag':
            # 拖动模式
            self._handle_drag_start(event)

    def _handle_pick(self,event):
        """采点模式下的鼠标按下处理"""
        if event.button == 1:
            # 左键—添加新点
            x,y = event.xdata,event.ydata  # 获取点击位置的坐标数据

            self.points.append((x,y)) # 加入点列表
            self.lines_visible = False # 新增点后，之前的连线作废
            self.analyzed = False  # 分析结果作废

            self._redraw()   # 重绘画布
            self._update_status("模式: 采点 | 左键采点，右键撤销")

        elif event.button == 3:
            self._handle_undo()

    # ========= 撤销逻辑 =============
    def _handle_undo(self):
        """撤销最后一个采集的点"""
        if not self.points:
            # 点列表已空
            self._update_status("没有可撤销的点")
            return
        removed = self.points.pop()
        self.lines_visible = False
        self.analyzed = False

        self._redraw()
        self._update_status(
            f"已撤销 ({removed[0]:.1f}, {removed[1]:.1f}) | 右键继续撤销"
        )

    # =========  拖动点逻辑 ===========
    def _handle_drag_start(self, event):
        """
        拖动模式下鼠标按下: 找到最近的点，开始拖动。
        """
        if event.button != 1 or not self.points:
            return
        # ── 找到离鼠标最近的点 ──
        click = np.array([event.xdata,event.ydata])
        pts = np.array(self.points)
        distances = np.linalg.norm(pts - click,axis = 1) # 计算欧氏距离
        min_idx = np.argmin(distances)
        min_dist = distances[min_idx]

        if min_dist < self.drag_threshold:
            self.drag_index = min_idx
        else:
            self.drag_index = None

    def _on_motion(self, event):
        """
        鼠标移动事件: 拖动过程中实时更新点的位置。
        """
        # 前置检查: 必须在拖动模式 + 已选中某个点 + 鼠标在坐标轴内
        if self.mode != 'drag':
            return
        if self.drag_index is None:
            return
        if event.inaxes != self.ax:
            return

        # ── 更新点坐标 ──
        self.points[self.drag_index] = (event.xdata, event.ydata)

        # ── 实时重绘 ──
        # 拖动时需要保持连线和分析标注（如果之前已经画了的话）
        self._redraw()

    def _on_release(self, event):
        """
        鼠标释放事件: 结束拖动。
        """
        if self.mode == 'drag' and self.drag_index is not None:
            self.drag_index = None             # 清除拖动状态
            # 如果之前分析过，拖动后自动重新分析
            if self.analyzed:
                self.analyze_turning()

    # ======  画布重绘 =========
    def _redraw(self):
        """
        清空画布并重新绘制所有元素。
        这是画面更新的核心方法，几乎所有操作后都要调用。
        """

        self.ax.cla()  # cla() = clear axes，清空当前坐标轴上的所有内容

        # ── 恢复坐标轴设置（因为 cla() 会把设置也清掉） ──
        self.ax.set_xlim(0, 200)
        self.ax.set_ylim(0, 200)
        self.ax.set_aspect('equal')
        self.ax.grid(True, linestyle='--', alpha=0.3)

        if not self.points:
            # 没有点，显示提示
            self.ax.set_title("左键采点 | 右键撤销", fontsize=10, color='gray')
            self.canvas.draw()     # 触发 Matplotlib 重绘
            return

        # ── 提取所有点的 x, y 坐标 ──
        # zip(*self.points) 把 [(x1,y1),(x2,y2),...] 转置为 [(x1,x2,...), (y1,y2,...)]
        xs, ys = zip(*self.points)

        # ── 画连线（如果已连线） ──
        if self.lines_visible:
            self.ax.plot(
                xs, ys,                # x坐标列表, y坐标列表
                '-',                   # 线型: 实线
                color='#1565C0',       # 深蓝色
                linewidth=1.5,         # 线宽 1.5
                zorder=1               # 图层顺序: 1（在点的下面）
            )

        # ── 画所有点 ──
        self.ax.scatter(
            xs, ys,
            c='red',                   # 红色点
            s=60,                      # 点大小 60
            zorder=2,                  # 图层 2（在线的上面）
            edgecolors='darkred',      # 点边框深红色
            linewidths=1               # 边框宽度
        )

        # ── 标注点号 ──
        for i, (x, y) in enumerate(self.points):
            self.ax.annotate(
                f'P{i+1}',            # 标注文字: P1, P2, P3, ...
                (x, y),               # 标注目标位置
                textcoords="offset points",  # 偏移单位是"点"（像素级）
                xytext=(8, 8),         # 标注文字相对于目标点偏移 (右8, 上8) 像素
                fontsize=9,
                fontweight='bold',
                color='#333333',       # 深灰色
                zorder=3               # 图层 3（最上层）
            )

        # ── 显示坐标值 ──
        for i, (x, y) in enumerate(self.points):
            self.ax.annotate(
                f'({x:.1f},{y:.1f})',  # 坐标文字，保留 1 位小数
                (x, y),
                textcoords="offset points",
                xytext=(8, -12),       # 在点号下方
                fontsize=7,
                color='#777777'        # 浅灰色，不喧宾夺主
            )

        # ── 更新标题 ──
        self.ax.set_title(
            f"共 {len(self.points)} 个点",
            fontsize=10, color='gray'
        )

        # ── 触发画布重绘 ──
        self.canvas.draw()

    # ========= 连线功能 =========
    def connect_lines(self):
        """将所有点按顺序用折线连接"""

        if len(self.points) < 2:
            messagebox.showwarning("提示", "至少需要 2 个点才能连线！")
            return
        self.lines_visible = True
        self._redraw()
        self._update_status("已连线 | 点击 [🔍分析拐向] 进行分析")

    # ========= 叉积计算 =========
    @staticmethod
    def cross_product(p1,p2,p3):
        """
        计算三个连续点处的向量叉积，判断拐向。

        参数:
            p1: tuple (x, y) —— 前一个点
            p2: tuple (x, y) —— 当前拐点
            p3: tuple (x, y) —— 后一个点

        返回:
            (cross_value, direction_str)
            cross_value: float，叉积数值
            direction_str: str，"左转 ↰" / "右转 ↱" / "共线 →"

        数学公式:
            a = P2 - P1    b = P3 - P2
            cross = a x b = (ax)(by) - (ay)(bx)
                  = (p2[0]-p1[0]) * (p3[1]-p2[1])
                  - (p2[1]-p1[1]) * (p3[0]-p2[0])
        """
        # 向量 a = P2 - P1 的分量
        ax = p2[0] - p1[0]
        ay = p2[1] - p1[1]

        # 向量 b = P3 - P2 的分量
        bx = p3[0] - p2[0]
        by = p3[1] - p2[1]

        # 叉积计算
        cross = ax * by - ay * bx

        # 判断方向
        # 使用一个小的容差值(epsilon)，避免浮点误差导致的误判

        eps = 1e-10

        if cross > eps:
            direction = "左转 ↰"   # 逆时针方向
        elif cross < -eps:
            direction = "右转 ↱"   # 顺时针方向
        else:
            direction = "共线 →"   # 三点共线
        return cross,direction

    # ========= 拐向分析 + 标注  ========
    def analyze_turning(self):
        """
        对所有内部顶点执行拐向分析，在画布上标注，并在结果面板显示。
        内部顶点 = 除了第一个点和最后一个点之外的所有点。
        """

        if len(self.points) < 3:
            messagebox.showwarning("提示", "至少需要 3 个点才能分析拐向！")
            return

        # ── 确保已连线 ──
        self.lines_visible = True
        self.analyzed = True
        self._redraw()                  # 先重绘基本元素

        # ── 准备结果面板 ──
        self.result_text.config(state=tk.NORMAL)   # 临时解锁文本框，允许写入
        self.result_text.delete('1.0', tk.END)     # 清空旧内容（'1.0'表示第1行第0列）
        self.result_text.insert(tk.END, "=== 拐向分析结果 ===\n\n", 'header')

        # ── 定义标注颜色 ──
        color_map = {
            "左转 ↰": '#2E7D32',        # 绿色
            "右转 ↱": '#C62828',        # 红色
            "共线 →": '#F57F17'         # 橙黄色
        }
        tag_map = {
            "左转 ↰": 'left',
            "右转 ↱": 'right',
            "共线 →": 'collinear'
        }

        # ── 遍历每个内部顶点 ──
        # range(1, n-1): 从第2个点到倒数第2个点（索引 1 到 n-2）
        # 因为第一个点没有"前一个点"，最后一个点没有"后一个点"
        n = len(self.points)
        for i in range(1, n - 1):
            p1 = self.points[i - 1]     # 前一个点
            p2 = self.points[i]         # 当前拐点（要判断的点）
            p3 = self.points[i + 1]     # 后一个点

            # ── 调用核心算法 ──
            cross_val, direction = self.cross_product(p1, p2, p3)

            # ── 在画布上标注 ──
            color = color_map[direction]
            self.ax.annotate(
                direction,                     # 标注文字: "左转 ↰" / "右转 ↱" / "共线 →"
                (p2[0], p2[1]),                # 标注位置: 当前拐点
                textcoords="offset points",
                xytext=(-20, -20),             # 偏移到点的左下方（避免与点号重叠）
                fontsize=10,
                fontweight='bold',
                color=color,                   # 按方向着色
                bbox=dict(                     # 给文字加背景框
                    boxstyle='round,pad=0.3',  # 圆角矩形，内边距 0.3
                    facecolor=color,           # 背景色 = 文字色
                    alpha=0.15                 # 15% 透明度（淡淡的底色）
                ),
                zorder=4                       # 最上层
            )

            # ── 在结果面板写入 ──
            line = f"P{i}->P{i+1}->P{i+2}:  {direction}\n"
            self.result_text.insert(tk.END, line, tag_map[direction])

        # ── 写入叉积数值 ──
        self.result_text.insert(tk.END, "\n=== 叉积数值 ===\n\n", 'header')
        for i in range(1, n - 1):
            cross_val, direction = self.cross_product(
                self.points[i-1], self.points[i], self.points[i+1]
            )
            sign = "+" if cross_val >= 0 else ""  # 正数加 + 号，负数自带 - 号
            self.result_text.insert(
                tk.END,
                f"  P{i+1}: {sign}{cross_val:.4f}\n",   # 保留4位小数
                tag_map[direction]                        # 用对应颜色标签
            )

        # ── 锁定结果面板 ──
        self.result_text.config(state=tk.DISABLED)  # 重新禁用编辑

        # ── 刷新画布 ──
        self.canvas.draw()
        self._update_status("分析完成 | 拖动点可实时更新")

    # ======= 清空重置 ======
    def clear_all(self):
        """清空所有点、连线、分析结果，恢复初始状态"""

        if self.points:
            # 有数据时弹出确认框，防止误操作
            ok = messagebox.askyesno("确认", "确定要清空所有点和分析结果吗？")
            if not ok:
                return               # 用户点"否"，取消操作

        # ── 重置所有状态 ──
        self.points.clear()           # 等效于 self.points = []，但保持引用不变
        self.lines_visible = False
        self.analyzed = False
        self.drag_index = None

        # ── 清空结果面板 ──
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        self.result_text.config(state=tk.DISABLED)

        # ── 重绘 + 更新状态栏 ──
        self._redraw()
        self._update_status("已清空 | 模式: 采点")

    # ======= 导入文件 =======
    def import_points(self):
        """
        从 CSV/TXT 文件导入坐标点。
        支持格式: 每行一个点，x 和 y 用逗号分隔。
        """

        # ── 弹出文件选择对话框 ──
        filepath = filedialog.askopenfilename(
            title="选择坐标文件",
            filetypes=[
                ("CSV 文件", "*.csv"),              # 下拉菜单第一项
                ("文本文件", "*.txt"),                # 第二项
                ("所有文件", "*.*")                   # 第三项
            ],
            initialdir="."                           # 初始目录: 当前目录
        )

        if not filepath:
            return               # 用户点了"取消"

        try:
            new_points = []      # 临时列表，读取成功后再赋值给 self.points

            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)               # csv.reader 自动按逗号分割每行

                for row_num, row in enumerate(reader, start=1):
                    # row 是一个列表，如 ['1.5', '3.2'] 或 ['x', 'y']（表头）

                    if not row or row[0].strip().startswith('#'):
                        # 跳过空行 和 以 # 开头的注释行
                        continue

                    # ── 尝试解析为浮点数 ──
                    try:
                        x = float(row[0].strip())    # strip() 去除首尾空白
                        y = float(row[1].strip())
                        new_points.append((x, y))
                    except (ValueError, IndexError):
                        # ValueError: 不能转浮点数（可能是表头 "x,y"）
                        # IndexError: 这行不够 2 列
                        # 跳过这些行，不报错（兼容表头）
                        continue

            if not new_points:
                messagebox.showwarning("提示", "文件中没有找到有效坐标！")
                return

            # ── 导入成功，覆盖当前点 ──
            self.points = new_points
            self.lines_visible = False
            self.analyzed = False

            # ── 自动调整坐标轴范围 ──
            xs, ys = zip(*self.points)
            margin = max(
                (max(xs) - min(xs)) * 0.15,    # x 范围的 15% 作为边距
                (max(ys) - min(ys)) * 0.15,    # y 范围的 15%
                0.5                             # 最小边距 0.5，防止所有点在一条线上时没有边距
            )
            self.ax.set_xlim(min(xs) - margin, max(xs) + margin)
            self.ax.set_ylim(min(ys) - margin, max(ys) + margin)

            self._redraw()
            self._update_status(f"已导入 {len(self.points)} 个点 | 来自 {filepath}")
            messagebox.showinfo("导入成功", f"成功导入 {len(self.points)} 个点")

        except Exception as e:
            messagebox.showerror("导入失败", f"读取文件时出错:\n{e}")

    # =========== 导出结果 ===========
    def export_results(self):
        """
        将点坐标和拐向分析结果导出为 CSV 文件。
        """

        if not self.points:
            messagebox.showwarning("提示", "没有数据可导出！")
            return

        # ── 弹出保存文件对话框 ──
        filepath = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".csv",                 # 默认扩展名
            filetypes=[("CSV 文件", "*.csv")],
            initialfile="turning_result.csv"         # 建议文件名
        )

        if not filepath:
            return

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                # newline='': 防止 Windows 下 csv 写入多余空行
                # utf-8-sig: 带 BOM 头的 UTF-8，Excel 打开不会乱码
                writer = csv.writer(f)

                # ── 写入表头 ──
                writer.writerow(['点序号', 'X', 'Y', '拐向', '叉积值'])

                # ── 写入每个点的数据 ──
                n = len(self.points)
                for i, (x, y) in enumerate(self.points):
                    if 0 < i < n - 1:
                        # 内部顶点: 有拐向和叉积值
                        cross_val, direction = self.cross_product(
                            self.points[i-1], self.points[i], self.points[i+1]
                        )
                        writer.writerow([
                            f'P{i+1}',              # 点序号
                            f'{x:.4f}',              # X 坐标
                            f'{y:.4f}',              # Y 坐标
                            direction,               # 拐向文字
                            f'{cross_val:.6f}'       # 叉积值（6位小数）
                        ])
                    else:
                        # 首尾点: 没有拐向（标记为端点）
                        writer.writerow([
                            f'P{i+1}', f'{x:.4f}', f'{y:.4f}', '端点', '-'
                        ])

            self._update_status(f"已导出到 {filepath}")
            messagebox.showinfo("导出成功", f"结果已保存到:\n{filepath}")

        except Exception as e:
            messagebox.showerror("导出失败", f"保存文件时出错:\n{e}")

# =========  主函数 ===============
def main():

    root = tk.Tk()

    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    app = TurningApp(root)   # 创建应用实例（触发 __init__，搭建界面）
    root.mainloop()         # 进入 Tkinter 事件循环（程序在此阻塞，等待用户操作）

if __name__ == '__main__':
    main()
