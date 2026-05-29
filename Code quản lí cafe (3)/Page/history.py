import tkinter as tk
from tkinter import ttk
import csv
import os
from common.button import CustomButton


class HistoryPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.view()
        self.load_history()

    def view(self):
        """🖥️ KHỞI TẠO GIAO DIỆN BẢNG NHẬT KÝ ĐĂNG NHẬP"""
        """Tiêu đề trang"""
        tk.Label(self.master, text="📜 LỊCH SỬ ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 18, "bold"), fg="#2c3e50").pack(
            pady=20)

        tool_frame = tk.Frame(self.master)
        tool_frame.pack(pady=10, fill="x", padx=20)

        CustomButton(tool_frame, text="🔙 Quay lại",
                     command=self.app_manager.show_quanlytk_page,
                     style_type="secondary").pack(side="left")

        """4 cột thông tin cơ bản để giám sát hoạt động đăng nhập."""
        columns = ("stt", "user", "role", "time")
        self.tree = ttk.Treeview(self.master, columns=columns, show="headings")

        self.tree.heading("stt", text="STT")
        self.tree.heading("user", text="Người dùng")
        self.tree.heading("role", text="Chức vụ")
        self.tree.heading("time", text="Thời gian đăng nhập")

        self.tree.column("stt", width=50, anchor="center")
        self.tree.column("user", width=150, anchor="center")
        self.tree.column("role", width=120, anchor="center")
        self.tree.column("time", width=250, anchor="center")

        self.tree.pack(expand=True, fill="both", padx=20, pady=10)
    def load_history(self):
        """📂 THUẬT TOÁN ĐỌC VÀ ĐẢO NGƯỢC DỮ LIỆU TỪ FILE PHẲNG (CSV)"""

        if not os.path.exists("database/history.csv"):
            # Nếu file chưa tồn tại hoặc chưa ai đăng nhập lần nào, tạo file trống để tránh crash hệ thống
            with open("database/history.csv", "w", newline="", encoding="utf-8") as f:
                pass
            return
        # Dọn sạch các dòng cũ trên bảng Treeview trước khi nạp dữ liệu mới
        for item in self.tree.get_children(): self.tree.delete(item)
        try:
            with open("database/history.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                data = list(reader)  # Đọc toàn bộ các dòng log vào một danh sách (list) trên RAM

                # 🔄 [THUẬT TOÁN ĐẢO NGƯỢC DANH SÁCH]:
                # Sử dụng `reversed(data)` để duyệt file từ dưới lên trên, giúp quản lí thấy tài khoản đăng nhập mới nhất

                for idx, row in enumerate(reversed(data), 1):
                    if len(row) >= 3:
                        # row[0]: Tên tài khoản, row[1]: Vai trò (Quản lý/Nhân viên), row[2]: Thời gian timestamp
                        self.tree.insert("", "end", values=(idx, row[0], row[1], row[2]))
        except Exception as e:
            # Bắt lỗi an toàn nếu file CSV bị hỏng hoặc bị khóa bởi một tiến trình khác bên ngoài
            print(f"Lỗi tải lịch sử: {e}")