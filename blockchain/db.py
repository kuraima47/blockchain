import os
import sqlite3
import utils


class Db:
    # try to integrate merkle patricia tree

    def __init__(self, filename, recover=False):
        self.conn = sqlite3.connect(filename)
        self.c = self.conn.cursor()
        self.tables = [
            {
                "name": "eoa_accounts",
                "fields": [
                    ("address", "TEXT"),
                    ("balance", "INTEGER"),
                    ("nonce", "INTEGER"),
                ],
            },
            {
                "name": "accounts",
                "fields": [
                    ("address", "TEXT"),
                    ("balance", "INTEGER"),
                    ("nonce", "INTEGER"),
                    ("code", "TEXT"),
                    ("storage", "TEXT"),
                ],
            },
            {
                "name": "contract_accounts",
                "fields": [
                    ("address", "TEXT"),
                    ("balance", "INTEGER"),
                    ("nonce", "INTEGER"),
                    ("storage", "TEXT"),
                ],
            },
            {
                "name": "contract_storage",
                "fields": [
                    ("address", "TEXT"),
                    ("key", "TEXT"),
                    ("value", "TEXT"),
                ],
            },
            {
                "name": "tx_pool",
                "fields": [
                    ("hash", "TEXT"),
                    ("nonce", "INTEGER"),
                    ("gas_price", "INTEGER"),
                    ("gas", "INTEGER"),
                    ("to", "TEXT"),
                    ("value", "INTEGER"),
                    ("data", "TEXT"),
                    ("v", "INTEGER"),
                    ("r", "INTEGER"),
                    ("s", "INTEGER"),
                ],
            },
            {
                "name": "transaction",
                "fields": [
                    ("hash", "TEXT"),
                    ("nonce", "INTEGER"),
                    ("gas_price", "INTEGER"),
                    ("gas", "INTEGER"),
                    ("from", "TEXT"),
                    ("to", "TEXT"),
                    ("value", "INTEGER"),
                    ("data", "TEXT"),
                    ("v", "INTEGER"),
                    ("r", "INTEGER"),
                    ("s", "INTEGER"),
                    ("block", "INTEGER"),
                    ("used_gas", "INTEGER"),
                ]
            }
        ]
        self.filename = filename

        if not recover:
            self.init_db()

    def init_db(self):
        self.create_all_tables()

    def close(self):
        self.conn.close()

    def create_all_tables(self):
        for table in self.tables:
            self.create_table(table["name"], **dict(table["fields"]))

    def drop_all_tables(self):
        for table in self.tables:
            self.drop_table(table["name"])

    def create_table(self, table_name, **fields):
        self.c.execute(
            f"CREATE TABLE {table_name} ({','.join([f'{k} {v}' for k, v in fields.items()])})"
        )
        self.conn.commit()

    def drop_table(self, table_name):
        self.c.execute(f"DROP TABLE {table_name}")
        self.conn.commit()

    def insert(self, table_name, **values):
        self.c.execute(
            f"INSERT INTO {table_name} ({','.join([k for k in values.keys()])}) VALUES ({','.join(['?' for _ in values.keys()])})",
            [v for v in values.values()],
        )

    def update(self, table_name, **values):
        self.c.execute(
            f"UPDATE {table_name} SET {','.join([f'{k}=?' for k in values.keys()])}",
            [v for v in values.values()],
        )

    @property
    def hash(self):
        return utils.sha3(self.filename)

    def __repr__(self):
        print(f"<{self.__class__.__name__} hash= {self.hash}>")
