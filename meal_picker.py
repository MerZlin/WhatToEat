# -*- coding: utf-8 -*-
"""
下一顿吃什么 - Windows 桌面版
纯 Python + tkinter，无需安装任何额外依赖
双击运行，快速出结果！
"""
import json
import os
import random
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ============ 预设菜品 ============
DEFAULT_DISHES = [
    # 家常菜
    ("红烧肉", "家常菜"), ("糖醋排骨", "家常菜"), ("鱼香肉丝", "家常菜"),
    ("宫保鸡丁", "家常菜"), ("麻婆豆腐", "家常菜"), ("回锅肉", "家常菜"),
    ("番茄炒蛋", "家常菜"), ("青椒肉丝", "家常菜"), ("地三鲜", "家常菜"),
    ("酸辣土豆丝", "家常菜"), ("蒜蓉西兰花", "家常菜"), ("可乐鸡翅", "家常菜"),
    ("干煸豆角", "家常菜"), ("孜然牛肉", "家常菜"), ("葱爆羊肉", "家常菜"),
    # 面食
    ("兰州拉面", "面食"), ("炸酱面", "面食"), ("西红柿鸡蛋面", "面食"),
    ("重庆小面", "面食"), ("油泼面", "面食"), ("刀削面", "面食"),
    ("担担面", "面食"), ("热干面", "面食"), ("饺子", "面食"),
    ("馄饨", "面食"), ("肉夹馍", "面食"), ("葱油拌面", "面食"),
    # 快餐
    ("汉堡", "快餐"), ("披萨", "快餐"), ("炸鸡", "快餐"),
    ("麻辣烫", "快餐"), ("冒菜", "快餐"), ("黄焖鸡米饭", "快餐"),
    ("盖浇饭", "快餐"), ("炒饭", "快餐"), ("炒面", "快餐"),
    # 汤品
    ("酸辣汤", "汤品"), ("紫菜蛋花汤", "汤品"), ("番茄牛腩汤", "汤品"),
    ("排骨汤", "汤品"), ("鸡汤", "汤品"), ("冬瓜汤", "汤品"),
    # 小吃
    ("煎饼果子", "小吃"), ("烤冷面", "小吃"), ("臭豆腐", "小吃"),
    ("凉皮", "小吃"), ("生煎包", "小吃"), ("小笼包", "小吃"),
    ("春卷", "小吃"), ("锅贴", "小吃"),
    # 异国料理
    ("寿司", "异国料理"), ("日式拉面", "异国料理"), ("咖喱饭", "异国料理"),
    ("韩式拌饭", "异国料理"), ("部队锅", "异国料理"), ("冬阴功", "异国料理"),
    ("意面", "异国料理"), ("牛排", "异国料理"),
    # 烧烤
    ("羊肉串", "烧烤"), ("烤鱼", "烧烤"), ("烤鸡翅", "烧烤"),
    ("烤茄子", "烧烤"), ("烤玉米", "烧烤"), ("烤韭菜", "烧烤"), ("烤生蚝", "烧烤"),
    # 素菜
    ("手撕包菜", "素菜"), ("蚝油生菜", "素菜"), ("凉拌黄瓜", "素菜"),
    ("虎皮青椒", "素菜"), ("干锅花菜", "素菜"), ("香菇油菜", "素菜"),
]


