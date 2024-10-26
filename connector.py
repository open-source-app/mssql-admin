import pyodbc
from models import Objectifier as Objectify
import queries as aq


class MSSQLDatabase:
    def __init__(self, host_name, port, user_name, password, db_name):
        self.conn = None
        self.cursor = None
        try:
            connection_string = (
                f"DRIVER={{SQL Server}};SERVER={host_name};"
                f"DATABASE={db_name};UID={user_name};PWD={password}"
            )
            self.conn = pyodbc.connect(connection_string)
            self.cursor = self.conn.cursor()
        except pyodbc.Error as err:
            print(f"Error connecting to MSSQL: {err}")

    def fetch_table_names(self):
        query = aq.tables
        filters = []
        return self.fetch_all_data(query, filters)

    def fetch_row_count(self, table_name):
        query = f"SELECT COUNT(*) AS TotalRows FROM [{table_name}];"
        return self.fetch_one_data(query, [])

    def fetch_table_details(self, table_name):
        query = aq.table_info
        filters = [table_name]
        return self.fetch_all_data(query, filters)

    def fetch_primary_key_details(self, table_name):
        query = aq.primary_key_column
        filters = [table_name]
        return self.fetch_all_data(query, filters)

    def fetch_foreign_key_details(self, table_name):
        query = aq.foreign_keys
        filters = [table_name]
        return self.fetch_all_data(query, filters)

    def fetch_identity_details(self, table_name):
        query = f"SELECT IDENT_CURRENT({table_name});"
        filters = []
        return self.fetch_one_data(query, filters)

    def fetch_foreign_table_data(self, table_name, column_name):
        query = f"SELECT [{column_name}] from [{table_name}];"
        filters = []
        return self.fetch_all_data(query, filters)

    def get_paginated_results(
        self, table_name, columns, order_key, skip_rows, fetch_rows
    ):
        query = f"""
            SELECT {columns}
            FROM [{table_name}]
            ORDER BY {order_key}
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY;
        """
        print(table_name, columns, order_key, skip_rows, fetch_rows, query)
        return self.fetch_all_data(query, [skip_rows, fetch_rows])

    def insert_data(self, query, values):
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return Objectify(
                    {"status": True, "rows_affected": self.cursor.rowcount}
                )
            else:
                return Objectify({"status": False, "rows_affected": 0})
        except pyodbc.Error as err:
            self.conn.rollback()
            print(err)
            return Objectify(
                {
                    "status": False,
                    "message": "".join(err.args[1].split(".")[1:4]).strip(),
                }
            )

    def fetch_one_data(self, query, filters=[]):
        try:
            self.cursor.execute(query, filters)
            columns = [column[0] for column in self.cursor.description]
            record = self.cursor.fetchone()
            return Objectify(
                {"columns": columns, "values": list(record) if record else []}
            )
        except pyodbc.Error as err:
            print(f"error fetching record: {err}")
            return Objectify({"columns": [], "values": []})

    def fetch_all_data(self, query, filters=[]):
        try:
            self.cursor.execute(query, filters)
            columns = [column[0] for column in self.cursor.description]
            record = list(self.cursor.fetchall())
            return Objectify({"columns": columns, "values": record})
        except pyodbc.Error as err:
            print(f"error fetching record: {err}")
            return Objectify({"columns": [], "values": []})

    def close_cursor(self):
        if self.cursor:
            self.cursor.close()

    def close_connection(self):
        if self.conn:
            self.conn.close()
