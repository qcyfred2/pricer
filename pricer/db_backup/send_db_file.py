import os
from pricer.utils.email_utils import send_email
import time
import datetime
from pricer.constants import RECEIVERS

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/db_backup/zip/'

while 1:

    now_str = str(datetime.datetime.now())[:19].split(' ')[1]

    if now_str == '22:10:00':
        files = [x for x in os.listdir(base_dir) if x != '__init__.py']
        new_file = files[-1]

        sql_path = base_dir + new_file
        send_email(receivers=RECEIVERS, subject='数据库备份',
                   # send_email(receivers=['qcy_1993@126.com'], subject='数据库备份',
                   content='%s<br/>数据库SQL文件' % str(datetime.datetime.now()), images=[], attachments=[sql_path],
                   cc=None)

        time.sleep(1)
