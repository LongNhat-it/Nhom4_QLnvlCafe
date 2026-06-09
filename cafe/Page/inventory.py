import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import numpy as np
import sqlite3
import os
import csv
import threading
import time
from datetime import datetime

# Import thư viện vẽ biểu đồ
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter


class InventoryPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.view()
        self.show_loading_screen()

    def view(self):
        header_bg = "#4A3525"
        header = ctk.CTkFrame(self.master, height=75, corner_radius=0, fg_color=header_bg)
        header.pack(fill="x")
        header.pack_propagate(False)

        lbl_header = ctk.CTkLabel(header, text="☕ QUẢN LÝ KHO & BÁO CÁO CHI TIÊU", font=("Arial", 22, "bold"),
                                  text_color="#FDFBF7")
        lbl_header.pack(side="left", padx=20, pady=15)

        cmd_back = self.app_manager.show_manager_menu if self.app_manager.current_role == "Quản lý" else self.app_manager.show_login_page
        text_back = "🔙 VỀ MENU" if self.app_manager.current_role == "Quản lý" else "ĐĂNG XUẤT"
        btn_back = ctk.CTkButton(header, text=text_back, fg_color="#D9534F", hover_color="#C9302C", text_color="white",
                                 font=("Arial", 12, "bold"), width=130, height=35, command=cmd_back)
        btn_back.pack(side="right", padx=20, pady=15)

        self.tab_view = ctk.CTkTabview(self.master)
        self.tab_view._segmented_button.configure(font=("Arial", 13, "bold"))
        self.tab_view.pack(fill="both", expand=True, padx=15, pady=10)

        self.tab1 = self.tab_view.add(" 📦 1. Quản lý kho thực tế ")
        self.tab2 = self.tab_view.add(" 📊 2. Tổng hợp chi phí ")
        self.tab_chart = self.tab_view.add(" 📈 3. Phân tích định kỳ ")
        self.tab3 = self.tab_view.add(" 📄 4. Phiếu báo cáo văn bản ")

        self.setup_tab_inventory()
        self.setup_tab_stats()
        self.setup_tab_chart()
        self.setup_tab_report_text()

    def setup_tab_inventory(self):
        toolbar = ctk.CTkFrame(self.tab1, fg_color="transparent")
        toolbar.pack(fill="x", pady=5)

        btn_style = {"font": ("Arial", 12, "bold"), "text_color": "white", "height": 35}

        btn_refresh = ctk.CTkButton(toolbar, text="🔄 Làm mới", command=self.clear_search_and_refresh,
                                    fg_color="#A67B5B", hover_color="#8E6649", width=110, **btn_style)
        btn_refresh.pack(side="left", padx=4)

        btn_add = ctk.CTkButton(toolbar, text="➕ Nhập hàng mới", command=lambda: self.open_form("NHẬP HÀNG MỚI"),
                                fg_color="#5C8D89", hover_color="#4A726E", width=150, **btn_style)
        btn_add.pack(side="left", padx=4)

        btn_edit = ctk.CTkButton(toolbar, text="📝 Sửa", command=self.edit_item, fg_color="#E0A96D",
                                 hover_color="#CC965C", width=100, **btn_style)
        btn_edit.pack(side="left", padx=4)

        btn_del = ctk.CTkButton(toolbar, text="🗑️ Xóa", command=self.delete_item, fg_color="#A64B2A",
                                hover_color="#8E3E22", width=100, **btn_style)
        btn_del.pack(side="left", padx=4)

        btn_import = ctk.CTkButton(toolbar, text="📥 Nhập CSV", command=self.import_csv, fg_color="#2E7D32",
                                   hover_color="#1B5E20", width=120, **btn_style)
        btn_import.pack(side="left", padx=4)

        btn_export = ctk.CTkButton(toolbar, text="📤 Xuất CSV", command=self.export_csv, fg_color="#1565C0",
                                   hover_color="#0D47A1", width=120, **btn_style)
        btn_export.pack(side="left", padx=4)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_data_from_db())

        self.ent_search = ctk.CTkEntry(toolbar, width=450, height=30, textvariable=self.search_var)
        self.ent_search.pack(side="right", padx=8)

        lbl_search = ctk.CTkLabel(toolbar, text="Tìm kiếm:", font=("Arial", 13, "italic"), text_color="#6F4E37")
        lbl_search.pack(side="right", padx=2)

        table_frame = ctk.CTkFrame(self.tab1, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#6F4E37", foreground="white", font=("Arial", 12, "bold"),
                        borderwidth=0)
        style.configure("Treeview", background="#FDFBF7", foreground="#4A3525", fieldbackground="#FDFBF7", rowheight=38,
                        font=("Arial", 12))

        columns = ("stt", "ten", "loai", "sl", "dv_nhap", "gia", "thang", "dot", "tong")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        titles = ["STT", "Nguyên liệu", "Phân loại", "Số lượng", "ĐV Nhập", "Giá nhập", "Tháng nhập", "Đợt nhập",
                  "Thành tiền"]
        widths = {"stt": 60, "ten": 180, "loai": 140, "sl": 100, "dv_nhap": 110, "gia": 110, "thang": 120, "dot": 100,
                  "tong": 130}

        for c, t in zip(self.tree["columns"], titles):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=widths.get(c, 120), anchor="center")
        self.tree.pack(fill="both", expand=True, side="left")

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

    def setup_tab_stats(self):
        container = ctk.CTkFrame(self.tab2, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        right_side = ctk.CTkFrame(container)
        right_side.pack(fill="both", expand=True, pady=10)

        filter_frame = ctk.CTkFrame(right_side, fg_color="transparent")
        filter_frame.pack(fill="x", pady=5)

        self.stat_filter_thang = ctk.CTkComboBox(filter_frame,
                                                 values=["Tất cả Tháng"] + [f"Tháng {i}" for i in range(1, 13)],
                                                 width=140, font=("Arial", 12),
                                                 command=lambda e: self.refresh_data_from_db())
        self.stat_filter_thang.pack(side="left", padx=5)
        self.stat_filter_thang.set("Tất cả Tháng")

        self.stat_filter_dot = ctk.CTkComboBox(filter_frame, values=["Tất cả Đợt"] + [f"Đợt {i}" for i in range(1, 6)],
                                               width=120, font=("Arial", 12),
                                               command=lambda e: self.refresh_data_from_db())
        self.stat_filter_dot.pack(side="left", padx=5)
        self.stat_filter_dot.set("Tất cả Đợt")

        self.tree_stats = ttk.Treeview(right_side, columns=("ten", "sl", "thang", "dot", "gia", "tong"),
                                       show="headings")
        titles = ["Nguyên liệu", "Số lượng", "Tháng nhập", "Đợt nhập", "Đơn giá", "Tổng hóa đơn"]
        for c, t in zip(self.tree_stats["columns"], titles):
            self.tree_stats.heading(c, text=t)
            self.tree_stats.column(c, anchor="center", width=120, minwidth=100)

        self.tree_stats.pack(fill="both", expand=True, padx=5, pady=(5, 0))

        hbar = ctk.CTkScrollbar(right_side, orientation="horizontal", command=self.tree_stats.xview)
        self.tree_stats.configure(xscrollcommand=hbar.set)
        hbar.pack(fill="x", padx=5, pady=(0, 5))

        bottom_frame = ctk.CTkFrame(right_side, fg_color="transparent")
        bottom_frame.pack(fill="x", pady=10)

        self.lbl_total_payment = ctk.CTkLabel(bottom_frame, text="KẾT QUẢ: 0 VNĐ", font=("Arial", 18, "bold"),
                                              text_color="#C0392B")
        self.lbl_total_payment.pack(side="right", padx=10)

    def setup_tab_chart(self):
        container = ctk.CTkFrame(self.tab_chart, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        # Thêm phần thống kê tóm tắt
        stats_frame = ctk.CTkFrame(container, fg_color="#FDFBF7", corner_radius=10, border_width=1, border_color="#E6D5C3")
        stats_frame.pack(fill="x", pady=(0, 15), ipadx=10, ipady=10)

        lbl_summary_title = ctk.CTkLabel(stats_frame, text="📊 TỔNG QUAN NGUỒN VỐN MUA NGUYÊN LIỆU", font=("Arial", 14, "bold"), text_color="#4A3525")
        lbl_summary_title.pack(pady=(5, 10))

        info_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=20)

        self.lbl_tong_von = ctk.CTkLabel(info_frame, text="Tổng vốn đã chi: 0 VNĐ", font=("Arial", 14, "bold"), text_color="#C0392B")
        self.lbl_tong_von.pack(side="left", expand=True)

        self.lbl_tb_von = ctk.CTkLabel(info_frame, text="Trung bình tháng: 0 VNĐ", font=("Arial", 14, "bold"), text_color="#2980B9")
        self.lbl_tb_von.pack(side="left", expand=True)

        self.lbl_max_von = ctk.CTkLabel(info_frame, text="Tháng chi nhiều nhất: Không có", font=("Arial", 14, "bold"), text_color="#27AE60")
        self.lbl_max_von.pack(side="left", expand=True)

        lbl_title = ctk.CTkLabel(container, text="BIỂU ĐỒ BIẾN ĐỘNG CHI PHÍ NHẬP HÀNG 12 THÁNG",
                                 font=("Arial", 16, "bold"), text_color="#4A3525")
        lbl_title.pack(anchor="w", pady=(0, 10))

        chart_frame = ctk.CTkFrame(container, fg_color="#FFFFFF", border_width=2, border_color="#E6D5C3",
                                   corner_radius=5)
        chart_frame.pack(fill="both", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(10, 5), dpi=100)
        self.fig.patch.set_facecolor('#FFFFFF')
        self.ax.set_facecolor('#FFFFFF')

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    # ---------------------------------------------------------------------------------
    # ĐÃ SỬA: THÊM LƯỚI GIÓNG VÀ SỐ LIỆU LÊN ĐỈNH CỘT
    # ---------------------------------------------------------------------------------
    def update_chart(self, df_list):
        months = [f"Tháng {i}" for i in range(1, 13)]
        costs = [0.0] * 12

        for item in df_list:
            ngay = item[5]
            thanh_tien = item[6]
            parts = ngay.split("-")
            thang_str = parts[0].strip()
            if "Tháng" in thang_str:
                try:
                    m = int(thang_str.replace("Tháng", "").strip())
                    if 1 <= m <= 12:
                        costs[m - 1] += thanh_tien
                except:
                    pass

        tong_von = sum(costs)
        active_months = [c for c in costs if c > 0]
        tb_von = tong_von / len(active_months) if active_months else 0
        max_von = max(costs) if costs else 0
        max_month = costs.index(max_von) + 1 if max_von > 0 else None

        self.lbl_tong_von.configure(text=f"Tổng vốn đã chi: {int(tong_von):,} VNĐ")
        self.lbl_tb_von.configure(text=f"Trung bình tháng: {int(tb_von):,} VNĐ")
        if max_month:
            self.lbl_max_von.configure(text=f"Tháng chi nhiều nhất: Tháng {max_month} ({int(max_von):,} VNĐ)")
        else:
            self.lbl_max_von.configure(text="Tháng chi nhiều nhất: Không có")

        self.ax.clear()

        # 1. Vẽ đường gióng ngang (Y-axis Grid)
        self.ax.grid(axis='y', linestyle='--', alpha=0.7, color='#D3C5B7')
        self.ax.set_axisbelow(True)  # Đẩy đường lưới ra phía sau cột

        bars = self.ax.bar(months, costs, color="#6F4E37", width=0.55)

        # 2. Hiển thị số liệu cụ thể lên đỉnh cột
        max_y = max(costs) if costs else 0
        padding = max_y * 0.03  # Tạo khoảng đệm nhỏ để chữ không dính sát viền cột

        for bar in bars:
            height = bar.get_height()
            if height > 0:  # Chỉ hiển thị số liệu khi chi phí > 0
                self.ax.text(bar.get_x() + bar.get_width() / 2.0,
                             height + padding,
                             f'{int(height):,}',  # Format số có dấu phẩy
                             ha='center', va='bottom', fontsize=9, color='#C0392B', fontweight='bold')

        # 3. Kéo giãn trục Y thêm 15% để số liệu trên cùng không bị lẹm viền
        if max_y > 0:
            self.ax.set_ylim(0, max_y * 1.15)

        self.ax.set_title("BIẾN ĐỘNG CHI PHÍ NHẬP HÀNG THEO KỲ", fontsize=13, fontweight="bold", color="#4A3525",
                          pad=15)
        self.ax.set_ylabel("Chi phí (VNĐ)", fontsize=11, fontweight="bold", color="#4A3525")

        self.ax.tick_params(axis='x', rotation=45, labelsize=10, colors="#4A3525")
        self.ax.tick_params(axis='y', labelsize=10, colors="#4A3525")

        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_color('#4A3525')
        self.ax.spines['bottom'].set_color('#4A3525')

        def money_formatter(x, pos):
            return f"{int(x):,}"

        self.ax.yaxis.set_major_formatter(FuncFormatter(money_formatter))

        self.fig.tight_layout()
        self.canvas.draw()

    def setup_tab_report_text(self):
        container = ctk.CTkFrame(self.tab3, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)
        top_ctrl = ctk.CTkFrame(container, fg_color="#FDFBF7", corner_radius=10, border_width=1, border_color="#E6D5C3")
        top_ctrl.pack(fill="x", pady=(0, 15), ipadx=10, ipady=10)
        lbl_ctrl = ctk.CTkLabel(top_ctrl, text="Định dạng xuất báo cáo:", font=("Arial", 14, "bold"),
                                text_color="#4A3525")
        lbl_ctrl.pack(side="left", padx=15)
        self.cbo_format = ctk.CTkComboBox(top_ctrl,
                                          values=["Xuất file Excel (.xlsx) - Đề xuất", "Xuất file CSV (.csv)"],
                                          width=260, height=35, font=("Arial", 13))
        self.cbo_format.pack(side="left", padx=10)
        self.cbo_format.set("Xuất file Excel (.xlsx) - Đề xuất")
        btn_export_rep = ctk.CTkButton(top_ctrl, text="🚀 LƯU PHIẾU BÁO CÁO", command=self.thuc_hien_xuat_bao_cao,
                                       fg_color="#27AE60", hover_color="#1E8449", text_color="white",
                                       font=("Arial", 13, "bold"), height=38)
        btn_export_rep.pack(side="right", padx=15)
        btn_monthly_history = ctk.CTkButton(top_ctrl, text="📜 Lịch sử tổng hợp",
                                            command=self.show_monthly_history_window, fg_color="#D97706",
                                            hover_color="#B45309", text_color="white", font=("Arial", 13, "bold"),
                                            height=38)
        btn_monthly_history.pack(side="right", padx=10)
        paper_frame = ctk.CTkFrame(container, fg_color="#FFFFFF", border_width=2, border_color="#6F4E37",
                                   corner_radius=5)
        paper_frame.pack(fill="both", expand=True, padx=40, pady=(5, 10))
        self.lbl_report_title = ctk.CTkLabel(paper_frame,
                                             text=f"PHIẾU BÁO CÁO KHO THÁNG {datetime.now().strftime('%m/%Y')}",
                                             font=("Arial", 18, "bold"), text_color="#2C3E50")
        self.lbl_report_title.pack(pady=(15, 5))
        summary_frame = ctk.CTkFrame(paper_frame, fg_color="#F2F3F4", corner_radius=8)
        summary_frame.pack(fill="x", padx=30, pady=10)
        self.lbl_tong_tien_phieu = ctk.CTkLabel(summary_frame, text="Tổng chi phí: 0 VNĐ", font=("Arial", 16, "bold"),
                                                text_color="#C0392B")
        self.lbl_tong_tien_phieu.pack(side="left", padx=20, pady=15)
        self.lbl_tong_mon_phieu = ctk.CTkLabel(summary_frame, text="Tổng danh mục hàng: 0", font=("Arial", 14, "bold"),
                                               text_color="#2980B9")
        self.lbl_tong_mon_phieu.pack(side="right", padx=20, pady=15)
        table_frame = ctk.CTkFrame(paper_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=30, pady=(5, 20))
        style = ttk.Style()
        style.configure("Report.Treeview.Heading", font=("Arial", 12, "bold"), background="#E6D5C3",
                        foreground="#4A3525")
        style.configure("Report.Treeview", rowheight=32, font=("Arial", 12))
        self.report_tree = ttk.Treeview(table_frame, columns=("stt", "ten", "loai", "sl_dv", "tien"), show="headings",
                                        style="Report.Treeview")
        self.report_tree.heading("stt", text="STT")
        self.report_tree.heading("ten", text="Tên mặt hàng")
        self.report_tree.heading("loai", text="Phân loại")
        self.report_tree.heading("sl_dv", text="Số lượng & ĐV")
        self.report_tree.heading("tien", text="Thành tiền (VNĐ)")
        self.report_tree.column("stt", width=60, anchor="center")
        self.report_tree.column("ten", width=250)
        self.report_tree.column("loai", width=150, anchor="center")
        self.report_tree.column("sl_dv", width=150, anchor="center")
        self.report_tree.column("tien", width=180, anchor="e")
        self.report_tree.pack(side="left", fill="both", expand=True)
        sb_report = ttk.Scrollbar(table_frame, orient="vertical", command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=sb_report.set)
        sb_report.pack(side="right", fill="y")

    def show_monthly_history_window(self):
        win = ctk.CTkToplevel(self.master)
        win.title("Lịch sử tổng hợp kho từng kỳ")
        w, h = 750, 450
        self.master.update_idletasks()
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_w = self.master.winfo_width()
        parent_h = self.master.winfo_height()
        x = parent_x + (parent_w // 2) - (w // 2)
        y = parent_y + (parent_h // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.grab_set()
        lbl_title = ctk.CTkLabel(win, text="📊 LỊCH SỬ TỔNG HỢP KHO THEO KỲ", font=("Arial", 16, "bold"),
                                 text_color="#4A3525")
        lbl_title.pack(pady=15)
        table_frame = ctk.CTkFrame(win, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        style = ttk.Style()
        style.configure("HistoryMonth.Treeview.Heading", font=("Arial", 11, "bold"), background="#6F4E37",
                        foreground="white")
        style.configure("HistoryMonth.Treeview", rowheight=30, font=("Arial", 11))
        tree_m = ttk.Treeview(table_frame, columns=("thang", "dot", "so_luong_loai", "tong_sl", "tong_gia_tri"),
                              show="headings", style="HistoryMonth.Treeview")
        tree_m.heading("thang", text="Tháng kiểm kho")
        tree_m.heading("dot", text="Đợt kiểm kho")
        tree_m.heading("so_luong_loai", text="Số loại mặt hàng")
        tree_m.heading("tong_sl", text="Tổng số lượng")
        tree_m.heading("tong_gia_tri", text="Tổng giá trị nhập (VNĐ)")
        tree_m.column("thang", width=140, anchor="center")
        tree_m.column("dot", width=120, anchor="center")
        tree_m.column("so_luong_loai", width=130, anchor="center")
        tree_m.column("tong_sl", width=120, anchor="center")
        tree_m.column("tong_gia_tri", width=180, anchor="e")
        tree_m.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=tree_m.yview)
        tree_m.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        period_data = {}
        try:
            conn = sqlite3.connect("database/cafe.db")
            cursor = conn.cursor()
            cursor.execute("SELECT ten, soluong, gianhap, ngaynhap FROM nguyenlieu")
            rows = cursor.fetchall()
            conn.close()
            for row in rows:
                ten, sl, gia, ngay_nhap_raw = row
                raw_key = ngay_nhap_raw.strip() if ngay_nhap_raw else "Chưa phân loại"
                if raw_key not in period_data:
                    period_data[raw_key] = {
                        "items": set(),
                        "total_qty": 0,
                        "total_value": 0
                    }
                period_data[raw_key]["items"].add(ten)
                period_data[raw_key]["total_qty"] += sl
                period_data[raw_key]["total_value"] += (sl * gia)

            def parse_thang_dot_for_sort(key):
                thang_num = 999
                dot_num = 999
                parts = key.split("-")
                if len(parts) >= 1:
                    thang_part = parts[0].strip()
                    if "Tháng" in thang_part:
                        try:
                            thang_num = int(thang_part.replace("Tháng", "").strip())
                        except:
                            pass
                if len(parts) >= 2:
                    dot_part = parts[1].strip()
                    if "Đợt" in dot_part:
                        try:
                            dot_num = int(dot_part.replace("Đợt", "").strip())
                        except:
                            pass
                return (thang_num, dot_num)

            sorted_keys = sorted(period_data.keys(), key=parse_thang_dot_for_sort)
            for key in sorted_keys:
                data = period_data[key]
                thang_val = "Chưa phân loại"
                dot_val = "Không rõ"
                parts = key.split("-")
                if len(parts) >= 1:
                    thang_val = parts[0].strip()
                if len(parts) >= 2:
                    dot_val = parts[1].strip()
                cnt_items = len(data["items"])
                total_qty = data["total_qty"]
                total_val = data["total_value"]
                tree_m.insert("", "end", values=(thang_val, dot_val, cnt_items, total_qty, f"{total_val:,}"))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải lịch sử tổng hợp: {e}")

        def on_tree_click(event):
            selected = tree_m.selection()
            if not selected:
                return
            item = tree_m.item(selected[0])
            thang_val, dot_val, _, _, _ = item["values"]
            self.show_period_details(win, thang_val, dot_val)

        tree_m.bind("<Double-1>", on_tree_click)
        lbl_hint = ctk.CTkLabel(win, text="* Nhấp đúp chuột vào một hàng để xem phiếu báo cáo chi tiết", font=("Arial", 11, "italic"), text_color="#A67B5B")
        lbl_hint.pack(pady=(5, 0))
        btn_close = ctk.CTkButton(win, text="Đóng", command=win.destroy, fg_color="#6F4E37", hover_color="#5A3E2B",
                                  text_color="white", width=120, height=35)
        btn_close.pack(pady=15)

    def show_period_details(self, parent_win, thang_val, dot_val):
        detail_win = ctk.CTkToplevel(parent_win)
        title = f"Chi tiết Báo cáo: {thang_val} - {dot_val}" if dot_val != "Không rõ" else f"Chi tiết Báo cáo: {thang_val}"
        detail_win.title(title)
        
        w, h = 800, 500
        parent_win.update_idletasks()
        parent_x = parent_win.winfo_rootx()
        parent_y = parent_win.winfo_rooty()
        parent_w = parent_win.winfo_width()
        parent_h = parent_win.winfo_height()
        x = parent_x + (parent_w // 2) - (w // 2)
        y = parent_y + (parent_h // 2) - (h // 2)
        detail_win.geometry(f"{w}x{h}+{x}+{y}")
        
        detail_win.transient(parent_win)
        detail_win.grab_set()

        lbl_title = ctk.CTkLabel(detail_win, text=f"📋 BÁO CÁO CHI TIẾT: {str(thang_val).upper()} - {str(dot_val).upper()}", font=("Arial", 16, "bold"), text_color="#4A3525")
        lbl_title.pack(pady=15)

        table_frame = ctk.CTkFrame(detail_win, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        style = ttk.Style()
        style.configure("Detail.Treeview.Heading", font=("Arial", 11, "bold"), background="#E6D5C3", foreground="#4A3525")
        style.configure("Detail.Treeview", rowheight=30, font=("Arial", 11))

        tree_d = ttk.Treeview(table_frame, columns=("stt", "ten", "loai", "sl_dv", "gia", "tien"), show="headings", style="Detail.Treeview")
        tree_d.heading("stt", text="STT")
        tree_d.heading("ten", text="Tên nguyên liệu")
        tree_d.heading("loai", text="Phân loại")
        tree_d.heading("sl_dv", text="Số lượng & ĐV")
        tree_d.heading("gia", text="Đơn giá (VNĐ)")
        tree_d.heading("tien", text="Thành tiền (VNĐ)")
        
        tree_d.column("stt", width=50, anchor="center")
        tree_d.column("ten", width=200)
        tree_d.column("loai", width=120, anchor="center")
        tree_d.column("sl_dv", width=120, anchor="center")
        tree_d.column("gia", width=120, anchor="e")
        tree_d.column("tien", width=150, anchor="e")
        
        tree_d.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(table_frame, orient="vertical", command=tree_d.yview)
        tree_d.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        target_ngay = f"{thang_val} - {dot_val}" if dot_val != "Không rõ" else thang_val

        try:
            conn = sqlite3.connect("database/cafe.db")
            cursor = conn.cursor()
            if dot_val == "Không rõ":
                cursor.execute("SELECT ten, loai, soluong, donvi, gianhap FROM nguyenlieu WHERE ngaynhap=? OR ngaynhap LIKE ?", (thang_val, f"{thang_val} - %"))
            else:
                cursor.execute("SELECT ten, loai, soluong, donvi, gianhap FROM nguyenlieu WHERE ngaynhap=?", (target_ngay,))
            rows = cursor.fetchall()
            conn.close()

            total_tien = 0
            for idx, row in enumerate(rows, 1):
                ten, loai, sl, dv, gia = row
                tien = sl * gia
                total_tien += tien
                tree_d.insert("", "end", values=(idx, ten, loai, f"{sl} {dv}", f"{gia:,}", f"{tien:,}"))

            summary_lbl = ctk.CTkLabel(detail_win, text=f"Tổng chi phí: {total_tien:,} VNĐ", font=("Arial", 15, "bold"), text_color="#C0392B")
            summary_lbl.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải chi tiết: {e}")

        btn_close = ctk.CTkButton(detail_win, text="Đóng", command=detail_win.destroy, fg_color="#6F4E37", hover_color="#5A3E2B", text_color="white", width=120, height=35)
        btn_close.pack(pady=10)

    def show_loading_screen(self):
        loading_win = ctk.CTkToplevel(self.master)
        loading_win.title("Loading...")
        loading_win.geometry("300x150")
        loading_win.transient(self.master)
        loading_win.grab_set()

        lbl_load = ctk.CTkLabel(loading_win, text="Đang xử lý đồng bộ dữ liệu...", font=("Arial", 12, "bold"))
        lbl_load.pack(pady=15)

        progress = ctk.CTkProgressBar(loading_win, orientation="horizontal", width=200, mode="indeterminate")
        progress.pack(pady=10)
        progress.start()

        def heavy_task():
            time.sleep(3.1)
            self.master.after(0, done)

        def done():
            try:
                progress.stop()
                loading_win.destroy()
            except:
                pass
            self.refresh_data_from_db()

        threading.Thread(target=heavy_task).start()

    def clear_search_and_refresh(self):
        self.ent_search.delete(0, "end")
        self.stat_filter_thang.set("Tất cả Tháng")
        self.stat_filter_dot.set("Tất cả Đợt")
        self.show_loading_screen()

    def refresh_data_from_db(self):
        query = self.search_var.get().strip().lower()
        loc_thang = self.stat_filter_thang.get()
        loc_dot = self.stat_filter_dot.get()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for i in self.tree_stats.get_children():
            self.tree_stats.delete(i)
        try:
            conn = sqlite3.connect("database/cafe.db")
            cursor = conn.cursor()
            cursor.execute("SELECT ten, loai, soluong, donvi, gianhap, ngaynhap FROM nguyenlieu")
            rows = cursor.fetchall()
            conn.close()
            df_list = []
            thanh_tien_list = []
            idx = 1
            for row in rows:
                ten, loai, sl, dv_nhap, gia, ngay = row
                thanh_tien = sl * gia
                df_list.append([ten, loai, sl, dv_nhap, gia, ngay, thanh_tien])
                parts = ngay.split("-")
                thang_val = parts[0].strip() if len(parts) >= 1 else ngay
                dot_val = parts[1].strip() if len(parts) >= 2 else ""
                if query in ten.lower() or query in loai.lower() or query in ngay.lower():
                    self.tree.insert("", "end", values=(idx, ten, loai, sl, dv_nhap, f"{gia:,}", thang_val, dot_val,
                                                        f"{thanh_tien:,}"))
                    thanh_tien_list.append(thanh_tien)
                    idx += 1
                phu_hop_tab2 = True
                if loc_thang != "Tất cả Tháng" and loc_thang not in ngay:
                    phu_hop_tab2 = False
                if loc_dot != "Tất cả Đợt" and loc_dot not in ngay:
                    phu_hop_tab2 = False
                if phu_hop_tab2:
                    self.tree_stats.insert("", "end", values=(ten, f"{sl} {dv_nhap}", thang_val, dot_val, f"{gia:,}",
                                                              f"{thanh_tien:,}"))
            total_sum = np.sum(np.array(thanh_tien_list, dtype=np.int64)) if thanh_tien_list else 0
            self.lbl_total_payment.configure(text=f"KẾT QUẢ: {total_sum:,} VNĐ")

            self.generate_custom_report(total_sum, df_list)
            self.update_chart(df_list)

        except Exception as e:
            print(e)

    def calculate_advanced_statistics(self, df_list):
        if not df_list:
            self.lbl_stats_summary.configure(text="Không có dữ liệu nguyên liệu.")
            return

        df = pd.DataFrame(df_list,
                          columns=["Nguyên liệu", "Loại", "Số lượng", "ĐV Nhập", "Giá nhập", "Ngày nhập", "Thành tiền"])

        total_types = len(df)
        thanh_tien_arr = df["Thành tiền"].to_numpy()
        mean_cost = np.mean(thanh_tien_arr)
        max_cost = np.max(thanh_tien_arr)

        group_counts = df.groupby("Loại")["Số lượng"].sum()
        total_qty = group_counts.sum()

        dist_text = ""
        for cat, qty in group_counts.items():
            percentage = (qty / total_qty) * 100 if total_qty > 0 else 0
            dist_text += f"+ {cat}: {percentage:.1f}%\n"

        summary_text = (
            f"Tổng số loại hàng: {total_types}\n\n"
            f"Thành tiền TB: {mean_cost:,.1f} VNĐ\n\n"
            f"Thành tiền lớn nhất: {max_cost:,.0f} VNĐ\n\n"
            f"TỶ LỆ PHÂN BỔ NHÓM:\n{dist_text}"
        )
        self.lbl_stats_summary.configure(text=summary_text)

    def generate_custom_report(self, total_money, df_list):
        self.lbl_tong_tien_phieu.configure(text=f"Tổng chi phí nhập hàng: {total_money:,} VNĐ")
        self.lbl_tong_mon_phieu.configure(text=f"Tổng danh mục kho: {len(df_list)} mặt hàng")
        self.lbl_report_title.configure(text=f"PHIẾU BÁO CÁO TỔNG HỢP KHO - THÁNG {datetime.now().strftime('%m/%Y')}")

        for i in self.report_tree.get_children():
            self.report_tree.delete(i)

        for idx, item in enumerate(df_list, 1):
            ten = item[0]
            loai = item[1]
            sl = item[2]
            dv_nhap = item[3]
            thanh_tien = item[6]
            self.report_tree.insert("", "end", values=(idx, ten, loai, f"{sl} {dv_nhap}", f"{thanh_tien:,}"))

    def thuc_hien_xuat_bao_cao(self):
        loai_file = self.cbo_format.get()
        thoi_gian = datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            conn = sqlite3.connect("database/cafe.db")
            df = pd.read_sql_query("SELECT ten, loai, soluong, donvi, gianhap FROM nguyenlieu", conn)
            conn.close()

            if df.empty:
                messagebox.showwarning("Cảnh báo", "Không có dữ liệu trong kho để xuất báo cáo!")
                return

            df['Thành tiền (VNĐ)'] = df['soluong'] * df['gianhap']
            df.rename(columns={
                'ten': 'Tên nguyên liệu',
                'loai': 'Phân loại',
                'soluong': 'Số lượng',
                'donvi': 'Đơn vị tính',
                'gianhap': 'Đơn giá (VNĐ)'
            }, inplace=True)

            total_cost = df['Thành tiền (VNĐ)'].sum()
            total_row = pd.DataFrame([{
                'Tên nguyên liệu': 'TỔNG CỘNG CHI PHÍ',
                'Phân loại': '',
                'Số lượng': '',
                'Đơn vị tính': '',
                'Đơn giá (VNĐ)': '',
                'Thành tiền (VNĐ)': total_cost
            }])
            df_export = pd.concat([df, total_row], ignore_index=True)

            if "Excel (.xlsx)" in loai_file:
                path = filedialog.asksaveasfilename(initialdir="database", initialfile=f"BaoCao_Kho_{thoi_gian}.xlsx",
                                                    defaultextension=".xlsx",
                                                    filetypes=[("Excel Spreadsheet", "*.xlsx")])
                if path:
                    try:
                        with pd.ExcelWriter(path, engine='openpyxl') as writer:
                            df_export.to_excel(writer, index=False, sheet_name="Bao_Cao_Kho")
                            worksheet = writer.sheets["Bao_Cao_Kho"]

                            for i, col in enumerate(df_export.columns):
                                max_len = max(df_export[col].astype(str).map(len).max(), len(col)) + 3
                                worksheet.column_dimensions[chr(65 + i)].width = max_len

                        messagebox.showinfo("Thành công", f"Đã lưu Phiếu báo cáo Excel chuyên nghiệp tại:\n{path}")
                    except ImportError:
                        df_export.to_csv(path.replace('.xlsx', '.csv'), index=False, encoding="utf-8-sig")
                        messagebox.showwarning("Thiếu thư viện",
                                               "Máy bạn chưa cài đặt thư viện 'openpyxl' để lưu file Excel định dạng cao.\nHệ thống đã tự động xuất bằng định dạng CSV thay thế.")

            else:
                path = filedialog.asksaveasfilename(initialdir="database", initialfile=f"BaoCao_Kho_{thoi_gian}.csv",
                                                    defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
                if path:
                    df_export.to_csv(path, index=False, encoding="utf-8-sig")
                    messagebox.showinfo("Thành công", f"Đã kết xuất Dữ liệu CSV thành công tại:\n{path}")

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra sự cố khi kết xuất file: {e}")

    def edit_item(self):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0])['values']
            ten = vals[1]
            loai = vals[2]
            sl = vals[3]
            dv_nhap = vals[4]
            gia = vals[5]
            thang = vals[6]
            dot = vals[7]
            ngay = f"{thang} - {dot}"
            self.open_form("CẬP NHẬT", (ten, loai, sl, dv_nhap, gia, ngay))

    def delete_item(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Xác nhận", "Xóa sản phẩm này khỏi cơ sở dữ liệu?"):
            ten = self.tree.item(sel[0])['values'][1]
            try:
                conn = sqlite3.connect("database/cafe.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM nguyenlieu WHERE ten=?", (ten,))
                conn.commit()

                cursor.execute("SELECT ten, loai, soluong, donvi, gianhap, ngaynhap FROM nguyenlieu")
                all_items = cursor.fetchall()
                conn.close()

                try:
                    with open("database/nguyenlieu.csv", "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Nguyên liệu", "Loại", "Số lượng", "Đơn vị nhập", "Giá nhập", "Ngày nhập"])
                        for item in all_items:
                            writer.writerow([item[0], item[1], item[2], item[3], item[4], item[5]])
                except Exception as ex:
                    print(ex)

                self.show_loading_screen()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa sản phẩm: {e}")

    def import_csv(self):
        file_path_selected = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path_selected:
            return
        try:
            df_imported = pd.read_csv(file_path_selected, encoding="utf-8")
            conn = sqlite3.connect("database/cafe.db")
            cursor = conn.cursor()
            for _, row in df_imported.iterrows():
                ten = row.get("Nguyên liệu", row.get("ten", ""))
                loai = row.get("Loại", row.get("loai", ""))
                sl = int(row.get("Số lượng", row.get("soluong", 0)))
                dv = row.get("Đơn vị nhập", row.get("donvi", ""))
                gia = int(row.get("Giá nhập", row.get("gianhap", 0)))
                ngay = row.get("Ngày nhập", row.get("ngaynhap", ""))

                if ten:
                    cursor.execute("INSERT OR REPLACE INTO nguyenlieu VALUES (?, ?, ?, ?, ?, ?)",
                                   (ten, loai, sl, dv, gia, ngay))
            conn.commit()
            conn.close()
            self.show_loading_screen()
            messagebox.showinfo("Thành công", "Đã nhập dữ liệu từ file CSV thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhập file CSV: {e}")

    def export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")],
                                            initialfile="kho_nguyen_lieu.csv")
        if path:
            try:
                conn = sqlite3.connect("database/cafe.db")
                df = pd.read_sql_query("SELECT * FROM nguyenlieu", conn)
                conn.close()
                df.to_csv(path, index=False, encoding="utf-8-sig")
                messagebox.showinfo("Thành công", f"Đã xuất file CSV thành công tại:\n{path}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xuất file: {e}")

    def open_form(self, title, edit_data=None):
        win = ctk.CTkToplevel(self.master)
        win.title(title)

        w, h = 540, 580

        self.master.update_idletasks()
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_w = self.master.winfo_width()
        parent_h = self.master.winfo_height()
        x = parent_x + (parent_w // 2) - (w // 2)
        y = parent_y + (parent_h // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

        win.grab_set()

        lbl_title = ctk.CTkLabel(win, text=title, font=("Arial", 18, "bold"), text_color="#4A3525")
        lbl_title.pack(pady=20)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(anchor="center", pady=10)

        font_lbl = ("Arial", 12, "bold")
        font_input = ("Arial", 13)

        lbl_ten = ctk.CTkLabel(form_frame, text="Tên nguyên liệu:", font=font_lbl, text_color="#4A3525")
        lbl_ten.grid(row=0, column=0, sticky="w", pady=8)
        ent_ten = ctk.CTkEntry(form_frame, font=font_input, width=240, height=35)
        ent_ten.grid(row=0, column=1, pady=8, padx=10)

        lbl_loai = ctk.CTkLabel(form_frame, text="Nhóm phân loại:", font=font_lbl, text_color="#4A3525")
        lbl_loai.grid(row=1, column=0, sticky="w", pady=8)
        cb_loai = ctk.CTkComboBox(form_frame, values=["Nhóm Hạt", "Nhóm Bột", "Nhóm Chất lỏng"], font=font_input,
                                  width=240, height=35)
        cb_loai.grid(row=1, column=1, pady=8, padx=10)

        lbl_sl = ctk.CTkLabel(form_frame, text="Số lượng:", font=font_lbl, text_color="#4A3525")
        lbl_sl.grid(row=2, column=0, sticky="w", pady=8)
        ent_sl = ctk.CTkEntry(form_frame, font=font_input, width=240, height=35)
        ent_sl.grid(row=2, column=1, pady=8, padx=10)

        lbl_dv = ctk.CTkLabel(form_frame, text="Đơn vị nhập:", font=font_lbl, text_color="#4A3525")
        lbl_dv.grid(row=3, column=0, sticky="w", pady=8)
        cb_dv_nhap = ctk.CTkComboBox(form_frame, values=["Kilogram (kg)", "Thùng (5kg)", "Thùng (10kg)"],
                                     font=font_input, width=240, height=35)
        cb_dv_nhap.grid(row=3, column=1, pady=8, padx=10)

        lbl_gia = ctk.CTkLabel(form_frame, text="Giá nhập (VNĐ):", font=font_lbl, text_color="#4A3525")
        lbl_gia.grid(row=4, column=0, sticky="w", pady=8)
        ent_gia = ctk.CTkEntry(form_frame, font=font_input, width=240, height=35)
        ent_gia.grid(row=4, column=1, pady=8, padx=10)

        lbl_ky = ctk.CTkLabel(form_frame, text="Chọn Kỳ kiểm kho:", font=font_lbl, text_color="#4A3525")
        lbl_ky.grid(row=5, column=0, sticky="w", pady=8)

        ky_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        ky_frame.grid(row=5, column=1, sticky="w", pady=8, padx=10)

        cb_thang = ctk.CTkComboBox(ky_frame, values=[f"Tháng {i}" for i in range(1, 13)], font=font_input, width=110,
                                   height=35)
        cb_thang.pack(side="left")
        cb_thang.set(f"Tháng {datetime.now().month}")

        lbl_sep = ctk.CTkLabel(ky_frame, text=" - ", font=("Arial", 12, "bold"), text_color="#4A3525")
        lbl_sep.pack(side="left", padx=2)

        cb_dot = ctk.CTkComboBox(ky_frame, values=[f"Đợt {i}" for i in range(1, 6)], font=font_input, width=100,
                                 height=35)
        cb_dot.pack(side="left")
        cb_dot.set("Đợt 1")

        def on_category_change(choice=None):
            cat = cb_loai.get()
            if cat == "Nhóm Hạt":
                cb_dv_nhap.configure(values=["Kilogram (kg)", "Thùng (5kg)", "Thùng (10kg)"])
                cb_dv_nhap.set("Kilogram (kg)")
            elif cat == "Nhóm Bột":
                cb_dv_nhap.configure(values=["Túi/Gói (500g)", "Túi/Gói (1kg)"])
                cb_dv_nhap.set("Túi/Gói (1kg)")
            elif cat == "Nhóm Chất lỏng":
                cb_dv_nhap.configure(values=["Chai", "Hộp", "Can (lít)"])
                cb_dv_nhap.set("Chai")

        cb_loai.configure(command=on_category_change)

        if edit_data:
            ent_ten.insert(0, edit_data[0])
            ent_ten.configure(state="readonly")
            cb_loai.set(edit_data[1])
            on_category_change()
            ent_sl.insert(0, edit_data[2])
            cb_dv_nhap.set(edit_data[3])
            ent_gia.insert(0, edit_data[4])
            raw_ngay = edit_data[5]
            if "Tháng" in raw_ngay and "-" in raw_ngay:
                try:
                    parts_ky = raw_ngay.split("-")
                    cb_thang.set(parts_ky[0].strip())
                    cb_dot.set(parts_ky[1].strip())
                except:
                    pass

        def save():
            ten = ent_ten.get().strip()
            loai = cb_loai.get()
            sl_str = ent_sl.get().strip()
            dv_nhap = cb_dv_nhap.get()
            gia_str = ent_gia.get().strip()

            if not ten or not loai:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin Tên và Phân loại!")
                return

            try:
                sl_val = int(sl_str.replace(',', '').replace('.', ''))
                if sl_val <= 0:
                    messagebox.showerror("Lỗi dữ liệu", "Số lượng hàng hóa phải lớn hơn 0!")
                    return
            except ValueError:
                messagebox.showerror("Lỗi dữ liệu", "Số lượng không hợp lệ!")
                return

            try:
                gia_val = int(gia_str.replace(',', '').replace('.', '').replace(' VNĐ', ''))
                if gia_val <= 0:
                    messagebox.showerror("Lỗi dữ liệu", "Giá nhập phải lớn hơn 0 VNĐ!")
                    return
            except ValueError:
                messagebox.showerror("Lỗi dữ liệu", "Đơn giá nhập không hợp lệ!")
                return

            ngay_tich_hop = f"{cb_thang.get()} - {cb_dot.get()}"

            try:
                conn = sqlite3.connect("database/cafe.db")
                cursor = conn.cursor()
                cursor.execute("SELECT ten FROM nguyenlieu WHERE ten=?", (ten,))
                if cursor.fetchone():
                    cursor.execute(
                        "UPDATE nguyenlieu SET loai=?, soluong=?, donvi=?, gianhap=?, ngaynhap=? WHERE ten=?",
                        (loai, sl_val, dv_nhap, gia_val, ngay_tich_hop, ten))
                else:
                    cursor.execute("INSERT INTO nguyenlieu VALUES (?, ?, ?, ?, ?, ?)",
                                   (ten, loai, sl_val, dv_nhap, gia_val, ngay_tich_hop))
                conn.commit()

                cursor.execute("SELECT ten, loai, soluong, donvi, gianhap, ngaynhap FROM nguyenlieu")
                all_items = cursor.fetchall()
                conn.close()

                try:
                    with open("database/nguyenlieu.csv", "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["Nguyên liệu", "Loại", "Số lượng", "Đơn vị nhập", "Giá nhập", "Ngày nhập"])
                        for item in all_items:
                            writer.writerow([item[0], item[1], item[2], item[3], item[4], item[5]])
                except Exception as ex:
                    print(ex)

                self.master.focus_set()
                self.show_loading_screen()
                win.after(10, win.destroy)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu CSDL: {e}")

        btn_confirm = ctk.CTkButton(win, text="XÁC NHẬN", fg_color="#5D4037", hover_color="#7B5E4E", text_color="white",
                                    font=("Arial", 13, "bold"), command=save, width=150, height=35)
        btn_confirm.pack(pady=25)