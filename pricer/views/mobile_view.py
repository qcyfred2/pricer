# -*- coding: utf-8 -*-
# 网页端下单

from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.views import View
from pricer.services.product_service import ProductService
from pricer.services.admin_service import AdminService
from pricer.services.order_service import OrderService
import urllib.parse as urlparse
from pricer.utils.utils import parse_get_params, get_session_cart
import json
from pricer.constants import TOTAL_PRICE, TOTAL_CATEGORY_NUMBER, TOTAL_NUMBER, INIT_CART, SESSION_EXPIER_TIME
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from pricer.settings import NGINX_PREFIX
from pricer.utils.my_logger import logger
import uuid


class MobileView(View):
    def __init__(self):
        super(MobileView, self).__init__()
        self._prod_serv = ProductService()
        self._order_serv = OrderService()
        self._admin_serv = AdminService()
        logger.info('MobileView::__init__(self)')

    def get(self, request):
        path = request.path
        logger.info('GET: '+path)

        # 查看产品列表
        if '/mobile/all_products/' == path:

            all_prods_df = self._prod_serv.get_all_prods_df()
            prods_html_data = self._prod_serv.cvt_df_grp_type(all_prods_df)
            prods_js_data = self._prod_serv.get_all_prods_dict()
            try:
                cart = get_session_cart(request)
                js_data = {'result': 1, 'cart': cart,
                           'prods_js_data': prods_js_data}
                html_data = {'result': 1, 'prods_html_data': prods_html_data}
            except Exception as e:
                logger.error(e)
            return render(request, 'mobile/product_list.html', {'js_data': json.dumps(js_data),
                                                                'html_data': html_data})

        # 手机上操作（增加、减少、删除、选中），此函数由ajax调用
        elif '/mobile/update_cart/' == path:

            try:
                request.session.set_expiry(SESSION_EXPIER_TIME)
                params = parse_get_params(request)
                product_id = int(params['product_id'][0])
                quantity = int(params['quantity'][0])
                year = int(params['year'][0])

                prod_df = self._prod_serv.get_all_prods_df(idx_col='产品编号')

                cart = get_session_cart(request)

                # if 数量为0，就把该商品从cart中去掉，并更新session
                # else， 查询所有商品的价格，计算价格（单项 & 购物车中所有商品的价格）
                if quantity > 0.5:  # 数量大于零

                    px_dict = self._prod_serv.calc_prod_item_price(prod_df, product_id, quantity, year)

                    item = {'product_id': product_id,
                            'quantity': quantity,
                            'unit_price': px_dict.get('unit_price', 0),
                            'product_price': px_dict.get('product_price', 0),
                            'year': year, }
                    cart[product_id] = json.dumps(item)
                else:  # 数量等于0
                    if product_id in cart:  # cart中本来有这个商品
                        cart.pop(product_id)  # remove

                # 订单总价
                # cart的key大于0的那些value，才是商品。有几个常量小于0。
                total_price = sum([json.loads(k2)['product_price']
                                   for k2 in [cart[k] for k in cart.keys() if k > 0]])
                total_number = sum([json.loads(k2)['quantity'] for k2 in [
                    cart[k] for k in cart.keys() if k > 0]])
                cart[TOTAL_PRICE] = total_price
                cart[TOTAL_NUMBER] = total_number
                cart[TOTAL_CATEGORY_NUMBER] = max(len(cart) - 3, 0)  # 减掉几个不是“已订商品”的key
                request.session['cart'] = json.dumps(cart)
                result_data = {'result': 1, 'cart': cart}
            except Exception as e:
                logger.error(e)
                result_data = {'result': 0}

            # 返回JSON，内含当前购物车中商品的id、数量、单价、总价等信息
            return HttpResponse(json.dumps(result_data))

        # 清空订单（此函数由ajax调用）
        elif '/mobile/clear_cart/' == path:
            try:
                cart = INIT_CART
                request.session['cart'] = json.dumps(cart)  # 更新session的cart
                result_data = {'result': 1, 'cart': cart}
            except Exception as e:
                logger.error(e)
                result_data = {'result': 0}

            return HttpResponse(json.dumps(result_data))

        # 进入订单预览页面
        elif '/mobile/preview_order/' == path:

            # 全部商品
            all_prods_df = self._prod_serv.get_all_prods_df()
            all_prods_df.index = all_prods_df['产品编号']

            # session 已购商品
            cart = get_session_cart(request)
            # cart是dict。但因为django的session比较弱，key和value只能存int或str
            # 所以，以 prod_id 为key的那些value，本来是dict结果，但存在session中，只能存成str
            # 因此，后面需要json.loads
            ordered_prod_df = all_prods_df.loc[[
                k for k in cart.keys() if k > 0]]
            ordered_prod_df['预订数量'] = ordered_prod_df['产品编号'].apply(
                lambda x: json.loads(cart[x])['quantity'])
            ordered_prod_df['预定年限'] = ordered_prod_df['产品编号'].apply(
                lambda x: json.loads(cart[x])['year'])
            ordered_prod_df['预定价格'] = ordered_prod_df['产品编号'].apply(
                lambda x: json.loads(cart[x])['product_price'])
            ordered_prod_df_grp_type = self._prod_serv.cvt_df_grp_type(
                ordered_prod_df)

            cart['total_price'] = cart[TOTAL_PRICE]
            cart['total_number'] = cart[TOTAL_NUMBER]

            js_data = dict()
            js_data['cart'] = cart

            result_data = {'cart': cart,
                           'prods_html_data': ordered_prod_df_grp_type,
                           'js_data': json.dumps(js_data)}
            return render(request, 'mobile/preview_order.html', {'data': result_data})

        # 进入填写客户信息的页面
        elif '/mobile/input_customer_info/' == path:
            return render(request, 'mobile/input_customer_info.html')

        elif '/mobile/save_order/' == path:
            logger.warning('GET提交，保存订单，可能是由于浏览器刷新所致')  # 浏览器刷新！
            return HttpResponseRedirect(NGINX_PREFIX + '/mobile/all_products/')  # 跳转到主界面

        # 新用户输入信息注册
        elif '/mobile/input_register/' == path:
            return render(request, 'mobile/register.html')

        # 选择登录 or 注册
        elif '/mobile/index/' == path:
            return render(request, 'mobile/index.html')

        # 用户通过点击发送到邮箱的链接激活
        elif '/mobile/activate/' == path:
            params = parse_get_params(request)
            user_id = int(params['user_id'][0])
            identify_code = params['identify_code'][0]

            u = self._admin_serv.activate({'user_id': user_id, 'identify_code': identify_code})
            if u is not None:
                logger.info('激活成功 ' + json.dumps(u))
                return HttpResponse('<h1>激活成功！<h1>')
            else:
                return HttpResponse('用户激活失败，请联系廖润雪。')

        # 网页上点击“登录”按钮后，先判断是否登录
        # TODO: 已经用了filter对身份进行验证，这个分支是否可以考虑不写？
        elif '/mobile/pre_login/' == path:
            admin_user_str = request.session.get('admin_user', None)
            if admin_user_str is None:
                result = 0
            else:
                result = 1
            return HttpResponse(json.dumps({'result': result}))

        elif '/mobile/login/' == path:
            return render(request, 'mobile/login.html')
        
        elif '/mobile/all_orders/' == path:
            admin_user_str = request.session['admin_user']
            admin_user = json.loads(admin_user_str)
            orders_dict = self._order_serv.get_all_orders_by_admin_id(admin_user['编号'])
            return render(request, 'mobile/order_list.html', {'data': orders_dict})

        elif '/mobile/order_result/' == path:
            params = parse_get_params(request)
            order_id = int(params['order_id'][0])
            result_data = self._order_serv.get_order_result(order_id)
            order_cpnt_df = result_data['order_cpnt_df']
            order_cpnt_df_grp_type = self._prod_serv.cvt_df_grp_type(
                order_cpnt_df)
            result_data['order_cpnt_df'] = order_cpnt_df_grp_type
            return render(request, 'mobile/order_result.html', {'data': result_data})

        elif '/mobile/my_info/' == path:
            admin_user_str = request.session['admin_user']
            admin_user = json.loads(admin_user_str)
            return render(request, 'mobile/my_info.html', {'data': admin_user})

        else:
            logger.warning('404')
            return HttpResponseRedirect(NGINX_PREFIX + '/mobile/index/')

    def post(self, request):
        path = request.path
        logger.info('POST: '+path)

        # 手机保存订单
        if '/mobile/save_order/' == path:
            admin_user_str = request.session['admin_user']
            admin_user = json.loads(admin_user_str)
            order_dict = dict()
            order_dict['admin_user'] = admin_user
            order_dict['tel'] = request.POST.get('tel', '')
            order_dict['name'] = request.POST.get('name', '')
            order_dict['email'] = request.POST.get('email', '')
            order_dict['organization'] = request.POST.get('organization', '')

            cart = get_session_cart(request)
            order_dict['cart'] = cart

            res = False
            if len(cart) > 3:  # 大于3是因为cart中，始终有3个变量（总价格，总件数，类别数）
                # service 保存订单
                res_dict = self._order_serv.save_order(order_dict=order_dict)
                res = res_dict.get('res', False)

            if res:
                # 全部商品
                all_prods_df = self._prod_serv.get_all_prods_df()
                all_prods_df.index = all_prods_df['产品编号']

                # session 已购
                cart = get_session_cart(request)
                ordered_prod_df = all_prods_df.loc[[
                    k for k in cart.keys() if k > 0]]
                ordered_prod_df['预订数量'] = ordered_prod_df['产品编号'].apply(
                    lambda x: json.loads(cart[x])['quantity'])
                ordered_prod_df['预定年限'] = ordered_prod_df['产品编号'].apply(
                    lambda x: json.loads(cart[x])['year'])
                ordered_prod_df['预定价格'] = ordered_prod_df['产品编号'].apply(
                    lambda x: json.loads(cart[x])['product_price'])
                ordered_prod_df_grp_type = self._prod_serv.cvt_df_grp_type(
                    ordered_prod_df)

                cart['total_price'] = cart[TOTAL_PRICE]
                cart['total_number'] = cart[TOTAL_NUMBER]

                result_data = {'cart': cart,
                               'prods_html_data': ordered_prod_df_grp_type,
                               'order_info': res_dict.get('order_info'),
                               'js_data': json.dumps({'cart': cart})}

                if 'cart' in request.session.keys():
                    del request.session['cart']  # 成功保存到数据库，则清除cart
                return HttpResponse(json.dumps({'result': 1, 'order_id': int(res_dict['order_id'])}))

            else:
                logger.info('订单保存失败 ' + admin_user_str)

                # 应该返回结果，然后用js重定向……
                return HttpResponse(json.dumps({'result': 0}))

        # 对新用户输入信息进行校验
        elif '/mobile/register/' == path:
            user_dict = dict()
            user_dict['tel'] = request.POST.get('tel', '')
            user_dict['name'] = request.POST.get('name', '')
            user_dict['email'] = request.POST.get('email', '')
            user_dict['id_code'] = uuid.uuid1().hex
            user_dict['pwd'] = user_dict['tel'][-4:]

            # TODO: 应该对输入进行校验
            # TODO: 数据库，用户名，要加唯一索引！
            u = self._admin_serv.register(user_dict)
            if u is not None:
                logger.info('新用户注册成功 ' + json.dumps(u))
                return HttpResponse(json.dumps({'result': 1}))
            else:
                logger.info('新用户注册失败 ' + json.dumps(user_dict))
                return HttpResponse(json.dumps({'result': 0}))

        # 用户输入用户名、密码以后的登录验证
        elif '/mobile/login/' == path:
            user_dict = dict()
            user_dict['name'] = request.POST.get('name', '')
            user_dict['pwd'] = request.POST.get('pwd', '')
            u = self._admin_serv.check_admin(user_dict)

            if u is not None:
                # session, 登录成功，跳转
                request.session.set_expiry(SESSION_EXPIER_TIME)
                request.session['admin_user'] = json.dumps(u)
                logger.info('登录成功 ' + request.session['admin_user'])
                return HttpResponse(json.dumps({'result': 1}))
            else:
                logger.info('登录失败 ' + json.dumps(user_dict))
                return HttpResponse(json.dumps({'result': 0}))

        else:
            logger.warning('404')
            return HttpResponseRedirect('/mobile/all_products/')  # 302 临时重定向

