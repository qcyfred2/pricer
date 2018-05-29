# -*- coding: utf-8 -*-
# 本应用中的常量
from pricer.settings import BASE_DIR


# 邮箱设置
SENDER = ''
RECEIVERS = ['']  # 管理员邮箱
USERNAME = ''
PASSWORD = ''
SMTP_SERVER = ''


APP_NAME = 'pricer'

# 激活时的url前缀
# 注意nginx…
ACTIVATE_URL_PREFIX = ''


# 订单模板
# excel文件
ORDER_XLSX_TEMPLATE = '{base_dir}/{app_name}/excel_template/prod.xlsx'.format(base_dir=BASE_DIR, app_name=APP_NAME)
# 生成的订单保存路径
ORDER_OUTPUT_XLSX_DIR_PATH = '{base_dir}/{app_name}/output_xlsx/'.format(base_dir=BASE_DIR, app_name=APP_NAME)

# 日志输出文件
LOG_PATH = '{base_dir}/{app_name}/logs/pricer.txt'.format(base_dir=BASE_DIR, app_name=APP_NAME)

# MySQL数据库

DB_USER = ''
DB_PWD = ''
DB_NAME = ''
DB_HOST = ''
DB_PORT = 3306
DB_CHARSET = 'utf8'

DB_URL_INFO = 'mysql+pymysql://%(user)s:%(password)s@%(host)s:%(port)d/%(database)s?charset='+DB_CHARSET
DB_INFO = {'user': DB_USER,
           'password': DB_PWD,
           'host': DB_HOST,
           'database': DB_NAME,
           'port': DB_PORT}


# Session 过期时间
SESSION_EXPIER_TIME = 60 * 60 * 24 * 365

# 购物车中的Key，这么做纯粹是为了迎合存在sqlite中的session的key全变成了str型
TOTAL_PRICE = -1  # 总价
TOTAL_CATEGORY_NUMBER = -2  # 类别总数
TOTAL_NUMBER = -3  # 小件总数

# 初始化购物车
INIT_CART = dict()
INIT_CART[TOTAL_PRICE] = 0
INIT_CART[TOTAL_NUMBER] = 0
INIT_CART[TOTAL_CATEGORY_NUMBER] = 0
