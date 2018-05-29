# -*- coding: utf-8 -*-
# 已修正 pymysql

from pricer.daos.base_dao import BaseDao


class ProductDao(BaseDao):
    def __init__(self):
        super(ProductDao, self).__init__()

    # 获取所有产品
    def get_all_prods(self, idx_col=None):
        return self.execute_df_query_by_t_name('t_product', idx_col=idx_col)
