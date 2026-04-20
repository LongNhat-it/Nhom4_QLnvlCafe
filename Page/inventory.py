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
        self.file_path = "database/nguyenlieu.csv"
        # Định nghĩa các trường dữ liệu cố định
        self.fields = ["Mã", "Tên", "Loại", "Tồn", "Đơn vị", "Giá"]
        self.view()
        self.refresh_data()

    def view(self):
        header_bg = "#6F4E37"
        header = tk.Frame(self.master, bg=header_bg, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="☕ QUẢN LÝ KHO NGUYÊN LIỆU", font=("Arial", 20, "bold"),
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

        tk.Label(self.tab2, text="Nội dung Công thức pha chế", bg="white", font=("Arial", 12)).pack(pady=50)
        tk.Label(self.tab3, text="Thống kê doanh thu & chi phí", bg="white", font=("Arial", 12)).pack(pady=50)
        self.lbl_alert = tk.Label(self.tab4, text="Cảnh báo hàng hóa", bg="#FDECEC", pady=20, font=("Arial", 11))
        self.lbl_alert.pack(fill="x", padx=20, pady=20)

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
            self.tree.heading(c, text=t)
            self.tree.column(c, width=100, anchor="center")

        self.tree.column("ten", width=200, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.tag_configure('low', background='#ffcccc')

    def refresh_data(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["Mã", "Tên", "Loại", "Tồn", "Đơn vị", "Giá", "Ngày", "Trạng thái"])
            return

        low_stock_list = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)
            for idx, r in enumerate(reader, 1):
                if len(r) >= 6:
                    is_low = int(r[3]) < 10
                    tag = 'low' if is_low else ''
                    if is_low: low_stock_list.append(r[1])
                    self.tree.insert("", "end", values=(idx, r[0], r[1], r[2], r[3], r[4], r[5]), tags=(tag,))

        if low_stock_list:
            self.lbl_alert.config(text=f"⚠ CẢNH BÁO HẾT HÀNG: {', '.join(low_stock_list)}", fg="#C0392B")
        else:
            self.lbl_alert.config(text="✅ Kho hàng ổn định", fg="green")

    def edit_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chú ý", "Vui lòng chọn nguyên liệu cần sửa!")
            return
        data = self.tree.item(selected[0])['values'][1:]
        self.open_form("CẬP NHẬT NGUYÊN LIỆU", data)

    def delete_item(self):
        selected = self.tree.selection()
        if not selected or not messagebox.askyesno("Xác nhận", "Xóa nguyên liệu này?"): return
        ma_xoa = self.tree.item(selected[0])['values'][1]

        rows = []
        with open(self.file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = [header] + [r for r in reader if r and r[0] != str(ma_xoa)]

        with open(self.file_path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
        self.refresh_data()

    def open_form(self, title, edit_data=None):
        win = tk.Toplevel(self.master)
        win.title(title)
        win.geometry("450x650")
        win.grab_set()

        win.grid_columnconfigure(0, weight=1)
        win.grid_columnconfigure(1, weight=1)

        tk.Label(win, text=title, font=("Arial", 16, "bold")).grid(row=0, columnspan=2, pady=30)

        ents = {}
        for i, field_name in enumerate(self.fields):
            tk.Label(win, text=f"{field_name}:").grid(row=i + 1, column=0, sticky="e", padx=10, pady=10)
            e = tk.Entry(win, width=30)
            e.grid(row=i + 1, column=1, sticky="w", padx=10)

            if edit_data is not None:
                e.insert(0, edit_data[i])
                if i == 0: e.config(state="readonly")
            ents[field_name] = e

        def save():
            new_row = [ents[f].get() for f in self.fields]
            if not new_row[0] or not new_row[1]:
                messagebox.showerror("Lỗi", "Mã và Tên không được để trống!")
                return

            new_row += [datetime.now().strftime("%d/%m/%Y"), "Sẵn sàng"]
            all_data = []
            with open(self.file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                all_data.append(header)
                for r in reader:
                    if r and r[0] == new_row[0]: continue
                    all_data.append(r)

            all_data.append(new_row)
            with open(self.file_path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(all_data)

            self.refresh_data()
            win.destroy()
            messagebox.showinfo("Thành công", "Đã cập nhật dữ liệu kho!")

        tk.Button(win, text="CẬP NHẬT", bg="#8B4513", fg="white", font=("Arial", 10, "bold"),
                  command=save, width=15, height=2).grid(row=8, columnspan=2, pady=(30, 10))

        tk.Button(win, text="HỦY", bg="#8B4513", fg="white", command=win.destroy,
                  width=15, height=2).grid(row=9, columnspan=2, pady=5)