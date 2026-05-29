import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import csv


class LoginPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.master.configure(bg="#f5f5f5")
        self.view()

    def view(self):
        """🖥️ KHỞI TẠO GIAO DIỆN FORM ĐĂNG NHẬP (MÀU CHỦ ĐẠO: NÂU CÀ PHÊ)"""
        header_color = "#6F4E37"
        header = tk.Frame(self.master, bg=header_color, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="☕ ĐĂNG NHẬP HỆ THỐNG",
                 font=("Arial", 16, "bold"), fg="white", bg=header_color).pack(pady=15)

        f = tk.Frame(self.master, bg="#f5f5f5")
        f.pack(pady=30)

        lbl_style = {"font": ("Arial", 10, "bold"), "bg": "#f5f5f5", "fg": "#333"}

        """Ô nhập Tài khoản (Username)"""
        tk.Label(f, text="Username:", **lbl_style).grid(row=0, column=0, pady=10, sticky="e")
        self.ent_user = tk.Entry(f, font=("Arial", 11), width=25)
        self.ent_user.grid(row=0, column=1, padx=10)

        """Ô nhập Mật khẩu - Có cấu hình ẩn ký tự `show="*"` để bảo mật"""
        tk.Label(f, text="Password:", **lbl_style).grid(row=1, column=0, pady=10, sticky="e")
        self.ent_pass = tk.Entry(f, show="*", font=("Arial", 11), width=25)
        self.ent_pass.grid(row=1, column=1, padx=10)

        """Hộp chọn Vai trò (Role Combobox) - Chặn không cho người dùng tự gõ chữ (`state="readonly"`)"""
        tk.Label(f, text="Chức vụ:", **lbl_style).grid(row=2, column=0, pady=10, sticky="e")
        self.cb_role = ttk.Combobox(f, values=["Quản lý", "Nhân viên"], state="readonly", width=23)
        self.cb_role.set("Nhân viên")
        self.cb_role.grid(row=2, column=1, padx=10)

        btn_frame = tk.Frame(self.master, bg="#f5f5f5")
        btn_frame.pack(pady=20)

        """Nút Đăng nhập kích hoạt hàm kiểm tra `self.login`"""
        tk.Button(btn_frame, text="ĐĂNG NHẬP", command=self.login,
                  bg="#6F4E37", fg="white", font=("Arial", 10, "bold"),
                  width=15, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)

        """Nút Tạo tài khoản chuyển hướng thông qua app_manager"""
        tk.Button(btn_frame, text="TẠO TÀI KHOẢN", command=self.app_manager.show_taotk_page,
                  bg="#6F4E37", fg="white", font=("Arial", 10, "bold"),
                  width=15, height=2, bd=0, cursor="hand2").pack(side="left", padx=10)

    def login(self):
        """🔐 THUẬT TOÁN XÁC THỰC TÀI KHOẢN & PHÂN QUYỀN TRUY CẬP"""
        user = self.ent_user.get().strip()
        pw = self.ent_pass.get().strip()
        role_selected = self.cb_role.get()

        """Kiểm tra trống thông tin đầu vào"""
        if not user or not pw:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đủ thông tin")
            return

        try:
            """ Đọc file cơ sở dữ liệu tài khoản"""
            with open("database/tk.csv", "r", encoding="utf-8") as f:
                lines = f.readlines()

                """Vòng lặp bỏ qua dòng tiêu đề [1:], quét qua từng tài khoản trong hệ thống"""
                for line in lines[1:]:
                    if not line.strip(): continue
                    data = line.strip().split(",")

                    if len(data) >= 2:
                        db_user = data[0]
                        db_pass = data[1]
                        """Nếu cột role (index 3) bị trống, tự động gán là "Nhân viên"""
                        db_role = data[3] if len(data) > 3 else "Nhân viên"

                        """Kiểm tra 3 điều kiện khớp khoá"""
                        if user == db_user and pw == db_pass:
                            if role_selected == db_role:
                                messagebox.showinfo("Thành công", f"Chào mừng {role_selected} {user}")
                                """Ghi nhận trạng thái Role hiện tại vào bộ quản lý ứng dụng để các trang sau kiểm tra phân quyền"""
                                self.app_manager.current_role = role_selected

                                # Chế độ ghi nối đuôi `"a"` (Append) để lưu thêm vết đăng nhập mới mà không làm mất log cũ
                                try:
                                    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                                    with open("database/history.csv", "a", newline="", encoding="utf-8") as hf:
                                        csv.writer(hf).writerow([user, role_selected, now])
                                except:
                                    pass  # Cơ chế bọc lỗi an toàn: Nếu file log bị lỗi, hệ thống vẫn cho phép user vào app tiếp

                                # ĐỊNH TUYẾN GIAO DIỆN SAU ĐĂNG NHẬP SỬ DỤNG BIẾN ROLE
                                if role_selected == "Quản lý":
                                    self.app_manager.show_manager_menu()  # Quản lý được vào Menu tổng
                                else:
                                    self.app_manager.show_inventory_page()  # Nhân viên chỉ được nhảy thẳng vào trang kho
                                return

                # Nếu quét hết file mà không trùng khớp cụm điều kiện nào
                messagebox.showerror("Lỗi", "Sai tài khoản, mật khẩu hoặc chức vụ")
        except FileNotFoundError:
            # Cơ chế cảnh báo lỗi hệ thống nếu file database bị di dời hoặc xóa nhầm
            messagebox.showerror("Lỗi", "Không tìm thấy file database/tk.csv")