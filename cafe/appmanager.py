import customtkinter as ctk
import os
import sqlite3
import csv
import webbrowser
from tkinter import messagebox
from Page.login import LoginPage
from Page.taotk import TaoTKPage
from Page.quanlitaikhoan import QuanLyTKPage
from Page.suatk import SuaTKPage
from Page.inventory import InventoryPage
from Page.history import HistoryPage
from Page.managermenu import ManagerMenu


class AppManager:
    def __init__(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.root = ctk.CTk()
        self.root.title("Hệ Thống Quản Lý Cafe")

        # ĐÃ THÊM: Đăng ký giao thức tắt ứng dụng an toàn khi bấm nút "X" trên cửa sổ
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.current_role = None
        self.current_user = None
        self.current_page = None

        if not os.path.exists("database"):
            os.makedirs("database")

        conn = sqlite3.connect("database/cafe.db")
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS taikhoan (taikhoan TEXT PRIMARY KEY, matkhau TEXT, gmail TEXT, chucvu TEXT)")
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS nguyenlieu (ten TEXT PRIMARY KEY, loai TEXT, soluong INTEGER, donvi TEXT, gianhap INTEGER, ngaynhap TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS history (user TEXT, role TEXT, time TEXT)")

        cursor.execute("SELECT COUNT(*) FROM taikhoan")
        if cursor.fetchone()[0] == 0:
            csv_path = "database/tk.csv"
            if os.path.exists(csv_path):
                try:
                    with open(csv_path, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        header = next(reader, None)
                        for row in reader:
                            if len(row) >= 4:
                                cursor.execute("INSERT OR IGNORE INTO taikhoan VALUES (?, ?, ?, ?)",
                                               (row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()))
                except Exception as e:
                    print(e)
            else:
                cursor.execute(
                    "INSERT OR IGNORE INTO taikhoan VALUES ('admin', '123456', 'admin@gmail.com', 'Quản lý')")
                cursor.execute(
                    "INSERT OR IGNORE INTO taikhoan VALUES ('staff', 'staff', 'staff@gmail.com', 'Nhân viên')")

        cursor.execute("SELECT COUNT(*) FROM nguyenlieu")
        if cursor.fetchone()[0] == 0:
            csv_path = "database/nguyenlieu.csv"
            if os.path.exists(csv_path):
                try:
                    with open(csv_path, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        header = next(reader, None)
                        for row in reader:
                            if len(row) >= 6:
                                try:
                                    sl = int(str(row[2]).strip())
                                    gia = int(str(row[4]).strip())
                                except:
                                    sl = 0
                                    gia = 0
                                cursor.execute("INSERT OR IGNORE INTO nguyenlieu VALUES (?, ?, ?, ?, ?, ?)",
                                               (row[0].strip(), row[1].strip(), sl, row[3].strip(), gia,
                                                row[5].strip()))
                except Exception as e:
                    print(e)

        cursor.execute("SELECT COUNT(*) FROM history")
        if cursor.fetchone()[0] == 0:
            csv_path = "database/history.csv"
            if os.path.exists(csv_path):
                try:
                    with open(csv_path, "r", encoding="utf-8") as f:
                        reader = csv.reader(f)
                        for row in reader:
                            if len(row) >= 3:
                                cursor.execute("INSERT INTO history VALUES (?, ?, ?)",
                                               (row[0].strip(), row[1].strip(), row[2].strip()))
                except Exception as e:
                    print(e)

        conn.commit()
        conn.close()

        self.show_login_page()

    # ĐÃ THÊM: Hàm xử lý dọn dẹp bộ nhớ và tắt ứng dụng an toàn
    def on_closing(self):
        try:
            # Giải phóng tất cả các luồng đồ họa đang vẽ ngầm của Matplotlib
            import matplotlib.pyplot as plt
            plt.close('all')
        except:
            pass
        self.root.quit()  # Dừng an toàn vòng lặp mainloop của Tkinter trước
        self.root.destroy()  # Hủy hoàn toàn các widget vật lý của cửa sổ

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def open_pdf(self):
        pdf_path = os.path.join("database", "HDSD.pdf")
        if not os.path.exists(pdf_path):
            with open(pdf_path, "w") as f:
                f.write("Huong dan su dung phan mem Quan Ly Kho Cafe")
        webbrowser.open(pdf_path)

    def show_about_window(self):
        about_win = ctk.CTkToplevel(self.root)
        about_win.title("About")
        about_win.geometry("450x250")  # Đã tăng chiều rộng lên 450 để hiển thị thoải mái hơn
        about_win.transient(self.root)
        about_win.grab_set()

        lbl_title = ctk.CTkLabel(about_win, text="PHẦN MỀM QUẢN LÝ CAFE", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=15)

        lbl_desc = ctk.CTkLabel(about_win,
                                text="Phiên bản: 2.0\nTác giả: TLong - TrTú - QNam - Ngọc Đức\nĐơn vị:Khoa Công Nghệ Thông Tin - Trường Đại Học Hạ Long\nNgày phát hành: 03/05/2026",
                                font=("Arial", 12),
                                justify="left")
        lbl_desc.pack(pady=10)

        btn_close = ctk.CTkButton(about_win, text="Đóng", command=about_win.destroy)
        btn_close.pack(pady=15)

    def show_login_page(self):
        self.current_role = None
        self.clear_screen()
        self.root.geometry("1100x650")
        try:
            self.root.update()
            self.root.state('zoomed')
        except:
            pass
        self.current_page = LoginPage(self.root, self)

    def show_manager_menu(self):
        self.clear_screen()
        try:
            self.root.state('zoomed')
        except:
            pass
        self.current_page = ManagerMenu(self.root, self)

    def show_taotk_page(self, from_admin=False):
        self.clear_screen()
        self.root.geometry("1100x650")
        try:
            self.root.update()
            self.root.state('zoomed')
        except:
            pass
        self.current_page = TaoTKPage(self.root, self, from_admin)

    def show_quanlytk_page(self):
        self.clear_screen()
        try:
            self.root.state('zoomed')
        except:
            pass
        self.current_page = QuanLyTKPage(self.root, self)

    def show_inventory_page(self):
        self.clear_screen()
        try:
            self.root.state('zoomed')
        except:
            pass
        self.current_page = InventoryPage(self.root, self)

    def show_history_page(self):
        self.clear_screen()
        try:
            self.root.state('zoomed')
        except:
            pass
        self.current_page = HistoryPage(self.root, self)

    def show_suatk_page(self, username):
        self.clear_screen()
        try:
            self.root.state('normal')
        except:
            pass
        self.root.geometry("450x600")
        self.current_page = SuaTKPage(self.root, self, username)

    def run(self):
        self.root.mainloop()