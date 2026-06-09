import customtkinter as ctk
from tkinter import messagebox, ttk
import sqlite3
import csv


class QuanLyTKPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.apply_styles()
        self.view()
        self.load_accounts()

    def apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", background="#6F4E37", foreground="white", font=("Arial", 13, "bold"),
                        borderwidth=0)
        style.map("Treeview.Heading", background=[('active', '#5A3E2B')])
        style.configure("Treeview", background="#FDFBF7", foreground="#4A3525", fieldbackground="#FDFBF7", rowheight=38,
                        font=("Arial", 12), borderwidth=0)
        style.map("Treeview", background=[("selected", "#E6D5C3")], foreground=[("selected", "#4A3525")])

    def view(self):
        header_frame = ctk.CTkFrame(self.master, height=75, corner_radius=0, fg_color="#4A3525")
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        lbl_header = ctk.CTkLabel(header_frame, text="☕ HỆ THỐNG TÀI KHOẢN NHÂN VIÊN", font=("Arial", 22, "bold"),
                                  text_color="#FDFBF7")
        lbl_header.pack(side="left", padx=25, pady=20)

        btn_menu = ctk.CTkButton(header_frame, text="🔙 VỀ MENU", command=lambda: self.app_manager.show_manager_menu(),
                                 fg_color="#D9534F", hover_color="#C9302C", text_color="white",
                                 font=("Arial", 12, "bold"), width=130, height=35)
        btn_menu.pack(side="right", padx=25, pady=18)

        tool_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        tool_frame.pack(pady=20, fill="x", padx=25)

        btn_style = {"font": ("Arial", 12, "bold"), "text_color": "white", "height": 35}

        btn_refresh = ctk.CTkButton(tool_frame, text="🔄 Làm mới", command=self.load_accounts, fg_color="#A67B5B",
                                    hover_color="#8E6649", width=110, **btn_style)
        btn_refresh.pack(side="left", padx=4)

        btn_add = ctk.CTkButton(tool_frame, text="➕ Thêm tài khoản", command=lambda: self.open_account_form("THÊM TÀI KHOẢN MỚI"), fg_color="#5C8D89",
                                hover_color="#4A726E", width=150, **btn_style)
        btn_add.pack(side="left", padx=4)

        btn_edit = ctk.CTkButton(tool_frame, text="✏️ Sửa", command=self.edit_account, fg_color="#E0A96D",
                                 hover_color="#CC965C", width=110, **btn_style)
        btn_edit.pack(side="left", padx=4)

        btn_del = ctk.CTkButton(tool_frame, text="🗑️ Xoá", command=self.delete_account, fg_color="#A64B2A",
                                hover_color="#8E3E22", width=110, **btn_style)
        btn_del.pack(side="left", padx=4)

        btn_history = ctk.CTkButton(tool_frame, text="📜 Lịch sử", command=self.app_manager.show_history_page,
                                    fg_color="#6F4E37", hover_color="#5A3E2B", width=110, **btn_style)
        btn_history.pack(side="right", padx=4)

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda n, i, m: self.load_accounts(self.search_var.get().strip().lower()))

        self.ent_search = ctk.CTkEntry(tool_frame, font=("Arial", 14), width=450, height=35,
                                       textvariable=self.search_var)
        self.ent_search.pack(side="right", padx=8)

        lbl_search = ctk.CTkLabel(tool_frame, text="Tìm kiếm:", font=("Arial", 13, "italic"), text_color="#6F4E37")
        lbl_search.pack(side="right", padx=2)

        table_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        table_frame.pack(expand=True, fill="both", padx=25, pady=5)

        columns = ("stt", "user", "pass", "gmail", "role")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        headers = {"stt": "STT", "user": "👤 Tên đăng nhập", "pass": "🔑 Mật khẩu bảo mật", "gmail": "✉️ Email liên hệ",
                   "role": "🎖️ Chức vụ quản trị"}

        for col in columns:
            self.tree.heading(col, text=headers[col])
            col_width = 80 if col == "stt" else 200
            self.tree.column(col, width=col_width, anchor="center")

        self.tree.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")

    def load_accounts(self, search_query=""):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = sqlite3.connect("database/cafe.db")
            cursor = conn.cursor()
            if search_query:
                cursor.execute(
                    "SELECT taikhoan, matkhau, gmail, chucvu FROM taikhoan WHERE taikhoan LIKE ? OR gmail LIKE ?",
                    (f"%{search_query}%", f"%{search_query}%"))
            else:
                cursor.execute("SELECT taikhoan, matkhau, gmail, chucvu FROM taikhoan")
            rows = cursor.fetchall()
            conn.close()

            for idx, row in enumerate(rows, 1):
                user, pw, gmail, role = row
                display_pass = "•" * len(pw)
                self.tree.insert("", "end", values=(idx, user, display_pass, gmail, role))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu tài khoản: {e}")

    def delete_account(self):
        selected = self.tree.selection()
        if not selected:
            return
        user_to_del = self.tree.item(selected[0])['values'][1]

        if messagebox.askyesno("Xác nhận",
                               f"Bạn có chắc chắn muốn xóa tài khoản nhân viên {user_to_del} ra khỏi hệ thống?"):
            try:
                conn = sqlite3.connect("database/cafe.db")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM taikhoan WHERE taikhoan=?", (user_to_del,))
                conn.commit()

                cursor.execute("SELECT taikhoan, matkhau, gmail, chucvu FROM taikhoan")
                all_accounts = cursor.fetchall()
                conn.close()

                try:
                    with open("database/tk.csv", "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["taikhoan", "matkhau", "gmail", "chucvu"])
                        for acc in all_accounts:
                            writer.writerow([acc[0], acc[1], acc[2], acc[3]])
                except Exception as ex:
                    print(ex)

                self.load_accounts()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa tài khoản: {e}")

    def edit_account(self):
        selected = self.tree.selection()
        if not selected:
            return
        user = self.tree.item(selected[0])['values'][1]
        self.open_account_form("CẬP NHẬT TÀI KHOẢN", user)

    def open_account_form(self, title, edit_username=None):
        win = ctk.CTkToplevel(self.master)
        win.title(title)
        w, h = 480, 520

        self.master.update_idletasks()
        parent_x = self.master.winfo_rootx()
        parent_y = self.master.winfo_rooty()
        parent_w = self.master.winfo_width()
        parent_h = self.master.winfo_height()
        x = parent_x + (parent_w // 2) - (w // 2)
        y = parent_y + (parent_h // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.grab_set()

        lbl_title = ctk.CTkLabel(win, text=title, font=("Arial", 18, "bold"), text_color="#4A3525")
        lbl_title.pack(pady=20)

        form_frame = ctk.CTkFrame(win, fg_color="transparent")
        form_frame.pack(anchor="center", pady=10)

        font_lbl = ("Arial", 12, "bold")
        font_input = ("Arial", 13)

        lbl_user = ctk.CTkLabel(form_frame, text="Tên tài khoản:", font=font_lbl, text_color="#4A3525")
        lbl_user.grid(row=0, column=0, sticky="w", pady=8)
        ent_user = ctk.CTkEntry(form_frame, font=font_input, width=220, height=35)
        ent_user.grid(row=0, column=1, pady=8, padx=10)

        lbl_gmail = ctk.CTkLabel(form_frame, text="Gmail:", font=font_lbl, text_color="#4A3525")
        lbl_gmail.grid(row=1, column=0, sticky="w", pady=8)
        ent_gmail = ctk.CTkEntry(form_frame, font=font_input, width=220, height=35)
        ent_gmail.grid(row=1, column=1, padx=10, pady=8)

        lbl_role = ctk.CTkLabel(form_frame, text="Chức vụ quyền:", font=font_lbl, text_color="#4A3525")
        lbl_role.grid(row=2, column=0, sticky="w", pady=8)
        cb_role = ctk.CTkComboBox(form_frame, values=["Quản lý", "Nhân viên"], font=font_input, width=220, height=35)
        cb_role.grid(row=2, column=1, pady=8, padx=10)
        cb_role.set("Nhân viên")

        lbl_pass = ctk.CTkLabel(form_frame, text="Mật khẩu:", font=font_lbl, text_color="#4A3525")
        lbl_pass.grid(row=3, column=0, sticky="w", pady=8)
        ent_pass = ctk.CTkEntry(form_frame, show="*", font=font_input, width=220, height=35)
        ent_pass.grid(row=3, column=1, pady=8, padx=10)

        lbl_confirm = ctk.CTkLabel(form_frame, text="Xác nhận mã:", font=font_lbl, text_color="#4A3525")
        lbl_confirm.grid(row=4, column=0, sticky="w", pady=8)
        ent_confirm = ctk.CTkEntry(form_frame, show="*", font=font_input, width=220, height=35)
        ent_confirm.grid(row=4, column=1, pady=8, padx=10)

        if edit_username:
            try:
                conn = sqlite3.connect("database/cafe.db")
                cursor = conn.cursor()
                cursor.execute("SELECT taikhoan, matkhau, gmail, chucvu FROM taikhoan WHERE taikhoan=?",
                               (edit_username,))
                row = cursor.fetchone()
                conn.close()
                if row:
                    ent_user.insert(0, row[0])
                    ent_user.configure(state="readonly")
                    ent_pass.insert(0, row[1])
                    ent_confirm.insert(0, row[1])
                    ent_gmail.insert(0, row[2])
                    cb_role.set(row[3])
            except Exception as e:
                print(e)

        def save():
            user = ent_user.get().strip()
            gmail = ent_gmail.get().strip()
            role = cb_role.get()
            pw = ent_pass.get().strip()
            confirm = ent_confirm.get().strip()

            if not user or not pw or not gmail:
                messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin")
                return

            if len(pw) < 3:
                messagebox.showwarning("Lỗi bảo mật", "Mật khẩu phải có ít nhất 3 ký tự để đảm bảo an toàn!")
                return

            if pw != confirm:
                messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
                return

            try:
                conn = sqlite3.connect("database/cafe.db")
                cursor = conn.cursor()

                if edit_username:
                    cursor.execute("UPDATE taikhoan SET matkhau=?, gmail=?, chucvu=? WHERE taikhoan=?",
                                   (pw, gmail, role, edit_username))
                else:
                    cursor.execute("SELECT taikhoan FROM taikhoan WHERE LOWER(taikhoan)=LOWER(?)", (user,))
                    if cursor.fetchone():
                        conn.close()
                        messagebox.showerror("Lỗi", "Tên tài khoản đã tồn tại!")
                        return
                    cursor.execute("INSERT INTO taikhoan VALUES (?, ?, ?, ?)", (user, pw, gmail, role))

                conn.commit()

                cursor.execute("SELECT taikhoan, matkhau, gmail, chucvu FROM taikhoan")
                all_accounts = cursor.fetchall()
                conn.close()

                try:
                    with open("database/tk.csv", "w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(["taikhoan", "matkhau", "gmail", "chucvu"])
                        for acc in all_accounts:
                            writer.writerow([acc[0], acc[1], acc[2], acc[3]])
                except Exception as ex:
                    print(ex)

                self.master.focus_set()
                self.load_accounts()
                win.after(10, win.destroy)
                messagebox.showinfo("Thành công", "Đã tạo tài khoản thành công")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu tài khoản: {e}")

        btn_confirm = ctk.CTkButton(win, text="XÁC NHẬN", fg_color="#5D4037", hover_color="#7B5E4E", text_color="white",
                                    font=("Arial", 13, "bold"), command=save, width=180, height=42)
        btn_confirm.pack(pady=25)