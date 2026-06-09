import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import sqlite3
import csv

class LoginPage:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.view()

    def view(self):
        container = ctk.CTkFrame(self.master, fg_color="#FDFBF7")
        container.pack(fill="both", expand=True)

        card = ctk.CTkFrame(container, fg_color="#FFFFFF", border_width=2, border_color="#E6D5C3", corner_radius=15, width=480, height=520)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        header = ctk.CTkFrame(card, height=75, corner_radius=0, fg_color="#4A3525")
        header.pack(fill="x")
        header.pack_propagate(False)

        lbl_header = ctk.CTkLabel(header, text="☕ ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 22, "bold"), text_color="#FDFBF7")
        lbl_header.pack(pady=20)

        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(pady=35)

        lbl_user = ctk.CTkLabel(f, text="Tên người dùng:", font=("Arial", 14, "bold"), text_color="#4A3525")
        lbl_user.grid(row=0, column=0, pady=12, padx=5, sticky="e")
        self.ent_user = ctk.CTkEntry(f, font=("Arial", 13), width=240, height=35)
        self.ent_user.grid(row=0, column=1, padx=10, pady=12)
        self.ent_user.bind("<Return>", lambda e: self.login())

        lbl_pass = ctk.CTkLabel(f, text="Mật khẩu:", font=("Arial", 14, "bold"), text_color="#4A3525")
        lbl_pass.grid(row=1, column=0, pady=12, padx=5, sticky="e")
        self.ent_pass = ctk.CTkEntry(f, show="*", font=("Arial", 13), width=240, height=35)
        self.ent_pass.grid(row=1, column=1, padx=10, pady=12)
        self.ent_pass.bind("<Return>", lambda e: self.login())

        self.chk_show_pass = ctk.CTkCheckBox(f, text="Hiện mật khẩu", command=self.toggle_password, font=("Arial", 12), text_color="#4A3525", fg_color="#6F4E37", hover_color="#5A3E2B", checkbox_width=18, checkbox_height=20)
        self.chk_show_pass.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.pack(pady=15)

        btn_login = ctk.CTkButton(btn_frame, text="ĐĂNG NHẬP", command=self.login, fg_color="#6F4E37", hover_color="#5A3E2B", text_color="white", font=("Arial", 13, "bold"), width=150, height=40)
        btn_login.pack(side="left", padx=10)

        btn_reg = ctk.CTkButton(btn_frame, text="TẠO TÀI KHOẢN", command=self.app_manager.show_taotk_page, fg_color="#A67B5B", hover_color="#8E6649", text_color="white", font=("Arial", 13, "bold"), width=150, height=40)
        btn_reg.pack(side="left", padx=10)

    def toggle_password(self):
        if self.chk_show_pass.get() == 1:
            self.ent_pass.configure(show="")
        else:
            self.ent_pass.configure(show="*")

    def login(self, event=None):
        user = self.ent_user.get().strip()
        pw = self.ent_pass.get().strip()

        if not user or not pw:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đủ thông tin")
            return
        if len(pw) < 3:
            messagebox.showwarning("Lỗi bảo mật", "Mật khẩu phải có ít nhất 3 ký tự để đảm bảo an toàn!")
            return

        try:
            conn = sqlite3.connect("database/cafe.db")
            cursor = conn.cursor()
            cursor.execute("SELECT chucvu FROM taikhoan WHERE LOWER(taikhoan)=LOWER(?) AND matkhau=?", (user, pw))
            row = cursor.fetchone()

            if row:
                role_detected = row[0]
                self.app_manager.current_user = user
                self.app_manager.current_role = role_detected
                messagebox.showinfo("Thành công", f"Chào mừng {role_detected} {user}")

                now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                cursor.execute("INSERT INTO history VALUES (?, ?, ?)", (user, role_detected, now))
                conn.commit()
                conn.close()

                try:
                    with open("database/history.csv", "a", newline="", encoding="utf-8") as hf:
                        writer = csv.writer(hf)
                        writer.writerow([user, role_detected, now])
                except Exception as ex:
                    print(ex)

                if role_detected == "Quản lý":
                    self.app_manager.show_manager_menu()
                else:
                    self.app_manager.show_inventory_page()
            else:
                conn.close()
                messagebox.showerror("Lỗi", "Tài khoản hoặc mật khẩu không chính xác")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi nạp cơ sở dữ liệu: {e}")