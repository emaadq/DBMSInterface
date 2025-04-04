"""
Main application entry point for Clothing Store DB Manager
"""

import tkinter as tk
from db_manager import ClothingStoreDBApp

if __name__ == "__main__":
    root = tk.Tk()
    app = ClothingStoreDBApp(root)
    root.mainloop()