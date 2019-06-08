from datetime import datetime
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
    def wrapper(*args, **kwargs) -> Tuple[bool, str]:
        try:
            return func(*args, **kwargs)
        except sqlite3.IntegrityError:
            return False, "Given url already exists"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    return wrapper


class Database:
    def __init__(self, division="default"):
        self._cursor = None
        self.division = division

        # Create database directory and file if not exist
        _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.db")
        os.makedirs(_path, exist_ok=True)
        self.connection = sqlite3.connect(
            os.path.join(_path, f"{self.division}_pyjj.db")
        )

    @handle_exception
    def add_url(self, url, tags) -> Tuple[bool, str]:
        self.cursor.execute(
            f"INSERT INTO pyjj_{self.division}_urls (url) VALUES ('{url}')"
        )
        self.connection.commit()
        self.add_tags(url_id=self.cursor.lastrowid, tags=tags)
        return True, f"Added successfully! id: {self.cursor.lastrowid}"

    @handle_exception
    def list_urls(self) -> Tuple[bool, list]:
        self.cursor.execute(f"SELECT * FROM pyjj_{self.division}_urls")
        return True, self.cursor.fetchall()

    @handle_exception
    def edit_url(self, id, url) -> Tuple[bool, str]:
        now = datetime.now()
        edited_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            f"UPDATE pyjj_{self.division}_urls SET url='{url}', created_at='{edited_time}' WHERE id={id}"
        )
        self.connection.commit()
        return True, f"Edited successfully! id: {id}"

    @handle_exception
    def get_url(self, id) -> Tuple[bool, object]:
        self.cursor.execute(f"SELECT * FROM pyjj_{self.division}_urls WHERE id={id}")
        result = self.cursor.fetchone()
        if result:
            return True, result
        else:
            return False, f"Given id does not exist! id: {id}"

    @handle_exception
    def remove_url(self, id) -> Tuple[bool, str]:
        self.cursor.execute(f"DELETE FROM pyjj_{self.division}_urls WHERE id={id}")
        self.connection.commit()
        return True, f"Removed successfully! id: {id}"

    @handle_exception
    def add_tags(self, url_id, tags: list) -> Tuple[bool, str]:
        for tag in tags:
            # Insert to tag table
            self.cursor.execute(
                f"INSERT INTO pyjj_{self.division}_tags (tag) VALUES ('{tag}')"
            )

            # Insert to url-tag table
            self.cursor.execute(
                f"INSERT INTO pyjj_{self.division}_url_tags (url_id, tag_id) VALUES ('{url_id}', '{self.cursor.lastrowid}')"
            )
        self.connection.commit()
        return True, f"Added successfully! tags: {tags}"

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = self.connection.cursor()
        return self._cursor

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
