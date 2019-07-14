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
    """Handles exceptions raise from query executions
    """

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
        """Creates a sqlite database with the given division name

        :param str division: a name of the sqlite database
        """
        self._cursor = None
        self.division = division

        # Create database directory and file if not exist
        _path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".db")
        os.makedirs(_path, exist_ok=True)
        self.connection = sqlite3.connect(
            os.path.join(_path, f"{self.division}_pyjj.db")
        )

    @handle_exception
    def add_url(self, url: str, tags: list = None) -> Tuple[bool, str]:
        """Inserts a url with tags if it is given

        :param str url: a url to insert
        :param list tags: a list of tags to be attached to the url
        """
        self.cursor.execute(
            f"INSERT INTO pyjj_{self.division}_urls (url) VALUES ('{url}')"
        )
        self.connection.commit()
        url_id = self.cursor.lastrowid
        if tags:
            self.add_tags(url_id=url_id, tags=tags)

        return True, f"Added successfully! id: {url_id}"

    @handle_exception
    def list_urls(self, tag: str = None) -> Tuple[bool, list]:
        """Returns a list of urls filtered by a tag if it is given.

        :param str tag: a tag attached to urls; it is used to filter urls
        :return: a tuple with a status of select query and a list of urls
        """
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
    def edit_url(self, id: int, url: str) -> Tuple[bool, str]:
        """Update url with id

        :param int id: an id of the url
        :param str url: a new url to update
        :return: a tuple with a status of update query and a message
        """
        now = datetime.now()
        edited_time = now.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            f"UPDATE pyjj_{self.division}_urls SET url='{url}', "
            f"created_at='{edited_time}' WHERE id={id}"
        )
        self.connection.commit()
        return True, f"Edited successfully! id: {id}"

    @handle_exception
    def get_url(self, id: int) -> Tuple[bool, object]:
        """Returns data that includes url and tags

        :param int id: an id of the url
        :return: a tuple with a status of select query and a result
        """
        self.cursor.execute(f"SELECT * FROM pyjj_{self.division}_urls WHERE id={id}")
        result = self.cursor.fetchone()
        if result:
            return True, result
        else:
            return False, f"Given id does not exist! id: {id}"

    @handle_exception
    def remove_url(self, id: int) -> Tuple[bool, str]:
        """Remove url with id

        :param int id: an id of the url
        :return: a tuple with a status of delete query and a message
        """
        self.cursor.execute(f"DELETE FROM pyjj_{self.division}_urls WHERE id={id}")
        self.connection.commit()
        return True, f"Removed successfully! id: {id}"

    @handle_exception
    def list_tags(self) -> Tuple[bool, list]:
        """Returns a list of tags

        :return: a tuple with a status of select query and a list of tags
        """
        self.cursor.execute(f"SELECT tag, created_at FROM pyjj_{self.division}_tags")
        tags = self.cursor.fetchall()
        return bool(tags), list(zip(range(1, len(tags) + 1), tags))

    @handle_exception
    def add_tags(self, url_id: int, tags: list) -> Tuple[bool, str]:
        """Attach tags to a url

        :param int url_id: an id of the url
        :param list tags: a list of tags(tag name)
        :return: a tuple with a status of insert query and a message
        """
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
                f"INSERT INTO pyjj_{self.division}_url_tags (url_id, tag_id)"
                f" VALUES ('{url_id}', '{tag_id}')"
            )

        self.connection.commit()
        return True, f"Added successfully! tags: {tags}"

    @handle_exception
    def check_tag(self, tag: str) -> Tuple[bool, int]:
        """Returns a tag id if the given tag exists, if not returns -1

        :param str tag: a tag name
        :return: a tuple with a status of select query and a tag id
        """
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
        """Remove a url and tag relationship

        :param int url_id: an id of the url
        :param str tag: a tag name
        :return: a tuple with a status of delete query and a message
        """
        is_exist, tag_id = self.check_tag(tag)
        if is_exist:
            self.cursor.execute(
                f"DELETE FROM pyjj_{self.division}_url_tags WHERE "
                f"url_id={url_id} AND tag_id={tag_id}"
            )
            self.connection.commit()
            return True, f"Removed successfully! id: {tag_id}"
        else:
            return False, f"Given tag does not exist for {url_id}! tag: {tag}"

    @handle_exception
    def get_random_url(self, tag: str = None) -> Tuple[bool, tuple]:
        """Returns a randomly selected url from urls filtered by a tag if it is given

        :param str tag: a tag name
        :return: a tuple with a status of select query and the url
        """
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
