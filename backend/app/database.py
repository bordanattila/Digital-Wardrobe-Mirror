"""SQLite access layer for wardrobe clothing items.

All queries use parameterized placeholders (?) so user-supplied values are
never interpolated into SQL strings (mitigates SQL injection).
"""

import sqlite3


class Database:
    """Thin wrapper around a sqlite3 connection for ClothingItem CRUD."""

    def __init__(self, db_file):
        """Open a connection to db_file and create a cursor.

        Args:
            db_file: Path to the SQLite database file (e.g. wardrobe.db).
        """
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def create_table(self):
        """Create the ClothingItem table if it does not already exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ClothingItem (
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
            """INSERT INTO ClothingItem (
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
        """Return all rows from ClothingItem (unordered)."""
        self.cursor.execute("SELECT * FROM ClothingItem")
        return self.cursor.fetchall()

    def get_clothing_item_by_id(self, item_id):
        """Return one row by primary key, or None if not found."""
        self.cursor.execute("SELECT * FROM ClothingItem WHERE id = ?", (item_id,))
        return self.cursor.fetchone()

    def update_clothing_item_by_id(
        self, item_id, item_name, item_color, item_size, item_category, item_subcategory
    ):
        """Update metadata for one row; item_image_path is not changed."""
        self.cursor.execute(
            """UPDATE ClothingItem SET item_name = ?, item_color = ?, item_size = ?,
            item_category = ?, item_subcategory = ? WHERE id = ?""",
            (
                item_name,
                item_color,
                item_size,
                item_category,
                item_subcategory,
                item_id,
            ),
        )
        self.conn.commit()

    def delete_clothing_item_by_id(self, item_id):
        """Delete one row by primary key."""
        self.cursor.execute("DELETE FROM ClothingItem WHERE id = ?", (item_id,))
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()
