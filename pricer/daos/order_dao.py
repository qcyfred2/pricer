# -*- coding: utf-8 -*-

from pricer.daos.base_dao import BaseDao
from pricer.constants import TOTAL_PRICE, TOTAL_NUMBER, TOTAL_CATEGORY_NUMBER
import datetime
from pricer.services.product_service import ProductService
import json
from pricer.utils.my_logger import logger


class OrderDao(BaseDao):

    def __init__(self):
        super(OrderDao, self).__init__()

    # 手机网页上查询订单
    def get_all_orders_by_admin_id(self, admin_id):
        if admin_id not in [1, 2, 3, 4]:  # 系统管理员编号
            sql = """SELECT * FROM v_orders WHERE 客户经理编号 = {admin_id};""".format(admin_id=admin_id)
        else:  # 系统管理员能查询所有订单
            sql = """SELECT * FROM v_orders;"""
        df = self.execute_df_query_by_sql(sql, idx_col='订单编号')
        d = dict(df.T)
        for k in d.keys():
            d[k] = dict(d[k])
        return d

    # 获取所有订单
    def get_all_orders_df(self):
        sql = """SELECT * from v_orders;"""
        return self.execute_df_query_by_sql(sql)

    def get_order_by_order_id(self, order_id):
        sql = """select * from v_orders where 订单编号 = {order_id};""".format(
            order_id=order_id)
        df = self.execute_df_query_by_sql(sql, idx_col='订单编号')
        d = dict(df.T)
        for k in d.keys():
            d[k] = dict(d[k])
        return d

    def get_order_detail_by_order_id(self, order_id):
        df = self.get_order_detail_df_by_order_id(order_id, '产品编号')
        return dict(df.T)

    # 获取订单（分页查询）
    def get_orders_by_page_number(self, page_number):  # ??是否需要其他条件
        pass

    # 获取指定一段日期的订单
    def get_orders_by_time(self, query_time):
        return self.execute_df_query_by_t_name('t_order_info', query_time)

    # 获取未处理的订单
    def get_pending_orders(self):
        pass

    # 获取未处理的订单分页？按日期？

    # 根据订单编号查询订单详情
    def get_order_detail_df_by_order_id(self, order_id, idx_col=None):
        # 产品信息、订单详情，封装成dict??
        sql = """
            SELECT
                p.`产品编号`,
                p.`产品类别`,
                p.`产品名称`,
                p.`产品品牌`,
                oc.`预定数量`,
                oc.`预定年限`,
                oc.`单项价格`,
                oc.`产品量词`,
                oc.`投标报价`, # 注意，应该用oc的投标报价，存储的投标报价会随着购买的数量变化。
                p.`报价单位`,
                p.`规格描述`
            FROM
                t_order_component AS oc,
                t_product AS p
            WHERE oc.`产品编号` = p.`产品编号`
                AND oc.`订单编号` = {order_id};
        """.format(order_id=order_id)

        return self.execute_df_query_by_sql(sql, idx_col=idx_col)

    # 修改订单状态
    def update_order_statue_by_order_id(self, order_id, new_statue):
        pass

    # 保存一笔订单
    def save_order(self, order_dict):
        result = True

        try:
            self.connect()
            with self._conn.cursor() as cursor:
                cursor.execute("""set session transaction isolation level REPEATABLE READ;""")

                params = order_dict
                if len(order_dict['cart']) < 4:  # 是3还是4？… -_-!
                    logger.error('购物车错误…')
                    raise ValueError('错误…')

                params['total_price'] = order_dict['cart'][TOTAL_PRICE]
                params['order_datetime'] = str(datetime.datetime.now())[:19]
                params['admin_user'] = order_dict['admin_user']
                params['admin_user_id'] = order_dict['admin_user']['编号']

                sql = """
                        INSERT INTO t_order_info ( 订单状态, 订单价格, 联系人, 联系方式, 电子邮箱, 下单时间, 下单员编号,
                          单位名称 ) VALUES ( '未处理', {total_price}, '{name}', '{tel}', '{email}', 
                          '{order_datetime}', {admin_user_id}, '{organization}') ;""".format(**params)

                cursor.execute(sql)

                #  得到该订单的编号
                sql = """select max(订单编号) from t_order_info;"""
                cursor.execute(sql)
                order_id = cursor.fetchall()[0][0]

                params['order_id'] = order_id

                # 数据存入订单详细表 t_order_component

                cart = params['cart']
                cart.pop(TOTAL_PRICE)
                cart.pop(TOTAL_NUMBER)
                cart.pop(TOTAL_CATEGORY_NUMBER)

                order_cpnt_list = [(k, cart[k]) for k in sorted(cart.keys())]

                prods_dict = ProductService().get_all_prods_dict()

                for oc in order_cpnt_list:
                    prod_id = oc[0]
                    param2 = dict()
                    param2['order_id'] = order_id
                    param2['prod_id'] = prod_id
                    param2['price_unit'] = prods_dict[str(prod_id)]['报价单位']
                    param2['prod_measure_word'] = prods_dict[str(prod_id)]['产品量词']
                    param2 = dict(param2, **json.loads(oc[1]))

                    sql = """ insert into t_order_component ( 订单编号, 产品编号, 预定数量, 预定年限, 投标报价, 报价单位,
                          产品量词, 单项价格 )  values ( {order_id}, {prod_id}, {quantity}, {year}, {unit_price},
                          '{price_unit}', '{prod_measure_word}', {product_price} ) ;""".format(**param2)
                    cursor.execute(sql)

                self.commit()
        except Exception as e:
            logger.error(e)
            result = False
            self.rollback()
        finally:
            self.disconnect()
        return {'res': result, 'order_id': order_id, 'order_info': params}
