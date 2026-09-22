import sqlite3

class Database:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ClothingItems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                item_color TEXT NOT NULL,
                item_size TEXT NOT NULL,
                item_category TEXT NOT NULL,
                item_subcategory TEXT NOT NULL,
                item_image_path TEXT NOT NULL)''')
        self.conn.commit()

    def add_clothing_item(self, item_name, item_type, item_color, item_size, item_price, item_image):
        self.cursor.execute('INSERT INTO ClothingItems (item_name, item_type, item_color, item_size, item_price, item_image) VALUES (?, ?, ?, ?, ?, ?)', (item_name, item_type, item_color, item_size, item_price, item_image))
        self.conn.commit()

    def close(self):
        self.conn.close()