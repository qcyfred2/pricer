# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from pandas import DataFrame, Series

from pricer import engine

df = pd.read_excel('填表_2018年5月20日191238.xlsx', index_col='产品编号')
print(df)
df.to_sql('t_product', engine, index=False, if_exists='append')
