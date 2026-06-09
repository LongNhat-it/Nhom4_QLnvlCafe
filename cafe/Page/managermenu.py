import customtkinter as ctk


class ManagerMenu:
    def __init__(self, master, app_manager):
        self.master = master
        self.app_manager = app_manager
        self.view()

    def view(self):
        header_bg = "#4A3525"
        header = ctk.CTkFrame(self.master, height=85, corner_radius=0, fg_color=header_bg)
        header.pack(fill="x")
        header.pack_propagate(False)

        lbl_header = ctk.CTkLabel(header, text="☕ TRUNG TÂM QUẢN LÍ CAFE", font=("Arial", 24, "bold"), text_color="#FDFBF7")
        lbl_header.pack(side="left", padx=30, pady=25)

        user_info_text = f"Tài khoản: {self.app_manager.current_user or 'Admin'} ({self.app_manager.current_role or 'Quản lý'})"
        lbl_user_info = ctk.CTkLabel(header, text=user_info_text, font=("Arial", 14, "italic"), text_color="#E6D5C3")
        lbl_user_info.pack(side="right", padx=20, pady=30)

        main_container = ctk.CTkFrame(self.master, fg_color="transparent")
        main_container.pack(expand=True, fill="both", padx=40, pady=30)

        main_container.columnconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)

        card_style = {"fg_color": "#FDFBF7", "border_width": 2, "border_color": "#E6D5C3", "corner_radius": 15}

        card_kho = ctk.CTkFrame(main_container, **card_style)
        card_kho.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        lbl_title_kho = ctk.CTkLabel(card_kho, text="📦 QUẢN LÝ KHO & CHI PHÍ", font=("Arial", 20, "bold"), text_color="#4A3525")
        lbl_title_kho.pack(pady=(20, 5))

        lbl_desc_kho = ctk.CTkLabel(card_kho, text="Khu vực kiểm soát nguyên liệu, tính toán tổng hợp chi phí hóa đơn nhập hàng, kết xuất văn bản báo cáo chuyên sâu.", font=("Arial", 14), text_color="#6F4E37", wraplength=380)
        lbl_desc_kho.pack(pady=(5, 10), fill="x", padx=20)

        btn_kho = ctk.CTkButton(card_kho, text="Truy Cập", command=self.app_manager.show_inventory_page, font=("Arial", 14, "bold"), fg_color="#6F4E37", hover_color="#5A3E2B", text_color="white", height=40, width=220)
        btn_kho.pack(side="bottom", pady=15)

        card_user = ctk.CTkFrame(main_container, **card_style)
        card_user.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")

        lbl_title_user = ctk.CTkLabel(card_user, text="👥 QUẢN LÝ TÀI KHOẢN & NHÂN SỰ", font=("Arial", 20, "bold"), text_color="#4A3525")
        lbl_title_user.pack(pady=(20, 5))

        lbl_desc_user = ctk.CTkLabel(card_user, text="Hệ thống quản trị nhân sự của quản lí Cafe. Cho phép thêm mới thành viên, cập nhật thông tin chức vụ, xóa tài khoản và xem nhật ký hoạt động đăng nhập hệ thống thời gian thực.", font=("Arial", 14), text_color="#6F4E37", wraplength=380)
        lbl_desc_user.pack(pady=(5, 10), fill="x", padx=20)

        btn_user = ctk.CTkButton(card_user, text="Truy Cập", command=self.app_manager.show_quanlytk_page, font=("Arial", 14, "bold"), fg_color="#6F4E37", hover_color="#5A3E2B", text_color="white", height=40, width=220)
        btn_user.pack(side="bottom", pady=15)

        card_pdf = ctk.CTkFrame(main_container, **card_style)
        card_pdf.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        lbl_title_pdf = ctk.CTkLabel(card_pdf, text="TÀI LIỆU HƯỚNG DẪN", font=("Arial", 20, "bold"), text_color="#4A3525")
        lbl_title_pdf.pack(pady=(20, 5))

        lbl_desc_pdf = ctk.CTkLabel(card_pdf, text="Xem tài liệu hướng dẫn vận hành chi tiết và quy trình thao tác phần mềm được lưu trữ dưới định dạng PDF. Hỗ trợ tra cứu nhanh chóng quy tắc nhập liệu.", font=("Arial", 14), text_color="#6F4E37", wraplength=380)
        lbl_desc_pdf.pack(pady=(5, 10), fill="x", padx=20)

        btn_pdf = ctk.CTkButton(card_pdf, text="Mở Hướng Dẫn PDF", command=self.app_manager.open_pdf, font=("Arial", 14, "bold"), fg_color="#E0A96D", hover_color="#CC965C", text_color="white", height=40, width=220)
        btn_pdf.pack(side="bottom", pady=15)

        card_about = ctk.CTkFrame(main_container, **card_style)
        card_about.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")

        lbl_title_about = ctk.CTkLabel(card_about, text="GIỚI THIỆU PHẦN MỀM", font=("Arial", 20, "bold"), text_color="#4A3525")
        lbl_title_about.pack(pady=(20, 5))

        lbl_desc_about = ctk.CTkLabel(card_about, text="Thông tin phiên bản, nhóm tác giả phát triển phần mềm và công nghệ áp dụng. Hệ thống sử dụng cơ sở dữ liệu SQLite đồng bộ hai chiều cùng giao diện CustomTkinter.", font=("Arial", 14), text_color="#6F4E37", wraplength=380)
        lbl_desc_about.pack(pady=(5, 10), fill="x", padx=20)

        btn_about = ctk.CTkButton(card_about, text="Xem Chi Tiết", command=self.app_manager.show_about_window, font=("Arial", 14, "bold"), fg_color="#5C8D89", hover_color="#4A726E", text_color="white", height=40, width=220)
        btn_about.pack(side="bottom", pady=15)

        footer_frame = ctk.CTkFrame(self.master, height=65, corner_radius=0, fg_color="#FDFBF7")
        footer_frame.pack(side="bottom", fill="x")

        btn_logout = ctk.CTkButton(footer_frame, text="ĐĂNG XUẤT", command=self.app_manager.show_login_page, font=("Arial", 12, "bold"), fg_color="#D9534F", hover_color="#C9302C", text_color="white", width=160, height=35)
        btn_logout.pack(side="bottom", padx=40, pady=12)