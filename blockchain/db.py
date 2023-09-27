import os
import sqlite3
import utils


class Db:
    def __init__(self, filename, recover=False):
        self.filename = filename
        if recover:
            self.load()
        else:
            self.init_db()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "rb") as f:
                # load the db from the file
                pass
        else:
            self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect(self.filename)
        self.c = self.conn.cursor()
        self.create_all_tables()

    def close(self):
        self.conn.close()

    def create_all_tables(self):
        pass

    def drop_all_tables(self):
        pass

    def create_table(self, table_name, **fields):
        # create a table in the db
        pass

    def drop_table(self, table_name):
        # drop a table from the db
        pass

    def insert(self, table_name, **values):
        # insert values into a table
        pass

    def update(self, table_name, **values):
        # update contract into table
        pass

    @property
    def hash(self):
        return utils.sha3(self.filename)

    def __repr__(self):
        print(f"<{self.__class__.__name__} hash= {self.hash}>")
