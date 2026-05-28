"""
models.py
---------
Data access functions for products and sales history.
All database reads/writes outside of init go through here.
"""

import random
import sqlite3
import pandas as pd
from database import get_conn


# ── Read ───────────────────────────────────────────────────────────────────────

def get_all_products() -> pd.DataFrame:
    """Return all products as a Pandas DataFrame."""
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM products", conn)


def get_product(product_id: int) -> dict | None:
    """Return a single product row as a dict, or None if not found."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
    if row is None:
        return None
    return dict(zip(["id", "name", "category", "qty", "threshold", "price"], row))


def get_sales(product_id: int) -> list[int]:
    """Return ordered list of weekly units sold for a product."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT units_sold FROM sales_history WHERE product_id = ? ORDER BY week",
            (product_id,)
        ).fetchall()
    return [r[0] for r in rows]


def get_stock_status(qty: int, threshold: int) -> str:
    """
    Classify stock level relative to threshold.
      > 70%  → OK
      30-70% → Low
      < 30%  → Critical
    """
    if threshold == 0:
        return "OK"
    ratio = qty / threshold
    if ratio <= 0.3:
        return "Critical"
    if ratio <= 0.7:
        return "Low"
    return "OK"


# ── Write ──────────────────────────────────────────────────────────────────────

def add_product(data: dict):
    """Insert a new product and generate 8 weeks of seed sales history."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO products (name, category, qty, threshold, price) VALUES (?,?,?,?,?)",
            (data["name"], data["category"], data["qty"], data["threshold"], data["price"])
        )
        pid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        base = max(1, data["qty"] // 4)
        for week in range(1, 9):
            conn.execute(
                "INSERT INTO sales_history (product_id, week, units_sold) VALUES (?,?,?)",
                (pid, week, random.randint(base, base * 2))
            )


def update_product(product_id: int, data: dict):
    """Update an existing product's fields."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE products SET name=?, category=?, qty=?, threshold=?, price=? WHERE id=?",
            (data["name"], data["category"], data["qty"], data["threshold"], data["price"], product_id)
        )


def update_threshold(product_id: int, threshold: int):
    """Update only the restock threshold for a product."""
    with get_conn() as conn:
        conn.execute(
            "UPDATE products SET threshold=? WHERE id=?",
            (threshold, product_id)
        )


def delete_product(product_id: int):
    """Delete a product and its associated sales history."""
    with get_conn() as conn:
        conn.execute("DELETE FROM sales_history WHERE product_id=?", (product_id,))
        conn.execute("DELETE FROM products WHERE id=?", (product_id,))
