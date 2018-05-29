# -*- coding: utf-8 -*-
# 在PC端使用

from django.shortcuts import render
from django.views import View
from pricer.services.product_service import ProductService
from pricer.services.order_service import OrderService
import urllib.parse as urlparse
from pricer.utils.utils import parse_get_params
import json
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from pricer.utils.my_logger import logger
from pricer.settings import NGINX_PREFIX


class OrderMgmtView(View):
    def __init__(self):
        super(OrderMgmtView, self).__init__()
        self._product_service = ProductService()
        self._order_service = OrderService()
        logger.info('OrderMgmtView::__init__(self)')

    def get(self, request):
        path = request.path
        print(path)
        logger.info(path)

        # PC 查看所有订单
        if '/mgmt/all_orders/' == path:

            orders_df = self._order_service.get_all_orders_df()
            if not orders_df.empty:
                
                # pd.to_html 不截断，但默认的width就被修改了。暂时没有想出更好的办法。
                old_width = pd.get_option('display.max_colwidth')  
                pd.set_option('display.max_colwidth', -1)  

                orders_df = orders_df[::-1]  # order by id desc
                orders_df['详情'] = orders_df['订单编号'].apply(
                    lambda x: '<a href="'+NGINX_PREFIX+'/mgmt/order_detail/?order_id=%d">查看</a>' % x)
#                pd.set_option('display.max_colwidth', old_width)
            return render(request, 'pc/order_list.html',
                          {'data': orders_df.to_html(index=False, escape=False, border=0,classes=['table', 'table-hover'])})

        # PC 查看订单详情
        elif '/mgmt/order_detail/' == path:

            # TODO：请封装为一个函数，放在utils.py中
            # 解析参数
            params = parse_get_params(request)
            order_id = int(params['order_id'][0])

            order_detail_df = self._order_service.get_order_detail_df_by_order_id(order_id)

            # TODO：以下几点可以完善
            # 对 order_detail_df 进行转置，按列排布可能好看点
            # 请把冗余信息单独提出来当到页面上
            old_width = pd.get_option('display.max_colwidth')  
            pd.set_option('display.max_colwidth', -1)  
            return render(request, 'pc/order_detail.html',
                          {'data': order_detail_df.to_html(index=False, escape=False, border=0,
                                                           classes=['table', 'table-hover'])})

