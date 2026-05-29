import tkinter as tk
import os
from Page.login import LoginPage
from Page.taotk import TaoTKPage
from Page.quanlitaikhoan import QuanLyTKPage
from Page.suatk import SuaTKPage
from Page.inventory import InventoryPage
from Page.history import HistoryPage
from Page.managermenu import ManagerMenu


class AppManager:
    """🎮 BỘ ĐIỀU PHỐI TRUNG TÂM (CONTROLLER / ROUTER) CỦA ỨNG DỤNG"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hệ Thống Quản Lý Cafe")

        """📝 Lưu trữ trạng thái phiên làm việc toàn cục"""
        self.current_role = None  # Phục vụ phân quyền
        self.current_user = None  # Lưu tên người dùng đang đăng nhập
        self.current_page = None  # Giữ thực thể (instance) của trang đang hiển thị hiện tại

        """Khởi tạo thư mục chứa dữ liệu nếu chạy ứng dụng lần đầu tiên"""
        if not os.path.exists("database"):
            os.makedirs("database")

        """Khởi động ứng dụng bằng màn hình Đăng nhập"""
        self.show_login_page()

    def clear_screen(self):
        """🧹 THUẬT TOÁN DỌN BÀN CHUYỂN TRANG (RESET VIEW)
        Quét và hủy toàn bộ các Widget (Button, Label, Frame...) của trang cũ
        đang bám trên cửa sổ root để chuẩn bị vẽ giao diện của trang mới.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_page(self):
        """🔑 ĐIỀU HƯỚNG: MÀN HÌNH ĐĂNG NHẬP"""
        self.current_role = None
        self.clear_screen()
        self.root.geometry("400x450")
        self.current_page = LoginPage(self.root, self)

    def show_manager_menu(self):
        """☕ ĐIỀU HƯỚNG: MENU TỔNG CHO QUẢN LÝ (DASHBOARD)"""
        self.clear_screen()
        self.root.geometry("450x450")
        self.current_page = ManagerMenu(self.root, self)

    def show_taotk_page(self, from_admin=False):
        """➕ ĐIỀU HƯỚNG: FORM TẠO TÀI KHOẢN MỚI"""
        self.clear_screen()
        self.root.geometry("450x550")
        self.current_page = TaoTKPage(self.root, self, from_admin)

    def show_quanlytk_page(self):
        """👥 ĐIỀU HƯỚNG: DANH SÁCH QUẢN LÝ NHÂN SỰ & TÀI KHOẢN"""
        self.clear_screen()
        self.root.geometry("900x550")
        self.current_page = QuanLyTKPage(self.root, self)

    def show_inventory_page(self):
        """📦 ĐIỀU HƯỚNG: PHÂN HỆ QUẢN LÝ KHO NGUYÊN LIỆU (Ứng dụng CRUD, Đồ thị, Báo cáo)"""
        self.clear_screen()
        self.root.geometry("1100x650")
        self.current_page = InventoryPage(self.root, self)

    def show_history_page(self):
        """📜 ĐIỀU HƯỚNG: TRANG XEM NHẬT KÝ ĐĂNG NHẬP HỆ THỐNG"""
        self.clear_screen()
        self.root.geometry("800x600")
        self.current_page = HistoryPage(self.root, self)

    def show_suatk_page(self, username):
        """✏️ ĐIỀU HƯỚNG: FORM SỬA TÀI KHOẢN KÈM THAM SỐ ĐỊNH DANH"""
        self.clear_screen()
        self.root.geometry("450x600")
        self.current_page = SuaTKPage(self.root, self, username)

    def run(self):
        """🚀 KÍCH HOẠT VÒNG LẶP SỰ KIỆN ĐỂ CHẠY ỨNG DỤNG"""
        self.root.mainloop()