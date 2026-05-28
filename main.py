"""
Smart Inventory Management System
Entry point — initializes the database and launches the GUI.
"""

from database import init_db
from ui.app import InventoryApp

if __name__ == "__main__":
    init_db()
    app = InventoryApp()
    app.mainloop()
