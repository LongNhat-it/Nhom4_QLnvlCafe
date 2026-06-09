import customtkinter as ctk
from tkinter import ttk
import sqlite3

class HistoryPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.apply_styles()
        self.view()
        self.load_history()

    def apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("History.Treeview.Heading", background="#6F4E37", foreground="white", font=("Arial", 13, "bold"), borderwidth=0)
        style.configure("History.Treeview", background="#FDFBF7", foreground="#4A3525", fieldbackground="#FDFBF7", rowheight=38, font=("Arial", 12), borderwidth=0)
        style.map("History.Treeview", background=[("selected", "#E6D5C3")], foreground=[("selected", "#4A3525")])

    def view(self):
        header_frame = ctk.CTkFrame(self.master, height=75, corner_radius=0, fg_color="#4A3525")
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        lbl_header = ctk.CTkLabel(header_frame, text="📜 LỊCH SỬ ĐĂNG NHẬP", font=("Arial", 22, "bold"), text_color="#FDFBF7")
        lbl_header.pack(side="left", padx=20, pady=15)

        tool_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        tool_frame.pack(pady=15, fill="x", padx=20)

        btn_back = ctk.CTkButton(tool_frame, text="🔙 Quay lại", command=self.app_manager.show_quanlytk_page, fg_color="#A67B5B", hover_color="#8E6649", text_color="white", font=("Arial", 12, "bold"), width=130, height=35)
        btn_back.pack(side="left")

        table_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        table_frame.pack(expand=True, fill="both", padx=20, pady=5)

        columns = ("stt", "user", "role", "time")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="History.Treeview")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.heading("stt", text="STT")
        self.tree.heading("user", text="👤 Tài khoản tác vụ")
        self.tree.heading("role", text="🎖️ Chức vụ quản trị")
        self.tree.heading("time", text="🕒 Thời điểm đăng nhập")

        self.tree.column("stt", width=70, anchor="center")
        self.tree.column("user", width=200, anchor="center")
        self.tree.column("role", width=170, anchor="center")
        self.tree.column("time", width=240, anchor="center")

        self.tree.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")

    def load_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            conn = sqlite3.connect("database/cafe.db")
            cursor = conn.cursor()
            cursor.execute("SELECT user, role, time FROM history")
            rows = cursor.fetchall()
            conn.close()

            for idx, row in enumerate(reversed(rows), 1):
                self.tree.insert("", "end", values=(idx, row[0], row[1], row[2]))
        except Exception as e:
            print(e)