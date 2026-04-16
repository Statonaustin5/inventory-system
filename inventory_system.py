import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from sklearn.linear_model import LinearRegression
# ----------------------
# DATABASE SETUP
# ----------------------
conn = sqlite3.connect("inventory.db")
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    price REAL,
    stock INTEGER
)
''')
conn.commit()

# ----------------------
# CORE FUNCTIONS
# ----------------------
def add_product(name, category, price, stock):
    c.execute("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
              (name, category, price, stock))
    conn.commit()
    messagebox.showinfo("Success", f"Added {name} to inventory.")

def update_product(pid, name, category, price, stock):
    c.execute("UPDATE products SET name=?, category=?, price=?, stock=? WHERE id=?",
              (name, category, price, stock, pid))
    conn.commit()
    messagebox.showinfo("Success", f"Updated product ID {pid}.")

def delete_product(pid):
    c.execute("DELETE FROM products WHERE id=?", (pid,))
    conn.commit()
    messagebox.showinfo("Success", f"Deleted product ID {pid}.")

def get_all_products():
    c.execute("SELECT * FROM products")
    return c.fetchall()

# ----------------------
# FORECASTING / REORDER ALERT
# ----------------------
def forecast_stock(pid):
    # Simulated historical sales (you can later store real sales)
    sales_data = np.array([5, 7, 6, 8, 7, 9, 6])  # past 7 days
    
    # Create time variable (days)
    X = np.array(range(len(sales_data))).reshape(-1, 1)
    y = sales_data

    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict next day's demand
    next_day = np.array([[len(sales_data)]])
    forecast = model.predict(next_day)[0]

    # Get current stock
    c.execute("SELECT stock, name FROM products WHERE id=?", (pid,))
    product = c.fetchone()
    stock_left, name = product

    # Suggested reorder (buffer = 3 days of demand)
    suggested_order = max(0, int(forecast * 3 - stock_left))

    # Show results
    messagebox.showinfo(
        "Forecast",
        f"Predicted daily demand for {name}: {forecast:.2f}\n"
        f"Suggested reorder: {suggested_order} units"
    )

    if suggested_order > 0:
        messagebox.showwarning(
            "Reorder Alert",
            f"Stock low for {name}! Consider ordering {suggested_order} units."
        )

# ----------------------
# CSV IMPORT / EXPORT
# ----------------------
def export_inventory():
    products = get_all_products()
    df = pd.DataFrame(products, columns=["ID", "Name", "Category", "Price", "Stock"])
    file_path = filedialog.asksaveasfilename(defaultextension=".csv")
    if file_path:
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Export", f"Inventory exported to {file_path}")

def import_inventory():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files","*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        for _, row in df.iterrows():
            c.execute("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
                      (row['Name'], row['Category'], row['Price'], row['Stock']))
        conn.commit()
        refresh_tree()
        messagebox.showinfo("Import", "Inventory imported successfully.")

# ----------------------
# DASHBOARD / PLOTS
# ----------------------
def show_dashboard():
    products = get_all_products()
    if not products:
        messagebox.showwarning("Dashboard", "No products to display.")
        return
    df = pd.DataFrame(products, columns=["ID", "Name", "Category", "Price", "Stock"])
    fig, ax = plt.subplots(figsize=(6,4))
    df.plot(kind="bar", x="Name", y="Stock", ax=ax, color="skyblue")
    ax.set_title("Current Stock Levels")
    ax.set_ylabel("Units in Stock")
    ax.set_xlabel("Product Name")

    dashboard_window = tk.Toplevel(root)
    dashboard_window.title("Inventory Dashboard")
    dashboard_window.geometry("+200+100")
    canvas = FigureCanvasTkAgg(fig, master=dashboard_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

# ----------------------
# SALE AND ORDER FUNCTIONS
# ----------------------
def record_sale_product():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a product to sell.")
        return
    pid = tree.item(selected)['values'][0]
    qty = simpledialog.askinteger("Record Sale", "Enter quantity sold:", minvalue=1)
    if qty is None:
        return
    c.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, pid))
    conn.commit()
    refresh_tree()
    forecast_stock(pid)

def order_product():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a product to order.")
        return
    pid = tree.item(selected)['values'][0]
    qty = simpledialog.askinteger("Order Product", "Enter quantity to order:", minvalue=1)
    if qty is None:
        return
    c.execute("UPDATE products SET stock = stock + ? WHERE id = ?", (qty, pid))
    conn.commit()
    refresh_tree()
    messagebox.showinfo("Order Placed", f"Ordered {qty} units for product ID {pid}.")

# ----------------------
# SAFE BUTTON FUNCTIONS
# ----------------------
def add_selected_product():
    add_product(name_var.get(), cat_var.get(), price_var.get(), stock_var.get())
    refresh_tree()

def update_selected_product():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a product to update.")
        return
    pid = tree.item(selected)['values'][0]
    update_product(pid, name_var.get(), cat_var.get(), price_var.get(), stock_var.get())
    refresh_tree()

def delete_selected_product():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a product to delete.")
        return
    pid = tree.item(selected)['values'][0]
    delete_product(pid)
    refresh_tree()

def forecast_selected_product():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a product to forecast.")
        return
    pid = tree.item(selected)['values'][0]
    forecast_stock(pid)

# ----------------------
# GUI
# ----------------------
root = tk.Tk()
root.title("Intelligent Inventory Management System")
root.geometry("1000x600")

# Form Labels and Inputs
tk.Label(root, text="Name").grid(row=0, column=0)
tk.Label(root, text="Category").grid(row=1, column=0)
tk.Label(root, text="Price").grid(row=2, column=0)
tk.Label(root, text="Stock").grid(row=3, column=0)

name_var = tk.StringVar()
cat_var = tk.StringVar()
price_var = tk.DoubleVar()
stock_var = tk.IntVar()
tk.Entry(root, textvariable=name_var).grid(row=0, column=1)
tk.Entry(root, textvariable=cat_var).grid(row=1, column=1)
tk.Entry(root, textvariable=price_var).grid(row=2, column=1)
tk.Entry(root, textvariable=stock_var).grid(row=3, column=1)

# Inventory Table
tree = ttk.Treeview(root, columns=("ID", "Name", "Category", "Price", "Stock"), show="headings")
for col in ("ID", "Name", "Category", "Price", "Stock"):
    tree.heading(col, text=col)
tree.grid(row=5, column=0, columnspan=8, pady=20, padx=10)

# Style headers
style = ttk.Style()
style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

# Button Frame
button_frame = tk.Frame(root)
button_frame.grid(row=4, column=0, columnspan=8, pady=10)

# Buttons
tk.Button(button_frame, text="Add Product", width=12, command=add_selected_product).grid(row=0, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Update Product", width=12, command=update_selected_product).grid(row=0, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Delete Product", width=12, command=delete_selected_product).grid(row=0, column=2, padx=5, pady=5)
tk.Button(button_frame, text="Forecast Stock", width=12, command=forecast_selected_product).grid(row=0, column=3, padx=5, pady=5)
tk.Button(button_frame, text="Export CSV", width=12, command=export_inventory).grid(row=1, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Import CSV", width=12, command=import_inventory).grid(row=1, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Dashboard", width=12, command=show_dashboard).grid(row=1, column=2, padx=5, pady=5)
tk.Button(button_frame, text="Record Sale", width=12, command=record_sale_product).grid(row=1, column=3, padx=5, pady=5)
tk.Button(button_frame, text="Order Product", width=12, command=order_product).grid(row=2, column=0, padx=5, pady=5)

# Refresh table function
def refresh_tree():
    for row in tree.get_children():
        tree.delete(row)
    for prod in get_all_products():
        tree.insert("", tk.END, values=prod)

refresh_tree()
root.mainloop()