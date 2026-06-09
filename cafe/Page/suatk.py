import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import csv


class SuaTKPage:
    def __init__(self, master, app_manager, username=""):
        self.master = master
        self.app_manager = app_manager
        self.old_user = str(username).strip()
        self.view()
        self.load_current_data()

    def view(self):
        header = ctk.CTkFrame(self.master, height=75, corner_radius=0, fg_color="#4A3525")
        header.pack(fill="x")
        header.pack_propagate(False)

        lbl_header = ctk.CTkLabel(header, text="☕ CHỈNH SỬA TÀI KHOẢN", font=("Arial", 22, "bold"), text_color="white")
        lbl_header.pack(pady=20)

        frame = ctk.CTkFrame(self.master, fg_color="transparent")
        frame.pack(pady=20, padx=20)

        lbl_info = ctk.CTkLabel(frame, text=f"Đang tiến hành chỉnh sửa: {self.old_user}", text_color="#6F4E37",
                                font=("Arial", 14, "bold"))
        lbl_info.grid(row=0, columnspan=2, pady=12)

        font_lbl = ("Arial", 12, "bold")
        font_input = ("Arial", 13)

        lbl_user = ctk.CTkLabel(frame, text="Tên tài khoản:", font=font_lbl, text_color="#4A3525")
        lbl_user.grid(row=1, column=0, pady=10, sticky="e")
        self.ent_user = ctk.CTkEntry(frame, font=font_input, width=220, height=35)
        self.ent_user.grid(row=1, column=1, padx=10, pady=10)

        lbl_gmail = ctk.CTkLabel(frame, text="Gmail:", font=font_lbl, text_color="#4A3525")
        lbl_gmail.grid(row=2, column=0, pady=10, sticky="e")
        self.ent_gmail = ctk.CTkEntry(frame, font=font_input, width=220, height=35)
        self.ent_gmail.grid(row=2, column=1, padx=10, pady=10)

        lbl_role = ctk.CTkLabel(frame, text="Chức vụ quyền:", font=font_lbl, text_color="#4A3525")
        lbl_role.grid(row=3, column=0, pady=10, sticky="e")
        self.cb_role = ctk.CTkComboBox(frame, values=["Quản lý", "Nhân viên"], font=font_input, width=220, height=35)
        self.cb_role.grid(row=3, column=1, padx=10, pady=10)

        lbl_pass = ctk.CTkLabel(frame, text="Mật khẩu mới:", font=font_lbl, text_color="#4A3525")
        lbl_pass.grid(row=4, column=0, pady=10, sticky="e")
        self.ent_pass = ctk.CTkEntry(frame, show="*", font=font_input, width=220, height=35)
        self.ent_pass.grid(row=4, column=1, padx=10, pady=10)

        lbl_confirm = ctk.CTkLabel(frame, text="Xác nhận mã:", font=font_lbl, text_color="#4A3525")
        lbl_confirm.grid(row=5, column=0, pady=10, sticky="e")
        self.ent_confirm = ctk.CTkEntry(frame, show="*", font=font_input, width=220, height=35)
        self.ent_confirm.grid(row=5, column=1, padx=10, pady=10)

        btn_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        btn_frame.pack(pady=20)

        btn_save = ctk.CTkButton(btn_frame, text="CẬP NHẬT", command=self.save_changes, fg_color="#6F4E37",
                                 hover_color="#5A3E2B", text_color="white", font=("Arial", 13, "bold"), width=130,
                                 height=40)
        btn_save.pack(side="left", padx=10)

        btn_back = ctk.CTkButton(btn_frame, text="QUAY LẠI", command=self.app_manager.show_quanlytk_page,
                                 fg_color="#A67B5B", hover_color="#8E6649", text_color="white",
                                 font=("Arial", 13, "bold"), width=130, height=40)
        btn_back.pack(side="left", padx=10)

    def load_current_data(self):
        try:
            conn = sqlite3.connect("database/cafe.db")
            cursor = conn.cursor()
            cursor.execute("SELECT taikhoan, matkhau, gmail, chucvu FROM taikhoan WHERE taikhoan=?", (self.old_user,))
            row = cursor.fetchone()
            if row:
                self.ent_user.insert(0, row[0])
                self.ent_pass.insert(0, row[1])
                self.ent_confirm.insert(0, row[1])
                self.ent_gmail.insert(0, row[2])
                self.cb_role.set(row[3])
            conn.close()
        except Exception as e:
            print(e)

    def save_changes(self):
        new_user = self.ent_user.get().strip()
        new_gmail = self.ent_gmail.get().strip()
        new_role = self.cb_role.get()
        new_pass = self.ent_pass.get().strip()
        confirm_pass = self.ent_confirm.get().strip()

        if not new_user or not new_pass or not new_gmail:
            messagebox.showwarning("Lỗi", "Vui lòng nhập đầy đủ thông tin")
            return

        if len(new_pass) < 3:
            messagebox.showwarning("Lỗi bảo mật", "Mật khẩu phải có ít nhất 3 ký tự để đảm bảo an toàn!")
            return

        if new_pass != confirm_pass:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        try:
            conn = sqlite3.connect("database/cafe.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE taikhoan SET taikhoan=?, matkhau=?, gmail=?, chucvu=? WHERE taikhoan=?",
                           (new_user, new_pass, new_gmail, new_role, self.old_user))
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

            messagebox.showinfo("Thành công", "Đã cập nhật tài khoản thành công")
            self.app_manager.show_quanlytk_page()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu thay đổi: {e}")