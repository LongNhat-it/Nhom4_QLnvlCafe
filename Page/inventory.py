import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime
from common.button import CustomButton


class InventoryPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        # Các đường dẫn file database
        self.file_path = "database/nguyenlieu.csv"
        self.recipe_file = "database/congthuc.csv"

        self.fields = ["Mã", "Tên", "Loại", "Tồn", "Đơn vị", "Giá"]

        self.view()
        self.refresh_data()
        self.refresh_recipes()

    def view(self):
        header_bg = "#6F4E37"
        header = tk.Frame(self.master, bg=header_bg, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="☕ QUẢN LÝ KHO & CÔNG THỨC", font=("Arial", 20, "bold"),
                 fg="white", bg=header_bg).pack(side="left", padx=20)

        btn_logout = tk.Button(header, text="ĐĂNG XUẤT", bg="#c0392b", fg="white",
                               font=("Arial", 10, "bold"), bd=0, padx=15, cursor="hand2",
                               command=self.app_manager.show_login_page)
        btn_logout.pack(side="right", padx=20, pady=15)

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab1 = tk.Frame(self.notebook, bg="white")
        self.tab2 = tk.Frame(self.notebook, bg="white")
        self.tab3 = tk.Frame(self.notebook, bg="white")
        self.tab4 = tk.Frame(self.notebook, bg="white")

        self.notebook.add(self.tab1, text=" 1. Quản lý kho ")
        self.notebook.add(self.tab2, text=" 2. Công thức ")
        self.notebook.add(self.tab3, text=" 3. Thống kê ")
        self.notebook.add(self.tab4, text=" 4. Báo cáo ")

        self.setup_tab_inventory()
        self.setup_tab_recipe()
        self.setup_tab_stats()
        self.setup_tab_reports()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        if self.notebook.index(self.notebook.select()) == 3:
            self.generate_report_logic()

    # kho hang
    def setup_tab_inventory(self):
        toolbar = tk.Frame(self.tab1, bg="white", pady=10)
        toolbar.pack(fill="x")
        CustomButton(toolbar, text="🔄 Làm mới", command=self.refresh_data, style_type="info").pack(side="left", padx=5)
        CustomButton(toolbar, text="➕ Nhập hàng", command=lambda: self.open_form("NHẬP HÀNG MỚI"),
                     style_type="success").pack(side="left", padx=5)
        CustomButton(toolbar, text="📝 Sửa thông tin", command=self.edit_item, style_type="warning").pack(side="left",
                                                                                                         padx=5)
        CustomButton(toolbar, text="🗑️ Xóa", command=self.delete_item, style_type="danger").pack(side="left", padx=5)

        self.cols = ("stt", "ma", "ten", "loai", "ton", "donvi", "gia")
        self.tree = ttk.Treeview(self.tab1, columns=self.cols, show="headings")
        titles = ["STT", "Mã", "Tên Nguyên Liệu", "Loại", "Tồn Kho", "Đơn Vị", "Giá Nhập"]
        for c, t in zip(self.cols, titles):
            self.tree.heading(c, text=t);
            self.tree.column(c, width=100, anchor="center")
        self.tree.column("ten", width=200, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.tag_configure('low', background='#ffcccc')

    # cong thuc
    def setup_tab_recipe(self): #Giao diện bảng công thức
        toolbar = tk.Frame(self.tab2, bg="white", pady=10)
        toolbar.pack(fill="x")
        CustomButton(toolbar, text="➕ Tạo công thức", command=self.open_recipe_form, style_type="success").pack(
            side="left", padx=5)
        CustomButton(toolbar, text="📝 Sửa", command=self.edit_recipe, style_type="warning").pack(side="left", padx=5)
        CustomButton(toolbar, text="🗑️ Xóa", command=self.delete_recipe, style_type="danger").pack(side="left", padx=5)

        self.recipe_tree = ttk.Treeview(self.tab2, columns=("mon", "gia", "note"), show="headings")
        self.recipe_tree.heading("mon", text="Tên Món");
        self.recipe_tree.heading("gia", text="Giá Bán");
        self.recipe_tree.heading("note", text="Ghi chú")
        self.recipe_tree.pack(fill="both", expand=True, padx=10, pady=10)

    # thong ke
    def setup_tab_stats(self): #Giao diện thống kê
        toolbar = tk.Frame(self.tab3, bg="white", pady=10)
        toolbar.pack(fill="x")
        CustomButton(toolbar, text="📊 TẠO BẢNG THỐNG KÊ TỒN KHO", command=self.generate_stats,
                     style_type="warning").pack(side="left", padx=10)

        self.stats_tree = ttk.Treeview(self.tab3, columns=("n", "s", "v"), show="headings")
        self.stats_tree.heading("n", text="Tên Nguyên Liệu");
        self.stats_tree.heading("s", text="Số Lượng Tồn");
        self.stats_tree.heading("v", text="Giá Trị Tồn")
        self.stats_tree.pack(fill="both", expand=True, padx=10, pady=10)

    # bao cao
    def setup_tab_reports(self): #Giao diện báo cáo
        frame = tk.Frame(self.tab4, bg="white", padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="📊 BÁO CÁO TỔNG QUAN HÀNG HÓA", font=("Arial", 14, "bold"), bg="white").pack(anchor="center")
        self.txt_report = tk.Text(frame, font=("Courier New", 12), bg="#F8F9FA", padx=10, pady=10)
        self.txt_report.pack(fill="both", expand=True, pady=10)

    def generate_report_logic(self): #Bảng báo cáo kho hàng tự động
        """Tự động tính toán khi xem Tab Báo cáo"""
        if not os.path.exists(self.file_path): return
        total_money, total_items, low_stock = 0, 0, []
        with open(self.file_path, "r", encoding="utf-8") as f:
            rdr = csv.reader(f);
            next(rdr)
            for r in rdr:
                if r:
                    total_items += 1
                    total_money += int(r[3]) * int(r[5])
                    if int(r[3]) < 10: low_stock.append(r[1])

        self.txt_report.delete("1.0", "end")
        content = f"""
==========================================
        BÁO CÁO KHO HÀNG TỰ ĐỘNG
        Ngày: {datetime.now().strftime('%d/%m/%Y %H:%M')}
==========================================

1. TỔNG SỐ NGUYÊN LIỆU: {total_items} mặt hàng
2. TỔNG GIÁ TRỊ TỒN KHO: {total_money:,} VNĐ

3. CẢNH BÁO NHẬP HÀNG:
   {f"Cần nhập thêm: {', '.join(low_stock)}" if low_stock else "Tất cả mặt hàng đều ổn định."}

------------------------------------------
Hệ thống tự động cập nhật số liệu mới nhất.
==========================================
"""
        self.txt_report.insert("1.0", content)

    def generate_stats(self): #Tạo nguyên vật liệu
        for i in self.stats_tree.get_children(): self.stats_tree.delete(i)
        if os.path.exists(self.file_path):
            with open(self.file_path, "r", encoding="utf-8") as f:
                rdr = csv.reader(f);
                next(rdr)
                for r in rdr:
                    thanh_tien = int(r[3]) * int(r[5])
                    self.stats_tree.insert("", "end", values=(r[1], r[3], f"{thanh_tien:,} VNĐ"))

    def refresh_data(self): #Làm mới nguyên vật liệu
        for i in self.tree.get_children(): self.tree.delete(i)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["Mã", "Tên", "Loại", "Tồn", "Đơn vị", "Giá", "Ngày", "Trạng thái"])
            return
        with open(self.file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f);
            next(reader, None)
            for idx, r in enumerate(reader, 1):
                if len(r) >= 6:
                    tag = 'low' if int(r[3]) < 10 else ''
                    self.tree.insert("", "end", values=(idx, r[0], r[1], r[2], r[3], r[4], r[5]), tags=(tag,))

    def edit_item(self): #Chỉnh sửa nguyên vật liệu
        sel = self.tree.selection()
        if sel: self.open_form("CẬP NHẬT NGUYÊN LIỆU", self.tree.item(sel[0])['values'][1:])

    def delete_item(self): #Xóa nguyên vật liệu
        sel = self.tree.selection()
        if not sel or not messagebox.askyesno("Xác nhận", "Xóa nguyên liệu này?"): return
        ma_xoa = self.tree.item(sel[0])['values'][1]
        rows = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            rdr = csv.reader(f);
            header = next(rdr)
            rows = [header] + [r for r in rdr if r and r[0] != str(ma_xoa)]
        with open(self.file_path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
        self.refresh_data()

    def open_form(self, title, edit_data=None):
        win = tk.Toplevel(self.master);
        win.geometry("450x650");
        win.grab_set()
        tk.Label(win, text=title, font=("Arial", 16, "bold")).pack(pady=20)
        ents = {}
        for f_name in self.fields:
            tk.Label(win, text=f"{f_name}:").pack()
            e = tk.Entry(win, width=30);
            e.pack(pady=5)
            if edit_data:
                idx = self.fields.index(f_name);
                e.insert(0, edit_data[idx])
                if idx == 0: e.config(state="readonly")
            ents[f_name] = e

        def save():
            new = [ents[f].get() for f in self.fields] + [datetime.now().strftime("%d/%m/%Y"), "Sẵn sàng"]
            all_d = []
            with open(self.file_path, "r", encoding="utf-8") as f:
                rdr = csv.reader(f);
                all_d.append(next(rdr))
                for r in rdr:
                    if r and r[0] != new[0]: all_d.append(r)
            all_d.append(new)
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(all_d)
            self.refresh_data();
            win.destroy()

        tk.Button(win, text="CẬP NHẬT", command=save, bg="#8B4513", fg="white", width=15, height=2).pack(pady=20)

    def refresh_recipes(self):
        for i in self.recipe_tree.get_children(): self.recipe_tree.delete(i)
        if os.path.exists(self.recipe_file):
            with open(self.recipe_file, "r", encoding="utf-8") as f:
                for r in csv.reader(f): self.recipe_tree.insert("", "end", values=r)

    def open_recipe_form(self, edit_data=None):
        win = tk.Toplevel(self.master);
        win.geometry("300x400");
        win.grab_set()
        tk.Label(win, text="Tên món:").pack();
        e_n = tk.Entry(win);
        e_n.pack()
        tk.Label(win, text="Giá bán:").pack();
        e_p = tk.Entry(win);
        e_p.pack()
        tk.Label(win, text="Ghi chú:").pack();
        txt = tk.Text(win, height=5);
        txt.pack()
        if edit_data:
            e_n.insert(0, edit_data[0]);
            e_p.insert(0, edit_data[1]);
            txt.insert("1.0", edit_data[2])

        def save():
            rows = []
            if os.path.exists(self.recipe_file):
                with open(self.recipe_file, "r", encoding="utf-8") as f:
                    rows = [r for r in csv.reader(f) if r and r[0] != e_n.get()]
            rows.append([e_n.get(), e_p.get(), txt.get("1.0", "end-1c")])
            with open(self.recipe_file, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            self.refresh_recipes();
            win.destroy()

        tk.Button(win, text="LƯU", command=save, bg="green", fg="white").pack(pady=10)

    def edit_recipe(self):
        sel = self.recipe_tree.selection()
        if sel: self.open_recipe_form(self.recipe_tree.item(sel[0])['values'])

    def delete_recipe(self):
        selected = self.recipe_tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn món cần xóa trong bảng công thức!")
            return

        ten_mon = str(self.recipe_tree.item(selected[0])['values'][0]).strip()

        if not messagebox.askyesno("Xác nhận", f"Xóa công thức món: {ten_mon}?"):
            return

        try:
            rows_keep = []
            if os.path.exists(self.recipe_file):
                with open(self.recipe_file, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    for r in reader:
                        if r and str(r[0]).strip() != ten_mon:
                            rows_keep.append(r)

                with open(self.recipe_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(rows_keep)

                self.refresh_recipes()
                messagebox.showinfo("Xong", f"Đã xóa công thức món {ten_mon}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa công thức: {e}")