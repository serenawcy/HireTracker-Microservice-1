# Reference: https://github.com/donald-f-ferguson/demo-flask/blob/main/database_services/RDBService.py
import pymysql
import json
import logging

import middleware.context as context

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RDBService:

    def __init__(self):
        pass

    @classmethod
    def _get_db_connection(cls):

        db_connect_info = context.get_db_info()

        logger.info("RDBService._get_db_connection:")
        logger.info("\t HOST = " + db_connect_info['host'])
        logger.info("\t HOST = " + db_connect_info['host'])

        db_info = context.get_db_info()

        db_connection = pymysql.connect(
            **db_info,
            autocommit=True
        )
        return db_connection

    @classmethod
    def run_sql(cls, sql_statement, args, fetch=False):

        conn = RDBService._get_db_connection()

        try:
            cur = conn.cursor()
            res = cur.execute(sql_statement, args=args)
            if fetch:
                res = cur.fetchall()
        except Exception as e:
            conn.close()
            raise e

        return res

    @classmethod
    def get_by_prefix(cls, db_schema, table_name, column_name, value_prefix):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name + " where " + \
              column_name + " like " + "'" + value_prefix + "%'"
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def get_all(cls, db_schema, table_name):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "select * from " + db_schema + "." + table_name
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def get_by_value(cls, db_schema, table_name, column_name, value):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()
        if isinstance(value, str):
            value = f"'{str(value)}'"
        else:
            value = str(value)
        sql = "select * from " + db_schema + "." + table_name + " where " + \
              column_name + " = " + value
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def update_by_column(cls, db_schema, table_name, refer_column, refer_value, column_name, value):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "update " + db_schema + "." + table_name + " set " + \
              column_name + " = " + "'" + value + "'" + " where " + refer_column + " = " + refer_value
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def delete_by_column(cls, db_schema, table_name, column_name, value):

        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        sql = "delete from " + db_schema + "." + table_name + " where " + \
              column_name + " = " + value
        print("SQL Statement = " + cur.mogrify(sql, None))

        res = cur.execute(sql)
        res = cur.fetchall()

        conn.close()

        return res

    @classmethod
    def insert(cls, db_schema, table_name, column_name_list, value_list, return_id: bool = False):
        conn = RDBService._get_db_connection()
        cur = conn.cursor()

        columns = ""
        for index, name in enumerate(column_name_list):
            if index != (len(column_name_list) - 1):
                columns = columns + name + ', '
            else:
                columns = columns + name

        values = ""
        for index, value in enumerate(value_list):
            if index != (len(value_list) - 1):
                values = values + "'" + str(value) + "'" + ', '
            else:
                values = values + "'" + str(value) + "'"

        sql = "insert into " + db_schema + "." + table_name + " (" + \
              columns + ") " + " values " + " (" + values + ") "
        print("SQL Statement = " + cur.mogrify(sql, None))
        res = cur.execute(sql)
        if return_id:
            res = cur.lastrowid
        else:
            res = cur.fetchall()
        conn.close()
        return res

    @classmethod
    def get_where_clause_args(cls, template):

        terms = []
        args = []
        clause = None

        if template is None or template == {}:
            clause = ""
            args = None
        else:
            for k, v in template.items():
                terms.append(k + "=%s")
                args.append(v)

            clause = " where " + " AND ".join(terms)

        return clause, args

    @classmethod
    def find_by_template(cls, db_schema, table_name, template, field_list):
        wc, args = RDBService.get_where_clause_args(template)
        conn = RDBService._get_db_connection()
        cur = conn.cursor()
        fields = ', '.join(field_list) if field_list else '*'
        sql = "select {} from ".format(fields) + db_schema + "." + table_name + " " + wc
        res = cur.execute(sql, args=args)
        res = cur.fetchall()
        conn.close()
        return res

    @classmethod
    def create(cls, db_schema, table_name, create_data):

        cols = []
        vals = []
        args = []

        for k, v in create_data.items():
            cols.append(k)
            vals.append('%s')
            args.append(v)

        cols_clause = "(" + ",".join(cols) + ")"
        vals_clause = "values (" + ",".join(vals) + ")"

        sql_stmt = "insert into " + db_schema + "." + table_name + " " + cols_clause + \
                   " " + vals_clause

        res = RDBService.run_sql(sql_stmt, args)
        return res

    @classmethod
    def update_by_template(cls,
                           db_schema: str,
                           table_name: str,
                           template: dict,
                           field_update: dict):
        wc, args = RDBService.get_where_clause_args(template)
        field_clauses, field_vals = [], []
        for k, v in field_update.items():
            field_clauses.append("{} = %s".format(k))
            field_vals.append(v)
        field_update = ", ".join(field_clauses)
        sql = "update {}.{} set {}{}".format(
            db_schema, table_name, field_update, wc)
        return RDBService.run_sql(sql, field_vals + args)