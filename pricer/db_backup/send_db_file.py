import os
import datetime
from qcy.email_utils.email_utils import send_email


def start_task(*args, **kwargs):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/db_backup/zip/'

    files = [x for x in os.listdir(base_dir) if x != '__init__.py']
    new_file = files[-1]

    sql_path = base_dir + new_file
    send_email(receivers=['qcy_1993@126.com', 'liaorx3@chinaunicom.cn'], subject='数据库备份',
               content='%s<br/>数据库SQL文件' % str(datetime.datetime.now()), images=[], attachments=[sql_path],
               cc=None)


if __name__ == '__main__':
    start_task()
