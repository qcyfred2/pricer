# -*- coding: utf-8 -*-

from pricer.daos.base_dao import BaseDao
from pricer.utils.my_logger import logger
import datetime


class AdminDao(BaseDao):

    def __init__(self):
        super(AdminDao, self).__init__()

    def get_admin_info_by_id(self, admin_id):
        sql = """
            SELECT
              a.`编号`,
              a.`登录名`,
              a.`姓名`,
              a.`电子邮箱`,
              a.`联系方式`
            FROM
              t_admin AS a
            WHERE a.`编号` = {admin_id} ;
        """.format(admin_id=admin_id)
        return self.execute_df_query_by_sql(sql)

    def get_admin_ids(self):
        sql = """SELECT 编号 FROM t_admin ;"""
        return self.execute_df_query_by_sql(sql)

    def save_admin(self, u):

        # 事务…
        try:
            u['reg_datetime'] = str(datetime.datetime.now())[:19]
            self.connect()
            with self._conn.cursor() as cursor:
                cursor.execute(
                    """set session transaction isolation level REPEATABLE READ;""")
                sql = """insert into t_admin (用户名, 密码, 姓名, 电子邮箱, 联系方式, 激活码, 激活, 注册时间) values 
                 ('{tel}', '{pwd}', '{name}', '{email}', '{tel}', '{id_code}', 'n', '{reg_datetime}');""".format(**u)
                cursor.execute(sql)

                sql = """select * from t_admin where 编号 = (select max(编号) from t_admin);"""
                cursor.execute(sql)
                user_id = cursor.fetchall()[0][0]
                u['user_id'] = user_id

                self.commit()
        except Exception as e:
            u = None
            logger.error(e)
            self.rollback()
            # send.email # new thread
        finally:
            self.disconnect()

        return u

    def active_admin(self, u):
        pass
