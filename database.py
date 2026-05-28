"""
database.py
-----------
Handles SQLite connection, schema creation, and seed data.
"""

import sqlite3

DB_PATH = "inventory.db"


def get_conn() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create tables if they don't exist and seed demo data on first run."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT    NOT NULL,
                category  TEXT    NOT NULL,
                qty       INTEGER NOT NULL DEFAULT 0,
                threshold INTEGER NOT NULL DEFAULT 10,
                price     REAL    NOT NULL DEFAULT 0.0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sales_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                week       INTEGER NOT NULL,
                units_sold INTEGER NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        _seed(conn)


def _seed(conn: sqlite3.Connection):
    """Insert demo products and 8-week sales history if the table is empty."""
    if conn.execute("SELECT COUNT(*) FROM products").fetchone()[0] > 0:
        return

    seed_data = [
        ("Wireless Keyboard",       "Electronics", 45, 20, 49.99, [30,28,35,32,38,40,36,42]),
        ("USB-C Hub",               "Electronics", 12, 25, 34.99, [18,20,22,19,24,21,25,23]),
        ("Standing Desk Mat",       "Office",        6, 15, 29.99, [ 8,10, 9,11,12,10,13,11]),
        ("Mechanical Pencils 12pk", "Stationery",   80, 30,  7.49, [40,45,38,50,48,52,55,58]),
        ("Notebook A5",             "Stationery",    3, 20,  5.99, [22,24,20,26,28,25,30,27]),
        ("HDMI Cable 2m",           "Electronics",  55, 15, 12.99, [15,14,16,18,17,19,20,18]),
        ("Ergonomic Mouse",         "Electronics",  18, 20, 59.99, [10,12,11,13,14,12,15,14]),
        ("Whiteboard Markers",      "Office",       35, 25,  8.99, [20,22,19,24,23,25,26,28]),
    ]

    for name, cat, qty, threshold, price, sales in seed_data:
        conn.execute(
            "INSERT INTO products (name, category, qty, threshold, price) VALUES (?,?,?,?,?)",
            (name, cat, qty, threshold, price)
        )
        pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        for week, units in enumerate(sales, 1):
            conn.execute(
                "INSERT INTO sales_history (product_id, week, units_sold) VALUES (?,?,?)",
                (pid, week, units)
            )
