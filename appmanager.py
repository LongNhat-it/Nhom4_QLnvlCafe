import tkinter as tk
import os
from Page.login import LoginPage
from Page.taotk import TaoTKPage
from Page.quanlitaikhoan import QuanLyTKPage
from Page.suatk import SuaTKPage
from Page.inventory import InventoryPage
from Page.history import HistoryPage

class AppManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Hệ Thống Quản Lý Cafe")
        self.current_role = None
        self.current_user = None

        if not os.path.exists("database"):
            os.makedirs("database")

        self.show_login_page()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login_page(self):
        self.current_role = None
        self.clear_screen()
        self.root.geometry("400x450")
        self.current_page = LoginPage(self.root, self)

    def show_taotk_page(self):
        self.clear_screen()
        self.root.geometry("450x550")
        self.current_page = TaoTKPage(self.root, self)

    def show_quanlytk_page(self):
        if self.current_role != "Quản lý": return
        self.clear_screen()
        self.root.geometry("900x550")
        self.current_page = QuanLyTKPage(self.root, self)

    def show_inventory_page(self):
        self.clear_screen()
        self.root.geometry("1100x800")
        self.current_page = InventoryPage(self.root, self)

    def show_history_page(self):
        self.clear_screen()
        self.root.geometry("800x600")
        self.current_page = HistoryPage(self.root, self)

    def show_suatk_page(self, username, password):
        self.clear_screen()
        self.root.geometry("450x600")
        self.current_page = SuaTKPage(self.root, self, username, password)

    def run(self):
        self.root.mainloop()