"""SQLite access layer for wardrobe clothing items.

All queries use parameterized placeholders (?) so user-supplied values are
never interpolated into SQL strings (mitigates SQL injection).
"""

import sqlite3


class Database:
    """Thin wrapper around a sqlite3 connection for ClothingItems CRUD."""

    def __init__(self, db_file):
        """Open a connection to db_file and create a cursor.

        Args:
            db_file: Path to the SQLite database file (e.g. wardrobe.db).
        """
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_table(self):
        """Create the ClothingItems table if it does not already exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ClothingItems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                item_color TEXT NOT NULL,
                item_size TEXT NOT NULL,
                item_category TEXT NOT NULL,
                item_subcategory TEXT NOT NULL,
                item_image_path TEXT NOT NULL)""")
        self.conn.commit()

    def add_clothing_item(
        self,
        item_name,
        item_color,
        item_size,
        item_category,
        item_subcategory,
        item_image_path,
    ):
        """Insert one clothing item. Values are bound via ? placeholders."""
        self.cursor.execute(
            """INSERT INTO ClothingItems (
            item_name, item_color, item_size, item_category, item_subcategory, 
            item_image_path) VALUES (?, ?, ?, ?, ?, ?)""",
            (
                item_name,
                item_color,
                item_size,
                item_category,
                item_subcategory,
                item_image_path,
            ),
        )
        self.conn.commit()

    def get_all_clothing_items(self):
        """Return all rows from ClothingItems (unordered)."""
        self.cursor.execute("SELECT * FROM ClothingItems")
        return self.cursor.fetchall()

    def get_clothing_item_by_id(self, item_id):
        """Return one row by primary key, or None if not found."""
        self.cursor.execute("SELECT * FROM ClothingItems WHERE id = ?", (item_id,))
        return self.cursor.fetchone()

    def close(self):
        """Close the database connection."""
        self.conn.close()
