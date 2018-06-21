# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from sqlalchemy import create_engine

DB_USER = ''
DB_PWD = ''
DB_NAME = ''
DB_HOST = ''
DB_PORT = 3800
DB_CHARSET = 'utf8'

DB_URL_INFO = 'mysql+pymysql://%(user)s:%(password)s@%(host)s:%(port)d/%(database)s?charset='+DB_CHARSET
DB_INFO = {'user': DB_USER,
           'password': DB_PWD,
           'host': DB_HOST,
           'database': DB_NAME,
           'port': DB_PORT}

engine = create_engine(DB_URL_INFO % DB_INFO)

df = pd.read_excel(r'D:\code\zdy\pricer\填表_2018年5月21日1104.xlsx', index_col='产品编号')


df.to_sql('t_product', engine, if_exists='append', index=False)
