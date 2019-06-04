import sqlite3
import os
from typing import List, Dict, Tuple


def generate_create_sqls(tbl_name: str, columns: List[tuple], keys: Dict) -> str:
    """
    tbl_name: string a table name after pyjj_{tbl_name}
    columns: list of tuples (column_name, data_type, options)
    keys: dict of keys key: (columns, options)
    """
    assert tbl_name
    column_stmt = ",".join(f"{key} {val} {opt}" for key, val, opt in columns)
    key_stmt = (
        ","
        + ",".join(
            f"{key} ({','.join(value[0])}) {value[1]}" for key, value in keys.items()
        )
        if keys
        else ""
    )
    return f"CREATE TABLE IF NOT EXISTS pyjj_{tbl_name} ({column_stmt} {key_stmt});"


def handle_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.IntegrityError:
            return False, "Given url already exists"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    return wrapper


class Database:
    def __init__(self, division="default", path: str = "./"):
        self._cursor = None
        self._division = division

        if os.path.exists(os.path.dirname(path)):
            self.connection = sqlite3.connect(
                os.path.join(path, f"{self.division}_pyjj.db")
            )
        else:
            raise NotADirectoryError()

    @handle_exception
    def add_url(self, url) -> Tuple[bool, str]:
        self.cursor.execute(
            f"INSERT INTO pyjj_{self.division}_urls (url) VALUES ('{url}')"
        )
        self.connection.commit()
        return True, f"Added successfully! id: {self.cursor.lastrowid}"

    @handle_exception
    def list_urls(self):
        self.cursor.execute(f"SELECT * FROM pyjj_{self.division}_urls")
        return True, self.cursor.fetchall()

    @handle_exception
    def edit_url(self, id, url):
        self.cursor.execute(
            f"UPDATE pyjj_{self.division}_urls SET url='{url}' WHERE id={id}"
        )
        self.connection.commit()
        return True, f"Edited successfully! id: {id}"

    @handle_exception
    def remove_url(self, id):
        self.cursor.execute(f"DELETE FROM pyjj_{self.division}_urls WHERE id={id}")
        self.connection.commit()
        return True, f"Removed successfully! id: {id}"

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = self.connection.cursor()
        return self._cursor

    @property
    def division(self):
        return self._division

    @division.setter
    def division(self, value):
        self._division = value
        self.setup()

    def close(self):
        if self.connection:
            self.connection.close()

    @handle_exception
    def setup(self):
        """Initialize tables in a database"""
        default_table_urls = {
            "tbl_name": f"{self.division}_urls",
            "columns": [
                ("id", "INTEGER", "PRIMARY KEY AUTOINCREMENT"),
                ("url", "TEXT", "UNIQUE NOT NULL"),
                ("created_at", "DATE", "DEFAULT(datetime('now', 'localtime'))"),
            ],
            "keys": {},
        }
        default_table_tags = {
            "tbl_name": f"{self.division}_tags",
            "columns": [
                ("id", "INTEGER", "PRIMARY KEY AUTOINCREMENT"),
                ("tag", "TEXT", "UNIQUE NOT NULL"),
                ("created_at", "DATE", "DEFAULT(datetime('now', 'localtime'))"),
            ],
            "keys": {},
        }
        default_table_url_tags = {
            "tbl_name": f"{self.division}_url_tags",
            "columns": [
                ("url_id", "INTEGER", "NOT NULL"),
                ("tag_id", "INTEGER", "NOT NULL"),
            ],
            "keys": {
                f"FOREIGN KEY (url_id) REFERENCES pyjj_{self.division}_urls": (
                    ["id"],
                    "ON DELETE CASCADE",
                ),
                f"FOREIGN KEY (tag_id) REFERENCES pyjj_{self.division}_tags": (
                    ["id"],
                    "ON DELETE CASCADE",
                ),
            },
        }

        for sql in (
            generate_create_sqls(**default_table_urls),
            generate_create_sqls(**default_table_tags),
            generate_create_sqls(**default_table_url_tags),
        ):
            self.cursor.execute(sql)

        self.connection.commit()
