import env_file
import datetime
import pyodbc
from models import Objectify
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

    def fetch_tables(self):
        query = aq.tables
        filters = []
        return self.fetch_all_data(query, filters)

    def fetch_plaza_details(self):
        query = "SELECT * FROM [Plaza] where [ID] = ?"
        filters = [Plaza_ID]
        return self.fetch_one_data(query, filters)

    def get_page_size(self, table_name):
        query = f"SELECT COUNT(*) AS TotalRows FROM [{table_name}];" 
        return self.fetch_one_data(query, [])

    def fetch_lane_details(self):
        query = "SELECT * FROM [Lane] where [ID] = ?"
        filters = [Lane_ID]
        return self.fetch_one_data(query, filters)

    def fetch_table_details(self, table_name):
        query = aq.table_info
        filters = [table_name]
        return self.fetch_all_data(query, filters)

    def fetch_paginated_table_data(self, table_name, sort_column,  page_number, page_size):
        query = f"SELECT * FROM [{table_name}] ORDER BY [{sort_column}] OFFSET ? ROWS FETCH NEXT ? ROWS ONLY;"
        offset = (page_number - 1) * page_size
        filters = [offset, page_size]
        return self.fetch_all_data(query, filters)

    def fetch_row_details(self, table_name, primary_key, row_id):
        query = f"SELECT TOP 1 * FROM [{table_name}] WHERE [{primary_key}]=?;"
        filters = [row_id]
        return self.fetch_one_data(query, filters)

    def fetch_foreign_key_details(self, table_name):
        query = aq.foreign_keys
        filters = [table_name]
        return self.fetch_all_data(query, filters)

    def fetch_table_data(self, table_name):
        query = f"SELECT * FROM [{table_name}]"
        filters = []
        return self.fetch_all_data(query, filters)

    def fetch_shift_details(self):
        query = "SELECT * FROM [shift] WHERE Start_time < ? AND End_Time > ?"
        time = f"{datetime.datetime.now().time()}"
        filters = [time, time]

    def fetch_one_data(self, query, filters=[]):
        try:
            self.cursor.execute(query, filters)
            columns = [column[0] for column in self.cursor.description]
            record = self.cursor.fetchone()
            return Objectify({'columns':columns, 'values':list(record) if record else []})
        except pyodbc.Error as err:
            print(f"error fetching record: {err}")
            return Objectify({'columns':[], 'values':[]})

    def insert_data(self, query, values):
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
            return Objectify({'status': 'success', 'rows_affected': self.cursor.rowcount})
        except pyodbc.Error as err:
            print(f"error inserting data: {err}")
            self.conn.rollback()
            return Objectify({'status': 'error', 'rows_affected': 0})

    def fetch_primary_key_details(self, table_name):
        query = aq.primary_key_column
        filters = [table_name]
        return self.fetch_one_data(query, filters)

    def fetch_identity_details(self, table_name):
        query = aq.has_identity
        filters = [table_name]
        return self.fetch_one_data(query, filters)

    def get_paginated_results(self, table_name, columns, primary_key, skip_rows, fetch_rows):
        query = f"""
            SELECT {columns} 
            FROM [{table_name}]
            ORDER BY {primary_key}
            OFFSET ? ROWS
            FETCH NEXT ? ROWS ONLY;
        """
        return self.fetch_all_data(query, [skip_rows, fetch_rows])

    def fetch_all_data(self, query, filters=[]):
        try:
            self.cursor.execute(query, filters)
            columns = [column[0] for column in self.cursor.description]
            record = list(self.cursor.fetchall())
            return Objectify({'columns':columns, 'values':record})
        except pyodbc.Error as err:
            print(f"error fetching record: {err}")
            return Objectify({'columns':[], 'values':[]})


    def close_cursor(self):
        if self.cursor:
            self.cursor.close()

    def close_connection(self):
        if self.conn:
            self.conn.close()

