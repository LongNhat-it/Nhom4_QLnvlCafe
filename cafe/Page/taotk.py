import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import csv

class TaoTKPage:
    def __init__(self, master, app_manager, from_admin=False):
        self.master = master
        self.app_manager = app_manager
        self.from_admin = from_admin
        self.view()

    def view(self):
        container = ctk.CTkFrame(self.master, fg_color="#FDFBF7")
        container.pack(fill="both", expand=True)

        card = ctk.CTkFrame(container, fg_color="#FFFFFF", border_width=2, border_color="#E6D5C3", corner_radius=15, width=480, height=540)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        header = ctk.CTkFrame(card, height=75, corner_radius=0, fg_color="#4A3525")
        header.pack(fill="x")
        header.pack_propagate(False)

        lbl_header = ctk.CTkLabel(header, text="☕ ĐĂNG KÝ THÀNH VIÊN MỚI", font=("Arial", 20, "bold"), text_color="white")
        lbl_header.pack(pady=20)

        frame = ctk.CTkFrame(card, fg_color="transparent")
        frame.pack(pady=25, padx=20)

        font_lbl = ("Arial", 12, "bold")
        font_input = ("Arial", 13)

        lbl_user = ctk.CTkLabel(frame, text="Tên người dùng:", font=font_lbl, text_color="#4A3525")
        lbl_user.grid(row=0, column=0, pady=12, sticky="e")
        self.entry_username = ctk.CTkEntry(frame, font=font_input, width=220, height=35)
        self.entry_username.grid(row=0, column=1, padx=10, pady=12)

        lbl_gmail = ctk.CTkLabel(frame, text="  Gmail:", font=font_lbl, text_color="#4A3525")
        lbl_gmail.grid(row=1, column=0, pady=12, sticky="e")
        self.entry_gmail = ctk.CTkEntry(frame, font=font_input, width=220, height=35)
        self.entry_gmail.grid(row=1, column=1, padx=10, pady=12)

        lbl_pass = ctk.CTkLabel(frame, text="Mật khẩu:", font=font_lbl, text_color="#4A3525")
        lbl_pass.grid(row=2, column=0, pady=12, sticky="e")
        self.entry_password = ctk.CTkEntry(frame, show="*", font=font_input, width=220, height=35)
        self.entry_password.grid(row=2, column=1, padx=10, pady=12)

        lbl_confirm = ctk.CTkLabel(frame, text="Xác nhận mã:", font=font_lbl, text_color="#4A3525")
        lbl_confirm.grid(row=3, column=0, pady=12, sticky="e")
        self.entry_confirm = ctk.CTkEntry(frame, show="*", font=font_input, width=220, height=35)
        self.entry_confirm.grid(row=3, column=1, padx=10, pady=12)

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=20)

        btn_reg = ctk.CTkButton(btn_frame, text="ĐĂNG KÝ", command=self.register, fg_color="#6F4E37", hover_color="#5A3E2B", text_color="white", font=("Arial", 13, "bold"), width=130, height=40)
        btn_reg.pack(side="left", padx=10)

        btn_back_cmd = lambda: self.app_manager.show_quanlytk_page() if self.from_admin else self.app_manager.show_login_page()
        btn_cancel = ctk.CTkButton(btn_frame, text="HỦY BỎ", command=btn_back_cmd, fg_color="#A67B5B", hover_color="#8E6649", text_color="white", font=("Arial", 13, "bold"), width=130, height=40)
        btn_cancel.pack(side="left", padx=10)

    def register(self):
        user = self.entry_username.get().strip()
        gmail = self.entry_gmail.get().strip()
        pw = self.entry_password.get().strip()
        confirm = self.entry_confirm.get().strip()

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
            cursor.execute("SELECT taikhoan FROM taikhoan WHERE LOWER(taikhoan)=LOWER(?)", (user,))
            if cursor.fetchone():
                conn.close()
                messagebox.showerror("Lỗi", "Tên tài khoản đã tồn tại!")
                return

            cursor.execute("INSERT INTO taikhoan VALUES (?, ?, ?, 'Nhân viên')", (user, pw, gmail))
            conn.commit()
            conn.close()

            try:
                with open("database/tk.csv", "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([user, pw, gmail, 'Nhân viên'])
            except Exception as ex:
                print(ex)

            messagebox.showinfo("Thành công", f"Đã tạo tài khoản cho {user}")
            if self.from_admin:
                self.app_manager.show_quanlytk_page()
            else:
                self.app_manager.show_login_page()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu tài khoản: {e}")