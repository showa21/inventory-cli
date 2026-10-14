"""SQLite-backed inventory storage."""
import sqlite3
from dataclasses import dataclass


@dataclass
class Item:
    id: int
    name: str
    quantity: int
    price: float


class Inventory:
    def __init__(self, path=":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                quantity INTEGER NOT NULL CHECK (quantity >= 0),
                price REAL NOT NULL CHECK (price >= 0)
            )"""
        )

    def add(self, name, quantity, price):
        name = name.strip()
        if not name:
            raise ValueError("name must not be empty")
        if quantity < 0 or price < 0:
            raise ValueError("quantity and price must be non-negative")
        try:
            cur = self.conn.execute(
                "INSERT INTO items (name, quantity, price) VALUES (?, ?, ?)",
                (name, quantity, price),
            )
        except sqlite3.IntegrityError:
            raise ValueError(f"item '{name}' already exists") from None
        self.conn.commit()
        return Item(cur.lastrowid, name, quantity, price)

    def list(self, search=""):
        rows = self.conn.execute(
            "SELECT id, name, quantity, price FROM items WHERE name LIKE ? ORDER BY name",
            (f"%{search}%",),
        )
        return [Item(*r) for r in rows]

    def adjust(self, name, delta):
        row = self.conn.execute(
            "SELECT quantity FROM items WHERE name = ?", (name,)
        ).fetchone()
        if row is None:
            raise KeyError(name)
        if row[0] + delta < 0:
            raise ValueError("not enough stock")
        self.conn.execute(
            "UPDATE items SET quantity = quantity + ? WHERE name = ?", (delta, name)
        )
        self.conn.commit()
        return row[0] + delta

    def remove(self, name):
        cur = self.conn.execute("DELETE FROM items WHERE name = ?", (name,))
        self.conn.commit()
        if cur.rowcount == 0:
            raise KeyError(name)

    def total_value(self):
        return self.conn.execute(
            "SELECT COALESCE(SUM(quantity * price), 0) FROM items"
        ).fetchone()[0]

    def low_stock(self, threshold=5):
        rows = self.conn.execute(
            "SELECT id, name, quantity, price FROM items WHERE quantity <= ? ORDER BY quantity",
            (threshold,),
        )
        return [Item(*r) for r in rows]
