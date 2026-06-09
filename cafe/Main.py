import sys
import io
import os
from appmanager import AppManager

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("--- Ứng dụng Quản lý Kho Cafe đang khởi động ---")
    app = AppManager()
    app.run()

if __name__ == "__main__":
    main()