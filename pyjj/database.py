import sqlite3
import os
from typing import List, Dict


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
    def __init__(self, path: str = "./"):
        if os.path.exists(os.path.dirname(path)):
            self.connection = sqlite3.connect(os.path.join(path, "pyjj.db"))
        else:
            raise NotADirectoryError()

        self._cursor = None

    @handle_exception
    def add_url(self, url) -> (bool, str):
        self.cursor.execute(f"INSERT INTO pyjj_default_urls (url) VALUES ('{url}')")
        self.connection.commit()
        return True, f"Added successfully! id: {self.cursor.lastrowid}"

    @handle_exception
    def list_urls(self):
        self.cursor.execute("SELECT * FROM pyjj_default_urls")
        return True, self.cursor.fetchall()

    @handle_exception
    def edit_url(self, id, url):
        self.cursor.execute(f"UPDATE pyjj_default_urls SET url='{url}' WHERE id={id}")
        self.connection.commit()
        return True, f"Edited successfully! id: {id}"

    @handle_exception
    def remove_url(self, id):
        self.cursor.execute(f"DELETE FROM pyjj_default_urls WHERE id={id}")
        self.connection.commit()
        return True, f"Removed successfully! id: {id}"

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = self.connection.cursor()
        return self._cursor

    def close(self):
        if self.connection:
            self.connection.close()

    # def _default(self):
    #     cursor = self.connection.cursor()
    #     DEFAULT_TABLE_URLS = {
    #         "tbl_name": "default_urls",
    #         "columns": [
    #             ("id", "INTEGER", "PRIMARY KEY AUTOINCREMENT"),
    #             ("url", "TEXT", "UNIQUE NOT NULL"),
    #             ("created_at", "DATE", "DEFAULT(datetime('now', 'localtime'))"),
    #         ],
    #         "keys": {},
    #     }
    #     DEFAULT_TABLE_TAGS = {
    #         "tbl_name": "default_tags",
    #         "columns": [
    #             ("id", "INTEGER", "PRIMARY KEY AUTOINCREMENT"),
    #             ("tag", "TEXT", "UNIQUE NOT NULL"),
    #             ("created_at", "DATE", "DEFAULT(datetime('now', 'localtime'))"),
    #         ],
    #         "keys": {},
    #     }
    #     DEFAULT_TABLE_URLTAGS = {
    #         "tbl_name": "default_url_tags",
    #         "columns": [
    #             ("url_id", "INTEGER", "NOT NULL"),
    #             ("tag_id", "INTEGER", "NOT NULL"),
    #         ],
    #         "keys": {
    #             "FOREIGN KEY (url_id) REFERENCES pyjj_default_urls": (
    #                 ["id"],
    #                 "ON DELETE CASCADE",
    #             ),
    #             "FOREIGN KEY (tag_id) REFERENCES pyjj_default_tags": (
    #                 ["id"],
    #                 "ON DELETE CASCADE",
    #             ),
    #         },
    #     }
    #     # print(generate_create_sqls(**DEFAULT_TABLE_TAGS))
    #     # print(generate_create_sqls(**DEFAULT_TABLE_URLS))
    #     # print(generate_create_sqls(**DEFAULT_TABLE_URLTAGS))

    #     cursor.execute(generate_create_sqls(**DEFAULT_TABLE_TAGS))
    #     cursor.execute(generate_create_sqls(**DEFAULT_TABLE_URLS))
    #     cursor.execute(generate_create_sqls(**DEFAULT_TABLE_URLTAGS))

    #     cursor.execute(
    #         """
    #         INSERT OR REPLACE INTO pyjj_default_urls (url) VALUES ('https://www.github.com/achooan')
    #     """
    #     )

    #     cursor.execute(
    #         """
    #         INSERT OR REPLACE INTO pyjj_default_tags (tag) VALUES ('personal')
    #     """
    #     )

    #     cursor.execute(
    #         """
    #         INSERT OR REPLACE INTO pyjj_default_url_tags (url_id, tag_id) VALUES (1, 1)
    #     """
    #     )
    #     self.connection.commit()
