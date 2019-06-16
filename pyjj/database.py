import os
import sqlite3
from datetime import datetime
from random import choice
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
    def add_url(self, url, tags=None) -> Tuple[bool, str]:
        self.cursor.execute(
            f"INSERT INTO pyjj_{self.division}_urls (url) VALUES ('{url}')"
        )
        self.connection.commit()

        if tags:
            self.add_tags(url_id=self.cursor.lastrowid, tags=tags)

        return True, f"Added successfully! id: {self.cursor.lastrowid}"

    @handle_exception
    def list_urls(self, tag: str = None) -> Tuple[bool, list]:
        sql = f"SELECT * FROM pyjj_{self.division}_urls"

        if tag:
            is_tag_exist, tag_id = self.check_tag(tag)
            if is_tag_exist:
                # Get urls with the given tag
                sql = f"""SELECT A.* FROM pyjj_{self.division}_urls AS A
                        INNER JOIN pyjj_{self.division}_url_tags AS B ON A.id=B.url_id
                        WHERE B.tag_id={tag_id}"""
            else:
                # If the given tag doesn't exist, return empty list
                return True, []

        self.cursor.execute(sql)
        url_rows = self.cursor.fetchall()
        tags = []

        for url in url_rows:
            self.cursor.execute(
                f"""SELECT B.tag FROM pyjj_{self.division}_url_tags AS A
                INNER JOIN pyjj_{self.division}_tags AS B ON A.tag_id=B.id
                WHERE url_id={url[0]}"""
            )
            url_tags = [t[0] for t in self.cursor.fetchall()]
            tags.append(url_tags)
        return True, list(zip(url_rows, tags))

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
    def list_tags(self) -> Tuple[bool, list]:
        self.cursor.execute(f"SELECT tag, created_at FROM pyjj_{self.division}_tags")
        tags = self.cursor.fetchall()
        return bool(tags), list(zip(range(1, len(tags) + 1), tags))

    @handle_exception
    def add_tags(self, url_id, tags: list) -> Tuple[bool, str]:
        for tag in tags:
            is_exists, tag_id = self.check_tag(tag)

            if not is_exists:
                # Insert to tag table
                self.cursor.execute(
                    f"INSERT INTO pyjj_{self.division}_tags (tag) VALUES ('{tag}')"
                )
                tag_id = self.cursor.lastrowid

            # Insert to url-tag table
            self.cursor.execute(
                f"INSERT INTO pyjj_{self.division}_url_tags (url_id, tag_id) VALUES ('{url_id}', '{tag_id}')"
            )

        self.connection.commit()
        return True, f"Added successfully! tags: {tags}"

    @handle_exception
    def check_tag(self, tag: str) -> Tuple[bool, int]:
        self.cursor.execute(
            f"SELECT id FROM pyjj_{self.division}_tags WHERE tag='{tag}'"
        )
        row = self.cursor.fetchone()
        if row:
            return True, row[0]
        else:
            return False, -1

    @handle_exception
    def remove_url_tag(self, url_id: int, tag: str) -> Tuple[bool, str]:
        is_exist, tag_id = self.check_tag(tag)
        if is_exist:
            self.cursor.execute(
                f"DELETE FROM pyjj_{self.division}_url_tags WHERE url_id={url_id} AND tag_id={tag_id}"
            )
            self.connection.commit()
            return True, f"Removed successfully! id: {tag_id}"
        else:
            return False, f"Given tag does not exist for {url_id}! tag: {tag}"

    @handle_exception
    def get_random_url(self, tag: str = None) -> Tuple[bool, tuple]:
        is_urls_exist, urls = self.list_urls(tag)
        url = choice(urls) if urls else ()
        return is_urls_exist, url

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
