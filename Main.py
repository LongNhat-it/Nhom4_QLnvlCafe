import tkinter as tk
from app_manager import CoffeeSystem

def main():
    print("Phần mềm đang khởi chạy")
    root = tk.Tk()
    app = CoffeeSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()