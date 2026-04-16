import tkinter as tk
from tkinter import messagebox, ttk
import random
from datetime import datetime, timedelta

# --- CẤU HÌNH GIAO DIỆN CAFE ---
COLOR_DARK_COFFEE = "#3D2B1F"
COLOR_BROWN = "#6F4E37"
COLOR_CREAM = "#FDF5E6"
COLOR_WHITE = "#FFFFFF"

# --- CƠ SỞ DỮ LIỆU TẠM THỜI ---
# Cập nhật users dùng Email làm key
users = {"admin@gmail.com": {"name": "Admin", "pass": "123456"}}

kho_nguyen_lieu = {
    "Hạt Cà Phê Robusta": {"ton_kho": 24, "dv": "kg", "gia_nhap": 150000},
    "Sữa đặc Ngôi Sao": {"ton_kho": 30, "dv": "lon", "gia_nhap": 18000},
    "Sữa tươi Long Thành": {"ton_kho": 15, "dv": "túi", "gia_nhap": 35000},
    "Bột Matcha Nhật": {"ton_kho": 5, "dv": "kg", "gia_nhap": 450000},
    "Siro Đào Pháp": {"ton_kho": 10, "dv": "chai", "gia_nhap": 120000}
}

lich_su_nhap_xuat = []  # Lưu dict: {'ngay':.., 'loai':.., 'ten':.., 'sl':.., 'tong_tien':..}
doanh_thu_thang = []  # Lưu doanh thu ngẫu nhiên

# Tạo dữ liệu ảo cho Doanh thu 6 tháng gần nhất
for i in range(6, 0, -1):
    thang = (datetime.now() - timedelta(days=30 * i)).strftime("%m/%Y")
    dt = random.randint(30, 150) * 1000000  # Doanh thu 30tr - 150tr
    cp = random.randint(10, 40) * 1000000  # Chi phí 10tr - 40tr
    doanh_thu_thang.append({"thang": thang, "doanh_thu": dt, "chi_phi": cp, "loi_nhuan": dt - cp})


class CoffeeSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Quản Lý Cafe")
        self.root.geometry("950x650")
        self.root.configure(bg=COLOR_WHITE)
        self.current_user = ""
        self.setup_login_ui()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ==========================================
    # PHẦN 1: ĐĂNG NHẬP & ĐĂNG KÝ (Dùng Email)
    # ==========================================
    def create_input(self, parent, label_text, is_password=False):
        frame = tk.Frame(parent, bg=COLOR_WHITE)
        frame.pack(fill="x", padx=50, pady=5)
        tk.Label(frame, text=label_text, bg=COLOR_WHITE, fg=COLOR_BROWN, font=("Arial", 10, "bold")).pack(anchor="w")
        entry = tk.Entry(frame, font=("Arial", 11), bg="#F8F9FA", bd=1, show="*" if is_password else "")
        entry.pack(fill="x", ipady=8, pady=(5, 10))
        return entry

    def setup_login_ui(self):
        self.clear_window()
        self.root.geometry("400x550")

        tk.Label(self.root, text="☕", font=("Arial", 60), bg=COLOR_WHITE, fg=COLOR_BROWN).pack(pady=(40, 10))
        tk.Label(self.root, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 16, "bold"), bg=COLOR_WHITE,
                 fg=COLOR_DARK_COFFEE).pack(pady=(0, 20))

        self.ent_email = self.create_input(self.root, "Email đăng nhập:")
        self.ent_pass = self.create_input(self.root, "Mật khẩu:", is_password=True)

        tk.Button(self.root, text="ĐĂNG NHẬP", command=self.handle_login, bg=COLOR_BROWN, fg=COLOR_WHITE,
                  font=("Arial", 11, "bold"), bd=0, cursor="hand2").pack(fill="x", padx=50, pady=20, ipady=10)
        tk.Button(self.root, text="Tạo tài khoản mới", command=self.setup_register_ui, fg="#2980B9", bg=COLOR_WHITE,
                  bd=0, font=("Arial", 9, "underline"), cursor="hand2").pack()

    def setup_register_ui(self):
        self.clear_window()
        tk.Label(self.root, text="TẠO TÀI KHOẢN", font=("Arial", 16, "bold"), bg=COLOR_WHITE, fg=COLOR_BROWN).pack(
            pady=30)

        self.reg_name = self.create_input(self.root, "Họ và tên:")
        self.reg_email = self.create_input(self.root, "Email:")
        self.reg_pass = self.create_input(self.root, "Mật khẩu:", is_password=True)

        tk.Button(self.root, text="ĐĂNG KÝ", command=self.handle_register, bg="#27AE60", fg=COLOR_WHITE,
                  font=("Arial", 11, "bold"), bd=0, cursor="hand2").pack(fill="x", padx=50, pady=20, ipady=10)
        tk.Button(self.root, text="Quay lại đăng nhập", command=self.setup_login_ui, fg="#2980B9", bg=COLOR_WHITE, bd=0,
                  cursor="hand2").pack()

    def handle_login(self):
        email, pwd = self.ent_email.get(), self.ent_pass.get()
        if email in users and users[email]["pass"] == pwd:
            self.current_user = users[email]["name"]
            self.setup_main_dashboard()
        else:
            messagebox.showerror("Lỗi", "Email hoặc mật khẩu không đúng!")

    def handle_register(self):
        name, email, pwd = self.reg_name.get(), self.reg_email.get(), self.reg_pass.get()
        if not name or not email or not pwd:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đủ thông tin!")
            return
        if "@" not in email:
            messagebox.showerror("Lỗi", "Email không hợp lệ!")
            return

        users[email] = {"name": name, "pass": pwd}
        messagebox.showinfo("Thành công", "Đăng ký thành công!")
        self.setup_login_ui()

    # ==========================================
    # PHẦN 2: GIAO DIỆN QUẢN LÝ CHÍNH (Đa Tab)
    # ==========================================
    def setup_main_dashboard(self):
        self.clear_window()
        self.root.geometry("950x650")

        # Header
        header = tk.Frame(self.root, bg=COLOR_BROWN, height=60)
        header.pack(fill="x")
        tk.Label(header, text="☕ PHẦN MỀM QUẢN LÝ CAFE", font=("Arial", 16, "bold"), bg=COLOR_BROWN,
                 fg=COLOR_WHITE).pack(side="left", padx=20, pady=15)

        tk.Button(header, text="Đăng xuất", command=self.setup_login_ui, bg="#c0392b", fg=COLOR_WHITE, bd=0,
                  padx=10).pack(side="right", padx=20, pady=15)
        tk.Label(header, text=f"Xin chào: {self.current_user}", bg=COLOR_BROWN, fg=COLOR_CREAM,
                 font=("Arial", 10, "italic")).pack(side="right", padx=10, pady=20)

        # Tạo hệ thống Tab (Notebook)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook.Tab", font=("Arial", 10, "bold"), padding=[15, 5])

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab 1: Kho Nguyên Liệu
        tab_kho = tk.Frame(notebook, bg=COLOR_WHITE)
        notebook.add(tab_kho, text="1. Tồn Kho Nguyên Liệu")
        self.build_tab_kho(tab_kho)

        # Tab 2: Nhập / Xuất
        tab_nx = tk.Frame(notebook, bg=COLOR_WHITE)
        notebook.add(tab_nx, text="2. Quản Lý Nhập/Xuất")
        self.build_tab_nhap_xuat(tab_nx)

        # Tab 3: Báo Cáo
        tab_bc = tk.Frame(notebook, bg=COLOR_WHITE)
        notebook.add(tab_bc, text="3. Báo Cáo Doanh Thu")
        self.build_tab_bao_cao(tab_bc)

    # --- TAB 1: KHO ---
    def build_tab_kho(self, frame):
        tk.Label(frame, text="DANH SÁCH NGUYÊN LIỆU TRONG KHO", font=("Arial", 12, "bold"), bg=COLOR_WHITE,
                 fg=COLOR_DARK_COFFEE).pack(pady=10)

        cols = ("ten", "sl", "dv", "gia", "tong_gia")
        self.tree_kho = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        self.tree_kho.heading("ten", text="Tên Nguyên Liệu")
        self.tree_kho.heading("sl", text="Tồn Kho")
        self.tree_kho.heading("dv", text="Đơn Vị")
        self.tree_kho.heading("gia", text="Giá Nhập/Đơn vị")
        self.tree_kho.heading("tong_gia", text="Tổng Giá Trị Tồn")

        self.tree_kho.column("sl", width=80, anchor="center")
        self.tree_kho.column("dv", width=80, anchor="center")
        self.tree_kho.pack(fill="both", expand=True, padx=20, pady=10)

        self.load_data_kho()

    def load_data_kho(self):
        for i in self.tree_kho.get_children(): self.tree_kho.delete(i)
        for ten, data in kho_nguyen_lieu.items():
            tong_gt = data["ton_kho"] * data["gia_nhap"]
            self.tree_kho.insert("", "end",
                                 values=(ten, data["ton_kho"], data["dv"], f"{data['gia_nhap']:,}đ", f"{tong_gt:,}đ"))

    # --- TAB 2: NHẬP XUẤT ---
    def build_tab_nhap_xuat(self, frame):
        form_frame = tk.Frame(frame, bg=COLOR_CREAM, bd=1, relief="solid")
        form_frame.pack(fill="x", padx=20, pady=10, ipady=10)

        tk.Label(form_frame, text="THAO TÁC NHẬP / XUẤT", font=("Arial", 11, "bold"), bg=COLOR_CREAM,
                 fg=COLOR_BROWN).grid(row=0, column=0, columnspan=4, pady=10)

        tk.Label(form_frame, text="Tên nguyên liệu:", bg=COLOR_CREAM).grid(row=1, column=0, padx=10, sticky="e")
        cb_nl = ttk.Combobox(form_frame, values=list(kho_nguyen_lieu.keys()), state="readonly", width=25)
        cb_nl.grid(row=1, column=1, padx=10)

        tk.Label(form_frame, text="Hành động:", bg=COLOR_CREAM).grid(row=1, column=2, padx=10, sticky="e")
        cb_hd = ttk.Combobox(form_frame, values=["Nhập thêm vào kho", "Xuất ra pha chế"], state="readonly", width=20)
        cb_hd.grid(row=1, column=3, padx=10)

        tk.Label(form_frame, text="Số lượng:", bg=COLOR_CREAM).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        ent_sl = tk.Entry(form_frame, width=28)
        ent_sl.grid(row=2, column=1, padx=10)

        def xu_ly_nhap_xuat():
            ten = cb_nl.get()
            h_dong = cb_hd.get()
            try:
                sl = int(ent_sl.get())
            except:
                messagebox.showerror("Lỗi", "Số lượng phải là số nguyên!")
                return

            if not ten or not h_dong or sl <= 0:
                messagebox.showwarning("Lỗi", "Vui lòng nhập đúng thông tin!")
                return

            gia = kho_nguyen_lieu[ten]["gia_nhap"]

            if h_dong == "Nhập thêm vào kho":
                kho_nguyen_lieu[ten]["ton_kho"] += sl
                tong_tien = sl * gia
                loai = "NHẬP"
            else:  # Xuất kho
                if sl > kho_nguyen_lieu[ten]["ton_kho"]:
                    messagebox.showerror("Lỗi", "Trong kho không đủ hàng để xuất!")
                    return
                kho_nguyen_lieu[ten]["ton_kho"] -= sl
                tong_tien = 0  # Xuất ra dùng không tính chi phí mua lúc này
                loai = "XUẤT"

            ngay_gio = datetime.now().strftime("%d/%m/%Y %H:%M")
            lich_su_nhap_xuat.insert(0, (ngay_gio, loai, ten, sl, f"{tong_tien:,}đ"))

            messagebox.showinfo("Thành công", f"Đã {loai} {sl} {kho_nguyen_lieu[ten]['dv']} {ten}")
            self.load_data_kho()
            load_lich_su()
            ent_sl.delete(0, tk.END)

        tk.Button(form_frame, text="XÁC NHẬN LƯU", command=xu_ly_nhap_xuat, bg="#2980B9", fg="white",
                  font=("Arial", 10, "bold")).grid(row=2, column=3, pady=10, ipadx=20)

        # Bảng lịch sử
        tk.Label(frame, text="LỊCH SỬ GIAO DỊCH", font=("Arial", 11, "bold"), bg=COLOR_WHITE).pack(pady=5)
        cols = ("ngay", "loai", "ten", "sl", "tien")
        self.tree_ls = ttk.Treeview(frame, columns=cols, show="headings")
        self.tree_ls.heading("ngay", text="Ngày giờ")
        self.tree_ls.heading("loai", text="Loại")
        self.tree_ls.heading("ten", text="Nguyên Liệu")
        self.tree_ls.heading("sl", text="Số lượng")
        self.tree_ls.heading("tien", text="Tổng tiền (Nhập)")
        self.tree_ls.pack(fill="both", expand=True, padx=20, pady=5)

        def load_lich_su():
            for i in self.tree_ls.get_children(): self.tree_ls.delete(i)
            for row in lich_su_nhap_xuat:
                self.tree_ls.insert("", "end", values=row)

    # --- TAB 3: BÁO CÁO DOANH THU ---
    def build_tab_bao_cao(self, frame):
        tk.Label(frame, text="BÁO CÁO DOANH THU & LỢI NHUẬN (6 THÁNG QUA)", font=("Arial", 12, "bold"), bg=COLOR_WHITE,
                 fg=COLOR_BROWN).pack(pady=15)

        cols = ("thang", "dt", "cp", "ln")
        tree_bc = ttk.Treeview(frame, columns=cols, show="headings", height=10)
        tree_bc.heading("thang", text="Tháng/Năm")
        tree_bc.heading("dt", text="Tổng Doanh Thu")
        tree_bc.heading("cp", text="Chi Phí Nguyên Liệu")
        tree_bc.heading("ln", text="Lợi Nhuận Thuần")

        tree_bc.pack(fill="x", padx=20)

        tong_ln = 0
        for bc in doanh_thu_thang:
            tree_bc.insert("", "end", values=(bc["thang"], f"{bc['doanh_thu']:,} VNĐ", f"{bc['chi_phi']:,} VNĐ",
                                              f"{bc['loi_nhuan']:,} VNĐ"))
            tong_ln += bc['loi_nhuan']

        # Khung tổng kết
        tk.Frame(frame, height=2, bg=COLOR_BROWN).pack(fill="x", padx=20, pady=20)
        tk.Label(frame, text=f"TỔNG LỢI NHUẬN ƯỚC TÍNH: {tong_ln:,} VNĐ", font=("Arial", 14, "bold"), fg="#27AE60",
                 bg=COLOR_WHITE).pack()


if __name__ == "__main__":
    app_root = tk.Tk()
    app = CoffeeSystem(app_root)
    app_root.mainloop()