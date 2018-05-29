# -*- coding: utf-8 -*-

from pricer.daos.product_dao import ProductDao
import pandas as pd


class ProductService:

    def __init__(self):
        self._prod_dao = ProductDao()

    def get_all_prods_df(self, idx_col=None):
        return self._prod_dao.get_all_prods(idx_col=idx_col)

    # 把商品df按类别转换为dict， key是类别，value是商品list，list中每个元素是描述该商品的dict
    def cvt_df_grp_type(self, df):
        prod_types = df['产品类别'].unique()

        prods = {}

        for prod_type in prod_types:
            sub_df = df.query('产品类别 == @prod_type')
            items = []
            for i in range(sub_df.shape[0]):
                items.append(dict(sub_df.iloc[i, :]))
            prods[prod_type] = items
        return prods

    # 获取产品列表（js需要的数据）
    def get_all_prods_dict(self, str_idx=True):
        df = self.get_all_prods_df(idx_col='产品编号')
        d = df.T.to_dict()
        return {str(k): v for k, v in d.items()} if str_idx else d

    def calc_prod_item_price(self, prod_df, prod_id, quantity, year):
        px_dict = {}
        prod_name = prod_df.loc[prod_id, '产品名称']

        if (prod_name != 'FC-SAN') and (prod_name != 'IP-SAN'):
            px_dict['unit_price'] = round(prod_df.loc[prod_id, '投标报价'], 2)
            px_dict['product_price'] = round(px_dict['unit_price'] * quantity * year, 2)
        else:
            px_dict['unit_price'] = round(self.calc_storage_price(prod_name, quantity) / quantity, 2)
            px_dict['product_price'] = round(self.calc_storage_price(prod_name, quantity) * year, 2)

        return px_dict

    def calc_storage_price(self, prod_name, n):

        if prod_name == 'FC-SAN':
            return self.FC_SAN_price_100GB(n)
        return self.IP_SAN_price_100GB(n)

    # n个单位存储服务的每年售价， 每个单位 100 GB
    def FC_SAN_price_100GB(self, n):
        return self.FC_SAN_price_TB(n / 10.0)

    def IP_SAN_price_100GB(self, n):
        return self.IP_SAN_price_TB(n / 10.0)

    def FC_SAN_price_TB(self, n):
        if n <= 10:
            return 8000 * n
        if n <= 50:
            return self.FC_SAN_price_TB(10) + (n - 10) * 7200

        return self.FC_SAN_price_TB(50) + (n - 50) * 6500

    def IP_SAN_price_TB(self, n):
        if n <= 10:
            return 3300 * n
        if n <= 50:
            return self.IP_SAN_price_TB(10) + (n - 10) * 3100
        return self.IP_SAN_price_TB(50) + (n - 50) * 2980
