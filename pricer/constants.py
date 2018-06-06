# -*- coding: utf-8 -*-
# 本应用中的常量
from pricer.settings import BASE_DIR
from pricer import setting_dict


# 邮箱设置
email_info = setting_dict.get('email')
SENDER = email_info['sender']
RECEIVERS = email_info['receivers']  # 管理员邮箱
USERNAME = email_info['username']
PASSWORD = email_info['password']
SMTP_SERVER = email_info['smtp_server']


app_info = setting_dict.get('app_info')
APP_NAME = app_info.get('app_name')
app_host = app_info.get('app_host')

# 激活时的url前缀
# 注意nginx…
ACTIVATE_URL_PREFIX = 'http://{host}/{app_name}/mobile/activate/'.format(
    host=app_host, app_name=APP_NAME)

# 合同文件夹路径
CONTRACT_DIR_PATH = setting_dict.get('contract_info').get('path')

# 订单模板
# excel文件
ORDER_XLSX_TEMPLATE = '{base_dir}/{app_name}/excel/prod.xlsx'.format(
    base_dir=BASE_DIR, app_name=APP_NAME)
# 生成的订单保存路径
ORDER_OUTPUT_XLSX_DIR_PATH = '{base_dir}/{app_name}/excel/output/'.format(
    base_dir=BASE_DIR, app_name=APP_NAME)

# 日志输出文件
LOG_PATH = '{base_dir}/{app_name}/logs/pricer.txt'.format(
    base_dir=BASE_DIR, app_name=APP_NAME)

# MySQL数据库
db_info = setting_dict.get('database')
DB_USER = db_info['user']
DB_PWD = db_info['pwd']
DB_NAME = db_info['db_name']
DB_HOST = db_info['host']
DB_PORT = db_info['port']
DB_CHARSET = db_info['charset']


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
