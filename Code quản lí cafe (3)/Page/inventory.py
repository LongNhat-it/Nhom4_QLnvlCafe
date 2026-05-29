# --- START OF FILE inventory.py ---

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from datetime import datetime
from common.button import CustomButton


class InventoryPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager

        self.file_path = "database/nguyenlieu.csv"
        # Cấu trúc trường tinh giản (Không chứa ĐV Sử dụng và Quản lý Lô/HSD)
        self.fields = ["Nguyên liệu", "Loại", "Số lượng", "Đơn vị nhập", "Giá nhập", "Ngày nhập"]

        if not os.path.exists("database"):
            os.makedirs("database")

        self.du_lieu_chi_tieu = {
            f"Tháng {i}": {
                "cac_dot": []
            } for i in range(1, 13)
        }

        self.view()
        self.refresh_data()
        self.cap_nhat_bang_chi_tieu_12_thang()

    def clean_number(self, value):
        try:
            v = str(value).replace(',', '').replace('.', '').replace(' VNĐ', '').strip()
            return int(v) if v else 0
        except:
            return 0

    def view(self):
        """HÀM KHỞI TẠO GIAO DIỆN CHÍNH VÀ ĐỊNH TUYẾN PHÂN QUYỀN"""
        header_bg = "#6F4E37"
        header = tk.Frame(self.master, bg=header_bg, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="☕ QUẢN LÝ KHO & BÁO CÁO", font=("Arial", 20, "bold"),
                 fg="white", bg=header_bg).pack(side="left", padx=20)

        # Kiểm tra role để định tuyến nút bấm (Về menu hoặc Đăng xuất)
        btn_back = tk.Button(header, text="🔙 VỀ MENU" if self.app_manager.current_role == "Quản lý" else "ĐĂNG XUẤT",
                             bg="#c0392b", fg="white", font=("Arial", 10, "bold"), bd=0, padx=15, cursor="hand2",
                             command=self.app_manager.show_manager_menu if self.app_manager.current_role == "Quản lý" else self.app_manager.show_login_page)
        btn_back.pack(side="right", padx=20, pady=15)

        # CẤU TRÚC PHÂN TÁCH TAB GIAO DIỆN
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab1 = tk.Frame(self.notebook, bg="white")
        self.tab2 = tk.Frame(self.notebook, bg="white")
        self.tab4 = tk.Frame(self.notebook, bg="#F5F5F5")  # Tab Phân tích tài chính
        self.tab3 = tk.Frame(self.notebook, bg="white")  # Tab Preview văn bản

        self.notebook.add(self.tab1, text=" 1. Quản lý kho ")
        self.notebook.add(self.tab2, text=" 2. Tổng hợp chi phí kho ")
        self.notebook.add(self.tab4, text=" 3. Phân tích chi phí theo kỳ ")
        self.notebook.add(self.tab3, text=" 4. Phiếu báo cáo văn bản ")

        # SỰ KIỆN ĐỒNG BỘ GIỮA CÁC TAB
        self.notebook.bind("<<NotebookTabChanged>>", self.xu_ly_chuyen_tab_tong_hop)

        self.setup_tab_inventory()
        self.setup_tab_stats()
        self.setup_tab_report_text()
        self.setup_tab_analysis_by_period()

    def setup_tab_inventory(self):
        """TAB 1: KHÔNG GIAN TÁC VỤ KHO THỰC TẾ (CRUD)"""
        toolbar = tk.Frame(self.tab1, bg="white", pady=10)
        toolbar.pack(fill="x")

        CustomButton(toolbar, text="🔄 Làm mới", command=self.clear_search_and_refresh, style_type="info").pack(
            side="left", padx=5)
        CustomButton(toolbar, text="➕ Nhập hàng mới", command=lambda: self.open_form("NHẬP HÀNG MỚI"),
                     style_type="success").pack(side="left", padx=5)
        CustomButton(toolbar, text="📝 Sửa", command=self.edit_item, style_type="warning").pack(side="left", padx=5)
        CustomButton(toolbar, text="🗑️ Xóa", command=self.delete_item, style_type="danger").pack(side="left", padx=5)

        CustomButton(toolbar, text="🔍", command=self.refresh_data, style_type="primary").pack(side="right", padx=2)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_data())
        self.ent_search = tk.Entry(toolbar, font=("Arial", 11), width=50, textvariable=self.search_var)
        self.ent_search.pack(side="right", padx=5)
        tk.Label(toolbar, text="Tìm kiếm:", bg="white").pack(side="right", padx=5)

        columns = ("stt", "ten", "loai", "sl", "dv_nhap", "gia", "ngay", "tong")
        self.tree = ttk.Treeview(self.tab1, columns=columns, show="headings")

        titles = ["STT", "Nguyên liệu", "Phân loại", "Số lượng", "ĐV Nhập", "Giá nhập", "Kỳ & Ngày nhập", "Thành tiền"]
        widths = {
            "stt": 50,
            "ten": 180,
            "loai": 130,
            "sl": 100,
            "dv_nhap": 110,
            "gia": 110,
            "ngay": 200,
            "tong": 120
        }

        for c, t in zip(self.tree["columns"], titles):
            self.tree.heading(c, text=t)
            self.tree.column(c, width=widths.get(c, 100), anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def setup_tab_stats(self):
        """TAB 2: THỐNG KÊ CHI PHÍ VÀ LỌC ĐƠN HÀNG THEO THÁNG / ĐỢT CHUYÊN SÂU"""
        filter_frame = tk.Frame(self.tab2, bg="white", pady=10)
        filter_frame.pack(fill="x", padx=20)

        tk.Label(filter_frame, text="📋 TỔNG HỢP CHI PHÍ HOÁ ĐƠN", font=("Arial", 14, "bold"), bg="white",
                 fg="#6F4E37").pack(side=tk.LEFT)

        # Bộ lọc Tháng và Đợt tích hợp trên Tab 2
        filter_ctrl = tk.Frame(filter_frame, bg="white")
        filter_ctrl.pack(side=tk.RIGHT)

        tk.Label(filter_ctrl, text="Lọc theo kỳ kho:", bg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT,
                                                                                                    padx=5)

        self.stat_filter_thang = ttk.Combobox(filter_ctrl,
                                              values=["Tất cả Tháng"] + [f"Tháng {i}" for i in range(1, 13)],
                                              state="readonly", font=("Arial", 10), width=12)
        self.stat_filter_thang.pack(side=tk.LEFT, padx=3)
        self.stat_filter_thang.set("Tất cả Tháng")
        self.stat_filter_thang.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        self.stat_filter_dot = ttk.Combobox(filter_ctrl, values=["Tất cả Đợt"] + [f"Đợt {i}" for i in range(1, 31)],
                                            state="readonly", font=("Arial", 10), width=10)
        self.stat_filter_dot.pack(side=tk.LEFT, padx=3)
        self.stat_filter_dot.set("Tất cả Đợt")
        self.stat_filter_dot.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        # Bảng hiển thị hóa đơn Tab 2
        self.tree_stats = ttk.Treeview(self.tab2, columns=("ten", "sl", "ngay", "gia", "tong"), show="headings")
        titles = ["Nguyên liệu/Mặt hàng", "Tổng số lượng mua", "Kỳ & Ngày lập hóa đơn", "Đơn giá (VNĐ)",
                  "Tổng thanh toán hóa đơn"]

        for c, t in zip(self.tree_stats["columns"], titles):
            self.tree_stats.heading(c, text=t)
            self.tree_stats.column(c, anchor="center")
            if c == "ngay":
                self.tree_stats.column(c, width=220, anchor="center")
        self.tree_stats.pack(fill="both", expand=True, padx=20, pady=5)

        bottom_frame = tk.Frame(self.tab2, bg="white")
        bottom_frame.pack(fill="x", padx=20, pady=10)
        tk.Button(bottom_frame, text="💰 TÍNH TỔNG CHI PHÍ HOÁ ĐƠN", command=self.sum_all_stats, bg="#27AE60",
                  fg="white", font=("Arial", 11, "bold"), padx=20, pady=5).pack(side="left")

        self.lbl_total_payment = tk.Label(bottom_frame, text="KẾT QUẢ: 0 VNĐ", font=("Arial", 14, "bold"), fg="#C0392B",
                                          bg="white")
        self.lbl_total_payment.pack(side="right")

    def setup_tab_analysis_by_period(self):
        """TAB 3: NƠI THEO DÕI BIẾN ĐỘNG CHI PHÍ THEO KỲ TỰ ĐỘNG"""
        MAU_NAU = "#6F4E37"
        MAU_NEN = "#F5F5F5"

        main_frame = tk.Frame(self.tab4, bg=MAU_NEN)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        tk.Label(main_frame, text="📊 BẢNG THEO DÕI BIẾN ĐỘNG CHI PHÍ THEO KỲ (12 THÁNG TỰ ĐỘNG)",
                 font=("Arial", 14, "bold"), bg=MAU_NEN, fg=MAU_NAU).pack(anchor="w", pady=(0, 15))

        cac_cot = ("thang", "so_dot", "tien_dot")
        self.exp_tree = ttk.Treeview(main_frame, columns=cac_cot, show="headings", height=13)
        self.exp_tree.heading("thang", text="Kỳ phân tích (Tháng)")
        self.exp_tree.heading("so_dot", text="Số đợt nhập hàng")
        self.exp_tree.heading("tien_dot", text="Tổng chi phí nhập hàng (VNĐ)")

        self.exp_tree.column("thang", width=150, anchor="w")
        self.exp_tree.column("so_dot", width=150, anchor="center")
        self.exp_tree.column("tien_dot", width=250, anchor="e")
        self.exp_tree.pack(fill=tk.BOTH, expand=True)

        self.exp_lbl_tong_nam = tk.Label(main_frame, text="TỔNG CHI PHÍ TÍCH LŨY KỲ: 0 VNĐ",
                                         font=("Arial", 13, "bold"), bg=MAU_NEN, fg="red")
        self.exp_lbl_tong_nam.pack(anchor="e", pady=15)

    def setup_tab_report_text(self):
        """TAB 4: CẤU TRÚC LẠI TRÊN DƯỚI ĐỂ TỐI ƯU KHÔNG GIAN BÁO CÁO VÀ KÍCH HOẠT NÚT XUẤT"""
        MAU_NAU = "#6F4E37"
        MAU_NEN = "#F5F5F5"

        main_report_frame = tk.Frame(self.tab3, bg=MAU_NEN)
        main_report_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        top_ctrl = tk.Frame(main_report_frame, bg=MAU_NEN)
        top_ctrl.pack(fill=tk.X, side=tk.TOP, pady=(0, 10))

        tk.Label(top_ctrl, text="Định dạng kết xuất:", bg=MAU_NEN, font=("Arial", 10, "bold"), fg=MAU_NAU).pack(
            side=tk.LEFT, padx=(5, 10))

        self.cbo_format = ttk.Combobox(top_ctrl, values=["Văn bản tổng hợp (.txt)", "File Excel/CSV (.csv)"],
                                       state="readonly", width=25, font=("Arial", 10))
        self.cbo_format.pack(side=tk.LEFT, padx=5)
        self.cbo_format.current(0)

        btn_action_export = tk.Button(top_ctrl, text="🚀 XUẤT PHIẾU BÁO CÁO", font=("Arial", 10, "bold"),
                                      bg="#27AE60", fg="white", activebackground="#1E8449", activeforeground="white",
                                      relief=tk.RAISED, bd=1, padx=15, pady=4, cursor="hand2",
                                      command=self.thuc_hien_xuat_bao_cao)
        btn_action_export.pack(side=tk.LEFT, padx=20)

        lbl_status = tk.Label(top_ctrl, text="● Real-time Kết Nối", fg="#27AE60", bg=MAU_NEN,
                              font=("Arial", 10, "bold"))
        lbl_status.pack(side=tk.RIGHT, padx=5)

        preview_frame = tk.LabelFrame(main_report_frame, text=" Nội dung Phiếu Báo Cáo Tổng Quan (Live Preview) ",
                                      font=("Arial", 11, "bold"), bg="white", fg=MAU_NAU, padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)

        scroll_y = tk.Scrollbar(preview_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.txt_report = tk.Text(preview_frame, font=("Courier New", 11), bg="#FDFEFE", fg="#2C3E50", bd=0,
                                  yscrollcommand=scroll_y.set, wrap=tk.WORD)
        self.txt_report.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.txt_report.yview)

    def thuc_hien_xuat_bao_cao(self):
        """LOGIC THỰC TẾ: TIẾN HÀNH TRÍCH XUẤT VÀ GHI FILE BÁO CÁO DỰA TRÊN ĐỊNH DẠNG ĐÃ CHỌN"""
        loai_file = self.cbo_format.get()
        noi_dung = self.txt_report.get("1.0", tk.END).strip()

        if not noi_dung or "BÁO CÁO THÁNG" not in noi_dung:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy dữ liệu hợp lệ để xuất báo cáo!")
            return

        thoi_gian = datetime.now().strftime("%Y%m%d_%H%M%S")

        if "(.txt)" in loai_file:
            ten_file_goi_y = f"BaoCao_Kho_{thoi_gian}.txt"
            path = filedialog.asksaveasfilename(initialdir="database", initialfile=ten_file_goi_y,
                                                defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if path:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(noi_dung)
                    messagebox.showinfo("Thành công", f"Đã xuất văn bản báo cáo tổng hợp tại:\n{path}")
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể lưu file văn bản: {e}")
        else:
            ten_file_goi_y = f"BaoCao_Kho_{thoi_gian}.csv"
            path = filedialog.asksaveasfilename(initialdir="database", initialfile=ten_file_goi_y,
                                                defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if path:
                try:
                    rows_to_export = []
                    if os.path.exists(self.file_path):
                        with open(self.file_path, "r", encoding="utf-8") as f_src:
                            reader = csv.reader(f_src)
                            rows_to_export = list(reader)

                    if not rows_to_export:
                        rows_to_export.append(self.fields)

                    with open(path, "w", newline="", encoding="utf-8") as f_dest:
                        writer = csv.writer(f_dest)
                        writer.writerows(rows_to_export)
                    messagebox.showinfo("Thành công", f"Đã kết xuất cấu trúc luồng dữ liệu CSV thành công tại:\n{path}")
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể lưu file CSV: {e}")

    def exp_xu_ly_an_hien_o_nhay(self, event):
        pass

    def cap_nhat_bang_chi_tieu_12_thang(self):
        for item in self.exp_tree.get_children():
            self.exp_tree.delete(item)
        tong_ca_nam = 0
        for i in range(1, 13):
            t_name = f"Tháng {i}"
            thang_info = self.du_lieu_chi_tieu[t_name]
            so_dot = len(thang_info["cac_dot"])
            cp_cac_dot = sum(d["chi_phi"] for d in thang_info["cac_dot"])
            tong_ca_nam += cp_cac_dot

            self.exp_tree.insert("", "end", values=(
                t_name,
                f"{so_dot} đợt" if so_dot else "0 đợt",
                f"{cp_cac_dot:,} VNĐ" if cp_cac_dot else "-"
            ))
        self.exp_lbl_tong_nam.config(text=f"TỔNG CHI PHÍ TÍCH LŨY KỲ: {tong_ca_nam:,} VNĐ")

    def xu_ly_chuyen_tab_tong_hop(self, event):
        idx = self.notebook.index(self.notebook.select())
        if idx == 1 or idx == 3:  # Cập nhật và lọc đồng bộ khi chuyển đổi tab
            self.refresh_data()

    def refresh_data(self):
        """HÀM ĐỌC FILE CSV VÀ ĐỒNG BỘ DỮ LIỆU LÊN TOÀN BỘ HỆ THỐNG GIAO DIỆN KHO TRỰC TUYẾN"""
        query = self.ent_search.get().strip().lower()

        # Đọc dữ liệu lọc từ bộ điều khiển Tab 2
        loc_thang = self.stat_filter_thang.get()
        loc_dot = self.stat_filter_dot.get()

        for i in self.tree.get_children(): self.tree.delete(i)
        for i in self.tree_stats.get_children(): self.tree_stats.delete(i)

        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self.fields)
            return

        for i in range(1, 13):
            self.du_lieu_chi_tieu[f"Tháng {i}"]["cac_dot"] = []

        grand_total = 0
        list_for_report = []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # Bỏ qua tiêu đề
                idx = 1
                for r in reader:
                    if not r or len(r) < 5: continue

                    if len(r) == 5:
                        ten, loai, sl_val, gia_val, ngay = r[0], r[1], r[2], r[3], r[4]
                        dv_nhap = "Kilogram (kg)"
                    else:
                        ten, loai, sl_val, dv_nhap, gia_val, ngay = r[0], r[1], r[2], r[3], r[4], r[5]

                    sl = self.clean_number(sl_val)
                    gia = self.clean_number(gia_val)
                    thanh_tien = sl * gia

                    # 1. Đồng bộ lên Tab 1 (Sử dụng thanh tìm kiếm tự do cũ)
                    if query in ten.lower() or query in loai.lower() or query in ngay.lower():
                        self.tree.insert("", "end",
                                         values=(idx, ten, loai, sl, dv_nhap, f"{gia:,}", ngay, f"{thanh_tien:,}"))
                        grand_total += thanh_tien
                        list_for_report.append([ten, loai, str(sl), dv_nhap, str(gia), ngay])
                        idx += 1

                    # 2. Logic lọc thông minh dành riêng cho Tab 2
                    phu_hop_bo_loc_tab2 = True
                    if loc_thang != "Tất cả Tháng" and loc_thang not in ngay:
                        phu_hop_bo_loc_tab2 = False
                    if loc_dot != "Tất cả Đợt" and loc_dot not in ngay:
                        phu_hop_bo_loc_tab2 = False

                    if phu_hop_bo_loc_tab2:
                        self.tree_stats.insert("", "end",
                                               values=(ten, f"{sl} {dv_nhap}", ngay, f"{gia:,}", f"{thanh_tien:,}"))

                    # --- LOGIC TỰ ĐỘNG ĐỒNG BỘ CHI PHÍ SANG PHÂN TÍCH KỲ ---
                    if ngay:
                        try:
                            int_thang = None
                            if "Tháng" in ngay and "-" in ngay:
                                parts = ngay.split("-")
                                int_thang = int(parts[0].replace("Tháng", "").strip())
                            else:
                                parsed_date = datetime.strptime(ngay.strip(), "%d/%m/%Y")
                                int_thang = parsed_date.month

                            month_key = f"Tháng {int_thang}"
                            if month_key in self.du_lieu_chi_tieu:
                                self.du_lieu_chi_tieu[month_key]["cac_dot"].append({
                                    "ngay": ngay, "ten": ten, "sl": sl, "chi_phi": thanh_tien
                                })
                        except Exception:
                            pass

            self.cap_nhat_bang_chi_tieu_12_thang()
            self.generate_custom_report(grand_total, list_for_report)
            self.sum_all_stats()  # Tự động tính lại tổng tiền tương ứng sau khi lọc
        except Exception as e:
            print(f"Lỗi tải dữ liệu: {e}")

    def generate_custom_report(self, total_money, data_list):
        self.txt_report.delete("1.0", "end")
        curr_month = datetime.now().strftime('%m/%Y')
        tong_so_dot_nam = 0
        tong_tien_nam = 0

        for i in range(1, 13):
            thang_info = self.du_lieu_chi_tieu[f"Tháng {i}"]
            tong_so_dot_nam += len(thang_info["cac_dot"])
            tong_tien_nam += sum(d["chi_phi"] for d in thang_info["cac_dot"])

        report_content = f"""
==================================================
              BÁO CÁO THÁNG {curr_month}
==================================================
PHẦN 1: THỐNG KÊ TÀI CHÍNH KHO HÀNG
   - Tổng số mặt hàng: {len(data_list)} loại
   - Tổng chi phí thanh toán kho: {total_money:,} VNĐ

PHẦN 2: CHI TIẾT HÀNG HÓA NHẬP KHO
"""
        for item in data_list:
            ten = item[0]
            loai = item[1]
            dv_nhap = item[3] if len(item) > 3 else "đơn vị"
            report_content += f"   + Nhóm: {loai:<15} | Tên: {ten:<20} | Đơn vị: {dv_nhap}\n"
        report_content += f"""
PHẦN 3: THỐNG KÊ CHI TIÊU TOÀN NĂM (KỲ ĐÁNH GIÁ)
   - Tổng số đợt chi tiêu đã ghi nhận (12 kỳ): {tong_so_dot_nam} đợt
   - Tổng số tiền chi tiêu cả năm: {tong_tien_nam:,} VNĐ
--------------------------------------------------
Hệ thống tự động đồng bộ dữ liệu lúc: {datetime.now().strftime('%H:%M:%S')}
==================================================
"""
        self.txt_report.insert("1.0", report_content)

    def sum_all_stats(self):
        total = 0
        for item in self.tree_stats.get_children():
            total += self.clean_number(self.tree_stats.item(item)['values'][4])
        self.lbl_total_payment.config(text=f"KẾT QUẢ: {total:,} VNĐ")

    def clear_search_and_refresh(self):
        self.ent_search.delete(0, tk.END)
        self.stat_filter_thang.set("Tất cả Tháng")
        self.stat_filter_dot.set("Tất cả Đợt")
        self.refresh_data()

    def edit_item(self):
        sel = self.tree.selection()
        if sel:
            self.open_form("CẬP NHẬT", self.tree.item(sel[0])['values'][1:7])

    def delete_item(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Xác nhận", "Xóa sản phẩm này khỏi cơ sở dữ liệu?"):
            ten = self.tree.item(sel[0])['values'][1]
            rows = []

            with open(self.file_path, "r", encoding="utf-8") as f:
                r = csv.reader(f)
                h = next(r)
                rows = [h] + [line for line in r if line and line[0] != ten]

            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            self.refresh_data()

    def open_form(self, title, edit_data=None):
        """FORM NHẬP LIỆU ĐỘNG: ĐỦ TRƯỜNG CHỌN THÁNG VÀ ĐỢT KHI THÊM/SỬA"""
        win = tk.Toplevel(self.master)
        win.title(title)
        win.geometry("480x560")
        win.grab_set()

        tk.Label(win, text=title, font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = tk.Frame(win, bg="#f5f5f5", padx=20, pady=15)
        form_frame.pack(fill="both", expand=True, padx=10, pady=5)

        tk.Label(form_frame, text="Tên nguyên liệu:", font=("Arial", 10, "bold"), bg="#f5f5f5").grid(row=0, column=0,
                                                                                                     sticky="w", pady=8)
        ent_ten = tk.Entry(form_frame, font=("Arial", 11), width=25)
        ent_ten.grid(row=0, column=1, pady=8, padx=10)

        tk.Label(form_frame, text="Nhóm phân loại:", font=("Arial", 10, "bold"), bg="#f5f5f5").grid(row=1, column=0,
                                                                                                    sticky="w", pady=8)
        cb_loai = ttk.Combobox(form_frame, values=["Nhóm Hạt", "Nhóm Bột", "Nhóm Chất lỏng"], state="readonly",
                               font=("Arial", 10), width=23)
        cb_loai.grid(row=1, column=1, pady=8, padx=10)
        cb_loai.set("Nhóm Hạt")

        tk.Label(form_frame, text="Số lượng:", font=("Arial", 10, "bold"), bg="#f5f5f5").grid(row=2, column=0,
                                                                                              sticky="w", pady=8)
        ent_sl = tk.Entry(form_frame, font=("Arial", 11), width=25)
        ent_sl.grid(row=2, column=1, pady=8, padx=10)

        tk.Label(form_frame, text="Đơn vị nhập:", font=("Arial", 10, "bold"), bg="#f5f5f5").grid(row=3, column=0,
                                                                                                 sticky="w", pady=8)
        cb_dv_nhap = ttk.Combobox(form_frame, state="readonly", font=("Arial", 10), width=23)
        cb_dv_nhap.grid(row=3, column=1, pady=8, padx=10)

        tk.Label(form_frame, text="Giá nhập (VNĐ):", font=("Arial", 10, "bold"), bg="#f5f5f5").grid(row=4, column=0,
                                                                                                    sticky="w", pady=8)
        ent_gia = tk.Entry(form_frame, font=("Arial", 11), width=25)
        ent_gia.grid(row=4, column=1, pady=8, padx=10)

        # Chọn Tháng & Đợt nhập hàng
        tk.Label(form_frame, text="Chọn Kỳ kiểm kho:", font=("Arial", 10, "bold"), bg="#f5f5f5").grid(row=5, column=0,
                                                                                                      sticky="w",
                                                                                                      pady=8)
        ky_frame = tk.Frame(form_frame, bg="#f5f5f5")
        ky_frame.grid(row=5, column=1, sticky="w", pady=8, padx=10)

        cb_thang = ttk.Combobox(ky_frame, values=[f"Tháng {i}" for i in range(1, 13)], state="readonly",
                                font=("Arial", 10), width=9)
        cb_thang.pack(side=tk.LEFT)
        cb_thang.set(f"Tháng {datetime.now().month}")

        tk.Label(ky_frame, text=" - ", bg="#f5f5f5", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=2)

        cb_dot = ttk.Combobox(ky_frame, values=[f"Đợt {i}" for i in range(1, 31)], state="readonly", font=("Arial", 10),
                              width=8)
        cb_dot.pack(side=tk.LEFT)
        cb_dot.set("Đợt 1")

        tk.Label(form_frame, text="Ngày nhập thực tế:", font=("Arial", 10, "bold"), bg="#f5f5f5").grid(row=6, column=0,
                                                                                                       sticky="w",
                                                                                                       pady=8)
        ent_ngay = tk.Entry(form_frame, font=("Arial", 11), width=25)
        ent_ngay.grid(row=6, column=1, pady=8, padx=10)
        ent_ngay.insert(0, datetime.now().strftime("%d/%m/%Y"))

        def on_category_change(event=None):
            cat = cb_loai.get()
            if cat == "Nhóm Hạt":
                cb_dv_nhap.config(values=["Kilogram (kg)", "Thùng (5kg)", "Thùng (10kg)"])
                cb_dv_nhap.set("Kilogram (kg)")
            elif cat == "Nhóm Bột":
                cb_dv_nhap.config(values=["Túi/Gói (500g)", "Túi/Gói (1kg)"])
                cb_dv_nhap.set("Túi/Gói (1kg)")
            elif cat == "Nhóm Chất lỏng":
                cb_dv_nhap.config(values=["Chai", "Hộp", "Can (lít)"])
                cb_dv_nhap.set("Chai")

        cb_loai.bind("<<ComboboxSelected>>", on_category_change)
        on_category_change()

        if edit_data:
            ent_ten.insert(0, edit_data[0])
            ent_ten.config(state="readonly")
            cb_loai.set(edit_data[1])
            on_category_change()

            ent_sl.delete(0, tk.END)
            ent_sl.insert(0, edit_data[2])
            cb_dv_nhap.set(edit_data[3])
            ent_gia.delete(0, tk.END)
            ent_gia.insert(0, edit_data[4])

            raw_ngay = edit_data[5]
            ent_ngay.delete(0, tk.END)
            if "Tháng" in raw_ngay and "(" in raw_ngay:
                try:
                    part_ky, part_date = raw_ngay.split("(")
                    ent_ngay.insert(0, part_date.replace(")", "").strip())
                    parts_ky = part_ky.split("-")
                    cb_thang.set(parts_ky[0].strip())
                    cb_dot.set(parts_ky[1].strip())
                except:
                    ent_ngay.insert(0, raw_ngay)
            else:
                ent_ngay.insert(0, raw_ngay)

        def save():
            ten = ent_ten.get().strip()
            loai = cb_loai.get()
            sl_str = ent_sl.get().strip()
            dv_nhap = cb_dv_nhap.get()
            gia_str = ent_gia.get().strip()
            ngay_thuc_te = ent_ngay.get().strip()

            if not ten or not loai:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin Tên và Phân loại!")
                return

            try:
                sl_val = int(sl_str.replace(',', '').replace('.', ''))
                if sl_val <= 0: messagebox.showerror("Lỗi dữ liệu", "Số lượng hàng hóa phải lớn hơn 0!"); return
            except ValueError:
                messagebox.showerror("Lỗi dữ liệu", "Số lượng không hợp lệ!"); return

            try:
                gia_val = int(gia_str.replace(',', '').replace('.', '').replace(' VNĐ', ''))
                if gia_val <= 0: messagebox.showerror("Lỗi dữ liệu", "Giá nhập phải lớn hơn 0 VNĐ!"); return
            except ValueError:
                messagebox.showerror("Lỗi dữ liệu", "Đơn giá nhập không hợp lệ!"); return

            try:
                datetime.strptime(ngay_thuc_te, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Lỗi dữ liệu", "Định dạng ngày chuẩn phải là DD/MM/YYYY."); return

            ngay_tich_hop = f"{cb_thang.get()} - {cb_dot.get()} ({ngay_thuc_te})"
            new_row = [ten, loai, str(sl_val), dv_nhap, str(gia_val), ngay_tich_hop]

            all_d = []
            with open(self.file_path, "r", encoding="utf-8") as f:
                r = csv.reader(f)
                h = next(r, None)
                if h: all_d.append(self.fields)
                for line in r:
                    if line and line[0] != ten: all_d.append(line)

            all_d.append(new_row)

            try:
                with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                    csv.writer(f).writerows(all_d)
                self.refresh_data()
                win.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

        tk.Button(win, text="XÁC NHẬN", bg="#8B4513", fg="white", font=("Arial", 11, "bold"), command=save, width=15,
                  height=2, bd=0, cursor="hand2").pack(pady=15)

# --- END OF FILE inventory.py ---