class MealPicker:
    DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meal_picker_data.json")

    def __init__(self):
        self.dishes = []
        self.history = []
        self.current_filter = "全部"
        self.is_spinning = False
        self.spin_job = None
        self.spin_index = 0
        self.last_result = None
        self._load_data()

        # ===== 主窗口 =====
        self.root = tk.Tk()
        self.root.title("🍜 下一顿吃什么？")
        self.root.geometry("720x640")
        self.root.minsize(580, 500)
        self.root.configure(bg="#1e1e2e")

        # 样式
        self._setup_styles()

        # ===== 构建 UI =====
        self._build_ui()
        self._refresh_all()

        # 窗口居中
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

        # 快捷键
        self.root.bind("<space>", lambda e: self._toggle_spin())
        self.root.bind("<Key-r>", lambda e: self._instant_pick())
        self.root.bind("<Key-R>", lambda e: self._instant_pick())
        self.root.bind("<Escape>", lambda e: self._cancel_spin())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ============ 样式 ============
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        BG = "#1e1e2e"
        FG = "#e0e0e0"
        CARD = "#2a2a3e"
        ACCENT = "#e94560"
        ACCENT2 = "#f5a623"

        style.configure(".", background=BG, foreground=FG, font=("Microsoft YaHei UI", 10))
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 22, "bold"),
                        foreground=ACCENT2, background=BG)
        style.configure("Subtitle.TLabel", font=("Microsoft YaHei UI", 9),
                        foreground="#888", background=BG)
        style.configure("Card.TFrame", background=CARD, relief="flat")
        style.configure("Result.TLabel", font=("Microsoft YaHei UI", 32, "bold"),
                        foreground=ACCENT2, background=CARD)
        style.configure("ResultCat.TLabel", font=("Microsoft YaHei UI", 10),
                        foreground="#aaa", background=CARD)

        style.configure("Primary.TButton", font=("Microsoft YaHei UI", 12, "bold"),
                        background=ACCENT, foreground="white", borderwidth=0,
                        padding=(30, 10))
        style.map("Primary.TButton", background=[("active", "#c0392b")])

        style.configure("Secondary.TButton", font=("Microsoft YaHei UI", 10),
                        background="#3a3a55", foreground=FG, borderwidth=0,
                        padding=(18, 8))
        style.map("Secondary.TButton", background=[("active", "#4a4a65")])

        style.configure("Danger.TButton", font=("Microsoft YaHei UI", 9),
                        background="#4a2030", foreground=ACCENT, borderwidth=0,
                        padding=(10, 5))
        style.map("Danger.TButton", background=[("active", "#5a3040")])

        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", font=("Microsoft YaHei UI", 10, "bold"),
                        padding=(20, 8), background="#2a2a3e", foreground="#999")
        style.map("TNotebook.Tab",
                  background=[("selected", CARD)],
                  foreground=[("selected", FG)])

        style.configure("Vertical.TScrollbar", background="#3a3a55",
                        troughcolor=CARD, borderwidth=0, arrowsize=16)

    # ============ 数据持久化 ============
    def _load_data(self):
        try:
            with open(self.DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.dishes = data.get("dishes", [])
                self.history = data.get("history", [])
        except (FileNotFoundError, json.JSONDecodeError):
            self.dishes = [{"name": n, "cat": c} for n, c in DEFAULT_DISHES]
            self.history = []

    def _save_data(self):
        with open(self.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"dishes": self.dishes, "history": self.history[:200]},
                      f, ensure_ascii=False, indent=2)

    # ============ 辅助方法 ============
    def _get_filtered(self):
        if self.current_filter == "全部":
            return self.dishes.copy()
        return [d for d in self.dishes if d["cat"] == self.current_filter]

    def _get_categories(self):
        cats = sorted(set(d["cat"] for d in self.dishes))
        return ["全部"] + cats

    # ============ 构建 UI ============
    def _build_ui(self):
        # --- 顶部标题 ---
        header = ttk.Frame(self.root)
        header.pack(pady=(16, 4))
        ttk.Label(header, text="🍜  下一顿吃什么？", style="Title.TLabel").pack()
        ttk.Label(header, text="把选择交给命运，让每一餐都有惊喜 ✨",
                  style="Subtitle.TLabel").pack()

        # --- 主体 Notebook ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(4, 12))

        self._build_pick_tab()
        self._build_manage_tab()

        # --- 底部状态栏 ---
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill="x", padx=16, pady=(0, 8))
        self._refresh_stats()

    def _build_pick_tab(self):
        """挑选 tab"""
        tab = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(tab, text="  🎰 挑选  ")

        # 分类按钮栏
        cat_frame = ttk.Frame(tab)
        cat_frame.pack(fill="x", padx=12, pady=(12, 4))
        self.cat_frame = cat_frame
        self.cat_buttons = {}

        # 转盘滚动显示区
        wheel_card = ttk.Frame(tab, style="Card.TFrame")
        wheel_card.pack(fill="x", padx=12, pady=6)
        wheel_card.configure(relief="solid", borderwidth=1)

        wheel_inner = tk.Frame(wheel_card, bg="#1e1e2e", height=120)
        wheel_inner.pack(fill="x", padx=2, pady=2)
        wheel_inner.pack_propagate(False)

        self.wheel_label = tk.Label(wheel_inner, text="", font=("Microsoft YaHei UI", 18, "bold"),
                                    fg="#e0e0e0", bg="#1e1e2e")
        self.wheel_label.pack(expand=True)

        # 结果展示区
        result_card = ttk.Frame(tab, style="Card.TFrame")
        result_card.pack(fill="x", padx=12, pady=6)
        result_card.configure(height=100)

        self.result_label = ttk.Label(result_card, text="👆 点一下试试", style="Result.TLabel")
        self.result_label.pack(pady=(14, 2))
        self.result_cat_label = ttk.Label(result_card, text="", style="ResultCat.TLabel")
        self.result_cat_label.pack(pady=(0, 12))

        # 按钮区
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="🎰  转一转  (空格键)", style="Primary.TButton",
                   command=self._toggle_spin).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="⚡  秒出结果  (R键)", style="Secondary.TButton",
                   command=self._instant_pick).pack(side="left", padx=6)

        # 历史区
        hist_card = ttk.Frame(tab, style="Card.TFrame")
        hist_card.pack(fill="both", expand=True, padx=12, pady=6)

        hist_header = ttk.Frame(hist_card)
        hist_header.pack(fill="x", padx=10, pady=(8, 2))
        ttk.Label(hist_header, text="🕐 最近挑选", font=("Microsoft YaHei UI", 10, "bold"),
                  background="#2a2a3e").pack(side="left")
        ttk.Button(hist_header, text="清空", style="Danger.TButton",
                   command=self._clear_history).pack(side="right")

        self.hist_text = tk.Text(hist_card, font=("Microsoft YaHei UI", 9),
                                 fg="#999", bg="#252538", bd=0, padx=12, pady=8,
                                 height=8, wrap="word", state="disabled",
                                 relief="flat")
        self.hist_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _build_manage_tab(self):
        """管理 tab"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="  📋 管理菜品  ")

        # 添加区
        add_frame = ttk.Frame(tab, style="Card.TFrame")
        add_frame.pack(fill="x", padx=12, pady=(12, 6))
        add_frame.configure(height=60)

        inner = ttk.Frame(add_frame)
        inner.pack(padx=12, pady=12, fill="x")
        ttk.Label(inner, text="➕ 添加菜品", font=("Microsoft YaHei UI", 10, "bold"),
                  background="#2a2a3e").pack(side="left", padx=(0, 10))

        self.new_name_var = tk.StringVar()
        ttk.Entry(inner, textvariable=self.new_name_var, font=("Microsoft YaHei UI", 10),
                  width=18).pack(side="left", padx=4)

        self.new_cat_var = tk.StringVar(value="家常菜")
        cats = sorted(set(c for _, c in DEFAULT_DISHES))
        cat_combo = ttk.Combobox(inner, textvariable=self.new_cat_var, values=cats,
                                 font=("Microsoft YaHei UI", 10), width=10, state="readonly")
        cat_combo.pack(side="left", padx=4)

        ttk.Button(inner, text="添加", style="Secondary.TButton",
                   command=self._add_dish).pack(side="left", padx=8)
        # 绑定回车
        inner.bind("<Return>", lambda e: self._add_dish())

        # 菜品列表
        list_frame = ttk.Frame(tab, style="Card.TFrame")
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.dish_tree = ttk.Treeview(list_frame, columns=("name", "cat"),
                                      show="headings", selectmode="browse",
                                      height=14)
        self.dish_tree.heading("name", text="菜名")
        self.dish_tree.heading("cat", text="分类")
        self.dish_tree.column("name", width=200, anchor="center")
        self.dish_tree.column("cat", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical",
                                  command=self.dish_tree.yview)
        self.dish_tree.configure(yscrollcommand=scrollbar.set)

        self.dish_tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 4), pady=8)

        del_btn_frame = ttk.Frame(list_frame)
        del_btn_frame.pack(side="bottom", pady=(0, 8))
        ttk.Button(del_btn_frame, text="🗑  删除选中菜品", style="Danger.TButton",
                   command=self._remove_dish).pack()

    # ============ 刷新 UI ============
    def _refresh_all(self):
        self._refresh_cat_buttons()
        self._refresh_dish_tree()
        self._refresh_history()
        self._refresh_stats()

    def _refresh_cat_buttons(self):
        for w in self.cat_frame.winfo_children():
            w.destroy()
        self.cat_buttons.clear()

        cats = self._get_categories()
        # 用 Canvas + Frame 实现可换行的分类按钮
        for i, cat in enumerate(cats):
            btn = tk.Button(self.cat_frame, text=cat, font=("Microsoft YaHei UI", 9),
                            relief="flat", bd=1, padx=12, pady=4,
                            cursor="hand2",
                            command=lambda c=cat: self._set_filter(c))
            btn.pack(side="left", padx=3, pady=3)
            self.cat_buttons[cat] = btn
        self._update_cat_style()

    def _update_cat_style(self):
        for cat, btn in self.cat_buttons.items():
            if cat == self.current_filter:
                btn.configure(bg="#e94560", fg="white", activebackground="#c0392b",
                              activeforeground="white")
            else:
                btn.configure(bg="#2a2a3e", fg="#aaa", activebackground="#3a3a55",
                              activeforeground="#e0e0e0")

    def _set_filter(self, cat):
        self.current_filter = cat
        self._update_cat_style()
        self._refresh_dish_tree()

    def _refresh_dish_tree(self):
        self.dish_tree.delete(*self.dish_tree.get_children())
        for d in self._get_filtered():
            idx = self.dishes.index(d)
            self.dish_tree.insert("", "end", iid=str(idx), values=(d["name"], d["cat"]))

    def _refresh_history(self):
        self.hist_text.configure(state="normal")
        self.hist_text.delete("1.0", "end")
        if not self.history:
            self.hist_text.insert("1.0", "  还没有挑选记录，快来试试吧~")
        else:
            for h in reversed(self.history[-30:]):
                ts = h.get("time", "")
                try:
                    dt = datetime.fromisoformat(ts)
                    now = datetime.now()
                    if dt.date() == now.date():
                        ts_str = f"今天 {dt:%H:%M}"
                    elif (now - dt).days == 1:
                        ts_str = f"昨天 {dt:%H:%M}"
                    else:
                        ts_str = f"{dt.month}/{dt.day} {dt:%H:%M}"
                except (ValueError, TypeError):
                    ts_str = ""
                self.hist_text.insert("end", f"  🍽  {h['name']}  [{h['cat']}]  {ts_str}\n")
        self.hist_text.configure(state="disabled")
        self.hist_text.see("1.0")

    def _refresh_stats(self):
        for w in self.status_bar.winfo_children():
            w.destroy()
        today = datetime.now().date().isoformat()
        today_count = sum(1 for h in self.history
                         if h.get("time", "").startswith(today))
        info = f"📚 {len(self.dishes)} 道菜  |  📂 {len(self._get_categories())-1} 个分类  |  📝 今日 {today_count} 次"
        ttk.Label(self.status_bar, text=info, font=("Microsoft YaHei UI", 8),
                  foreground="#666", background="#1e1e2e").pack(side="left")

    # ============ 挑选逻辑 ============
    def _toggle_spin(self):
        """空格键——开始/停止转盘"""
        if self.is_spinning:
            self._stop_spin()
        else:
            self._start_spin()

    def _start_spin(self):
        filtered = self._get_filtered()
        if not filtered:
            messagebox.showinfo("提示", "请先添加菜品！")
            return
        if self.is_spinning:
            return

        self.is_spinning = True
        self.spin_index = 0
        self._spin_step()

    def _spin_step(self):
        if not self.is_spinning:
            return

        filtered = self._get_filtered()
        n = len(filtered)
        if n == 0:
            self.is_spinning = False
            return

        # 快速滚动 —— 每 40ms 换一个，比 HTML 版快一倍
        d = filtered[self.spin_index % n]
        self.wheel_label.configure(text=d["name"])
        self.result_label.configure(text="🎰 转盘中...", font=("Microsoft YaHei UI", 14))
        self.result_cat_label.configure(text="按空格键停止")
        self.spin_index += 1

        self.spin_job = self.root.after(40, self._spin_step)

    def _stop_spin(self):
        if not self.is_spinning:
            return
        # 逐渐减速
        self.is_spinning = False
        if self.spin_job:
            self.root.after_cancel(self.spin_job)
            self.spin_job = None
        self._show_result()

    def _instant_pick(self):
        """秒出结果——无滚动，0.3 秒延迟直接显示"""
        filtered = self._get_filtered()
        if not filtered:
            messagebox.showinfo("提示", "请先添加菜品！")
            return

        # 取消正在进行的旋转
        if self.is_spinning:
            self.is_spinning = False
            if self.spin_job:
                self.root.after_cancel(self.spin_job)
                self.spin_job = None

        # 极短的闪烁效果
        picked = random.choice(filtered)
        self.wheel_label.configure(text="")
        self.result_label.configure(text="⚡ ...", font=("Microsoft YaHei UI", 14))
        self.result_cat_label.configure(text="")

        def show():
            self.wheel_label.configure(text=picked["name"])
            self._show_result_for(picked)
        self.root.after(200, show)

    def _cancel_spin(self):
        if self.is_spinning:
            self.is_spinning = False
            if self.spin_job:
                self.root.after_cancel(self.spin_job)
                self.spin_job = None
            if self.last_result:
                self._show_result_for(self.last_result)
            else:
                self.result_label.configure(text="已取消", font=("Microsoft YaHei UI", 14))
                self.result_cat_label.configure(text="")
                self.wheel_label.configure(text="")

    def _show_result(self):
        filtered = self._get_filtered()
        if not filtered:
            return
        n = len(filtered)
        picked = filtered[(self.spin_index - 1) % n] if self.spin_index > 0 else random.choice(filtered)
        self._show_result_for(picked)

    def _show_result_for(self, picked):
        self.last_result = picked
        self.wheel_label.configure(text=picked["name"])
        self.result_label.configure(text=picked["name"], font=("Microsoft YaHei UI", 30, "bold"),
                                     foreground="#f5a623")
        self.result_cat_label.configure(text=picked["cat"])
        # 记录
        self.history.append({
            "name": picked["name"],
            "cat": picked["cat"],
            "time": datetime.now().isoformat()
        })
        self._save_data()
        self._refresh_history()
        self._refresh_stats()

    # ============ 菜品管理 ============
    def _add_dish(self):
        name = self.new_name_var.get().strip()
        cat = self.new_cat_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "请输入菜品名称！")
            return
        if any(d["name"] == name and d["cat"] == cat for d in self.dishes):
            messagebox.showinfo("提示", f"「{name}」({cat}) 已经存在！")
            return
        self.dishes.append({"name": name, "cat": cat})
        self._save_data()
        self.new_name_var.set("")
        self._refresh_all()
        # 切回全部
        if self.current_filter != "全部":
            self.current_filter = "全部"
            self._update_cat_style()
        self._refresh_dish_tree()

    def _remove_dish(self):
        sel = self.dish_tree.selection()
        if not sel:
            messagebox.showinfo("提示", "请先在列表中选中要删除的菜品")
            return
        idx = int(sel[0])
        d = self.dishes[idx]
        if messagebox.askyesno("确认删除", f"确定要删除「{d['name']}」({d['cat']}) 吗？"):
            del self.dishes[idx]
            self._save_data()
            if self.last_result and self.last_result["name"] == d["name"] \
               and self.last_result["cat"] == d["cat"]:
                self.last_result = None
            self._refresh_all()

    def _clear_history(self):
        if messagebox.askyesno("确认清空", "确定要清空所有挑选历史吗？"):
            self.history.clear()
            self._save_data()
            self._refresh_history()
            self._refresh_stats()

    def _on_close(self):
        self._save_data()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MealPicker()
    app.run()
