import sqlite3
import os
import shutil

class Storage:
    def __init__(self, db="database.db"):
        self.conn = sqlite3.connect(db)
        self.cursor = self.conn.cursor()
        self.create_table()
        
    def create_table(self):
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS snip (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                ocr_text TEXT NOT NULL,
                                x INTEGER,
                                y INTEGER,
                                width INTEGER,
                                height INTEGER,
                                date TEXT NOT NULL,
                                filepath TEXT NOT NULL
                            )
                            """)
        self.conn.commit()
        
    def add_snip(self, name, ocr_text, x, y, width, height, date, filepath):
        self.cursor.execute(
            "INSERT INTO snip (name, ocr_text, x, y, width, height, date, filepath) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, ocr_text, x, y, width, height, date, filepath)
        )
        self.conn.commit()
        
    def get_snips(self, id=None):
        if id is None:
            self.cursor.execute("SELECT * FROM snip")
            return self.cursor.fetchall()
        else:
            self.cursor.execute("SELECT * FROM snip WHERE id = ?", (id,))
            return self.cursor.fetchone()

    def update_snip(self, id, name):
        if self.conn is None:
            return
        self.cursor.execute("UPDATE snip SET name = ? WHERE id = ?", (name, id))
        self.conn.commit()
        
    def delete_snip(self, id=None):
        if id is None:
            self.cursor.execute("SELECT filepath FROM snip")
            rows = self.cursor.fetchall()
            self.cursor.execute("DELETE FROM snip")
            
            for (file_path,) in rows:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                elif os.path.isfile(file_path):
                    os.remove(file_path)
        else:
            self.cursor.execute("SELECT filepath FROM snip WHERE id = ?", (id,))
            row = self.cursor.fetchone()
            
            if row:
                file_path = row[0]
                if os.path.exists(file_path):
                    os.remove(file_path)
            self.cursor.execute("DELETE FROM snip WHERE id = ?", (id,))
        self.conn.commit()
    
    def delete_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS snip")
        self.conn.commit()

    def close(self):
        self.conn.close()