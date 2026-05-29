import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from common.button import CustomButton


class QuanLyTKPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager

        self.search_var = None
        self.ent_search = None
        self.tree = None

        self.config()
        self.view()
        self.load_accounts()

    def config(self):
        self.master.title("Quản lý nhân sự kho")
        self.master.geometry("1200x550")

    def view(self):
        """🖥️ KHỞI TẠO GIAO DIỆN BẢNG DANH SÁCH TÀI KHOẢN VÀ THANH CÔNG CỤ"""
        header_frame = tk.Frame(self.master, bg="#5D4037", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="☕ DANH SÁCH TÀI KHOẢN NHÂN VIÊN", font=("Arial", 18, "bold"), fg="white",
                 bg="#5D4037").pack(side="left", padx=20, pady=15)

        CustomButton(header_frame, text="🔙 VỀ MENU", command=lambda: self.app_manager.show_manager_menu(),
                     style_type="danger").pack(side="right", padx=20, pady=15)

        tool_frame = tk.Frame(self.master, bg="#f5f5f5")
        tool_frame.pack(pady=10, fill="x", padx=20)

        CustomButton(tool_frame, text="🔄 Làm mới", command=self.load_accounts, style_type="info").pack(side="left",
                                                                                                       padx=5)
        CustomButton(tool_frame, text="➕ Thêm", command=lambda: self.app_manager.show_taotk_page(from_admin=True),
                     style_type="success").pack(side="left", padx=5)

        CustomButton(tool_frame, text="✏️ Sửa", command=self.edit_account, style_type="warning").pack(side="left",
                                                                                                      padx=5)
        CustomButton(tool_frame, text="🗑️ Xóa", command=self.delete_account, style_type="danger").pack(side="left",
                                                                                                       padx=5)

        CustomButton(tool_frame, text="📜 Lịch sử", command=self.app_manager.show_history_page,
                     style_type="primary").pack(side="right", padx=5)
        CustomButton(tool_frame, text="🔍", command=self.search_account, style_type="primary").pack(side="right", padx=2)

        # Sử dụng StringVar với sự kiện trace_add lắng nghe sự kiện gõ phím. Người dùng gõ đến đâu,
        # hệ thống tự động bóc tách chuỗi gõ đó và đẩy vào hàm load_accounts() để lọc trực tiếp đến đấy.
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda n, i, m: self.load_accounts(self.search_var.get().strip().lower()))

        self.ent_search = tk.Entry(tool_frame, font=("Arial", 11), width=50, textvariable=self.search_var)
        self.ent_search.pack(side="right", padx=5)
        tk.Label(tool_frame, text="Tìm kiếm:", font=("Arial", 10), bg="#f5f5f5").pack(side="right", padx=5)

        columns = ("stt", "user", "pass", "gmail", "role")
        self.tree = ttk.Treeview(self.master, columns=columns, show="headings", height=15)
        headers = {"stt": "STT", "user": "Tên đăng nhập", "pass": "Mật khẩu", "gmail": "Email", "role": "Chức vụ"}
        for col in columns:
            self.tree.heading(col, text=headers[col])
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)

    def search_account(self):
        """🔍 KÍCH HOẠT TÌM KIẾM THỦ CÔNG KHI BẤM NÚT KÍNH LÚP"""
        query = self.ent_search.get().strip().lower()
        self.load_accounts(query)

    def load_accounts(self, search_query=""):
        """📂 THUẬT TOÁN ĐỌC FILE CSV, ÁP DỤNG BỘ LỌC VÀ MÃ HÓA MẬT KHẨU KHI HIỂN THỊ"""
        for item in self.tree.get_children(): self.tree.delete(item)
        if not os.path.exists("database/tk.csv"): return
        try:
            with open("database/tk.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # Bỏ qua dòng tiêu đề của file CSV
                idx_counter = 1
                for row in reader:
                    if len(row) >= 2:
                        user, gmail, role = row[0], row[2] if len(row) > 2 else "", row[3] if len(
                            row) > 3 else "Nhân viên"

                        if search_query in user.lower() or search_query in gmail.lower():

                            display_pass = "*" * len(row[1])

                            self.tree.insert("", "end", values=(idx_counter, user, display_pass, gmail, role))
                            idx_counter += 1
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {e}")

    def delete_account(self):
        """🗑️ THUẬT TOÁN XÓA TÀI KHOẢN TRÊN FILE CSV"""
        selected = self.tree.selection()
        if not selected: return
        user_to_del = self.tree.item(selected[0])['values'][1]  # Lấy Username từ dòng được chọn

        if messagebox.askyesno("Xác nhận", f"Xóa tài khoản {user_to_del}?"):
            rows = []
            # Đọc toàn bộ danh sách tài khoản hiện tại vào RAM
            with open("database/tk.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                # Lọc loại bỏ tài khoản có tên trùng khớp với `user_to_del`
                rows = [header] + [row for row in reader if row and row[0] != user_to_del]

            # Ghi đè danh sách đã lọc ngược trở lại file CSV
            # 🚀 Hướng lên SQL: "DELETE FROM tai_khoan WHERE username = ?"
            with open("database/tk.csv", "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(rows)
            self.load_accounts()  # Làm mới lại bảng hiển thị sau khi xóa

    def edit_account(self):
        """✏️ ĐIỀU HƯỚNG SỬA TÀI KHOẢN"""
        selected = self.tree.selection()
        if not selected: return
        user = self.tree.item(selected[0])['values'][1]  # Trích xuất Username được chọn
        # Chuyển hướng sang trang Sửa tài khoản (suatk_page) và truyền theo tên User cần sửa
        self.app_manager.show_suatk_page(user)