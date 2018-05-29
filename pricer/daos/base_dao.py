# -*- coding: utf-8 -*-

import pandas as pd
from pricer.utils.my_logger import logger
import pymysql.cursors
from pricer.constants import DB_HOST, DB_PORT, DB_USER, DB_PWD, DB_NAME, DB_CHARSET


class BaseDao:
    def __init__(self):
        self._conn = None

    def connect(self):
        self._conn = pymysql.Connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            passwd=DB_PWD,
            db=DB_NAME,
            charset=DB_CHARSET)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def disconnect(self):
        self._conn.close()

    def execute_update_by_sql(self, sql):

        try:
            self.connect()
            with self._conn.cursor() as cursor:
                cursor.execute(sql)
                self.commit()
        except Exception as e:
            logger.error(sql)
            logger.error(e)
            self.rollback()
        finally:
            self.disconnect()

    def execute_query_by_sql(self, sql):
        rs = None
        try:
            self.connect()
            with self._conn.cursor() as cursor:
                cursor.execute(sql)
                rs = cursor.fetchall()
        except Exception as e:
            logger.error(sql)
            logger.error(e)
        finally:
            self.disconnect()
        return rs

    def execute_df_query_by_t_name(self, table_name, idx_col=None):
        df = None
        sql = """select * from {table_name}""".format(table_name=table_name)
        try:
            self.connect()
            if idx_col is None:
                df = pd.read_sql(sql, self._conn)
            else:
                df = pd.read_sql(sql, self._conn, index_col=idx_col)
        except Exception as e:
            logger.error(sql)
            logger.error(e)
        finally:
            self.disconnect()

        return df

    def execute_df_query_by_sql(self, sql, idx_col=None):

        df = None
        try:
            self.connect()
            if idx_col is None:
                df = pd.read_sql(sql, self._conn)
            else:
                df = pd.read_sql(sql, self._conn, index_col=idx_col)
        except Exception as e:
            logger.error(sql)
            logger.error(e)
        finally:
            self.disconnect()

        return df
