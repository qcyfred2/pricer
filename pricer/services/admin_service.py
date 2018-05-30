# -*- coding: utf-8 -*-
# 本APP使用者的管理

from pricer.daos.admin_dao import AdminDao
from pricer.constants import (ACTIVATE_URL_PREFIX)
from pricer.utils.my_logger import logger
from pricer.utils.email_utils import send_email
import threading


class AdminService:

    def __init__(self):
        self.admin_dao = AdminDao()

    def check_admin(self, u):
        sql = """select * from t_admin where 用户名 = '{name}' and 密码 = `{pwd}` and 激活 = 'y';""".format(
            **u)
        df = self.admin_dao.execute_df_query_by_sql(sql)
        if not df.empty:
            print('登录验证成功')
            return df.T[0].to_dict()
        return None

    def register(self, u):
        u = self.admin_dao.save_admin(u)
        # 如果注册成功，则开启新线程，发送激活邮件
        if u is not None:
            t1 = threading.Thread(
                target=self._send_active_url_email, args=(u,))
            t1.start()
        return u

    def _send_active_url_email(self, u):

        subject = '用户激活_{name}'.format(**u)
        u['activate_url'] = ACTIVATE_URL_PREFIX + \
            '?user_id={user_id}&identify_code={id_code}'.format(**u)

        images = []

        try:
            content = """
                            <b>用户激活</b><br/>
                            客户经理 {name}<br/>
                            登录手机 {tel}<br/>
                            电子邮箱 {email}<br/>
                            点击下面的链接激活（或复制到浏览器地址栏上访问即可）<br/>
                            {activate_url}
                            """.format(**u)
            attachments = []
            receivers = [u['email']]

            logger.info('%d - 发送激活邮箱...' % u['user_id'])
            send_email(receivers, subject, content, images, attachments)
            logger.info('%d - 待激活邮箱发送成功' % u['user_id'])
        except Exception as e:
            logger.info('%d - 待激活邮箱发送失败' % u['user_id'])
            logger.error(e)

    def activate(self, u):
        sql = """select 激活码 from t_admin where 编号 = {user_id};""".format(**u)
        rs = self.admin_dao.execute_query_by_sql(sql)

        if len(rs) > 0:
            if rs[0][0] == u['identify_code']:
                sql = """update t_admin set 激活 = 'y' where 编号 = {user_id}; """.format(
                    **u)
                self.admin_dao.execute_update_by_sql(sql)
                return u
        else:
            return None
