# -*- coding: utf-8 -*-

from pricer.daos.order_dao import OrderDao
from pricer.daos.product_dao import ProductDao
import pandas as pd
from pricer.constants import (ORDER_OUTPUT_XLSX_DIR_PATH,
                              ORDER_OUTPUT_XLSX_DIR_PATH,
                              ORDER_XLSX_TEMPLATE,
                              RECEIVERS)
import shutil
import xlwings as xw
from pricer.utils.email_utils import send_email
import pythoncom
import threading
import datetime
from pricer.utils.my_logger import logger


class OrderService:

    def __init__(self):
        self._order_dao = OrderDao()
        self._product_dao = ProductDao()

    def get_all_orders_by_admin_id(self, admin_id):
        return self._order_dao.get_all_orders_by_admin_id(admin_id)

    # 网页上显示table
    def get_all_orders_df(self):
        return self._order_dao.get_all_orders_df()
    # 网页上显示table

    def get_order_detail_df_by_order_id(self, order_id):
        return self._order_dao.get_order_detail_df_by_order_id(order_id)

    # 网页通过ajax下单，成功后，将得到order_id，ajax success重定向到order_result
    def get_order_result(self, order_id):
        order_info = self._order_dao.get_order_by_order_id(order_id)
        # order_cpnt = self._order_dao.get_order_detail_by_order_id(order_id)
        order_cpnt_df = self._order_dao.get_order_detail_df_by_order_id(
            order_id)
        return {'order_info': order_info, 'order_cpnt_df': order_cpnt_df}

    def save_order(self, order_dict):
        # 1. 保存至数据库
        res_dict = self._order_dao.save_order(order_dict=order_dict)

        res = res_dict.get('res', False)  # 结果

        if res:
            # 2. 开启新线程，生成excel，发送邮件。主线程返回，以免等待时间过长…
            order_id = res_dict.get('order_id')
            order_info = res_dict.get('order_info')

            t1 = threading.Thread(
                target=self._save_xlsx_send_mail, args=(order_id, order_info))
            t1.start()

        else:
            logger.error('订单保存失败')

        return res_dict

    def _save_xlsx_send_mail(self, order_id, order_info):

        # 1. 生成Excel订单
        try:
            logger.info('正在保存订单excel文件')
            self._save_xlsx(order_id)
            logger.info('订单excel文件保存成功')
        except Exception as e:
            logger.info('订单excel文件保存失败 %d' % order_id)
            logger.error(e)

        # 2. 发送邮件
        try:
            logger.info('正在发送邮件')
            self._send_email_order_xlsx(order_id, order_info)
        except Exception as e:
            logger.error('邮件发送失败 %d' % order_id)
            logger.error(e)

    def _save_xlsx(self, order_id):
        prod_df = self._product_dao.get_all_prods()
        ordered_prod_df = self._order_dao.get_order_detail_df_by_order_id(
            order_id)

        # TODO: 检查，fillna应该是0，还是用 ''??
        # 用'' 要报错……
        df_to_gen_xlsx = pd.merge(prod_df[['产品编号', '产品类别', '产品简称', '产品名称', '产品品牌', '规格描述',
                                           '投标报价', '报价单位', '产品量词']], ordered_prod_df[['产品编号', '预定数量', '预定年限', '单项价格']],
                                  on='产品编号', how='outer').fillna(0)

        # 修改 df_to_gen_xlsx 的存储服务的投标报价（总价 / 数量 / year）
        storage_df_idx = df_to_gen_xlsx.query("产品类别 == '存储服务'").index
        df_to_gen_xlsx.loc[storage_df_idx, '投标报价'] = df_to_gen_xlsx.loc[storage_df_idx, '单项价格'] \
            / df_to_gen_xlsx.loc[storage_df_idx, '预定数量'] \
            / df_to_gen_xlsx.loc[storage_df_idx, '预定年限']

        new_xlsx_name = 'order_{order_id}.xlsx'.format(order_id=order_id)
        new_xlsx_path = ORDER_OUTPUT_XLSX_DIR_PATH + new_xlsx_name

        self.new_xlsx_path = new_xlsx_path

        shutil.copy(ORDER_XLSX_TEMPLATE, new_xlsx_path)

        # 生成excel
        pythoncom.CoInitialize()  # 如果没有这句话，报错，尚未调用 CoInitialize…

        app = xw.App(visible=False, add_book=False)
        wb = app.books.open(new_xlsx_path)

        sht = wb.sheets[0]
        ordered_prod_df = df_to_gen_xlsx.query("预定数量>0.5").copy()
        ordered_prod_df.sort_values('产品编号', ascending=True, inplace=True)
        ordered_prod_df = ordered_prod_df[sht.range(
            'A1').expand('right').value]
        sht.range('A2').value = ordered_prod_df.values

        wb.save()
        wb.close()
        app.quit()

    # 这些参数应该从成员变量里面取…
    def _send_email_order_xlsx(self, order_id, order_info):
        subject = '新订单_{organization}_{order_id}'.format(**order_info)
        images = []

        try:
            content = """
                    <b>尊敬的客户：</b><br/><br/>
                    您好！<br/>
                    您提交的订单我们已收到，我们将尽快与您联系！<br/>
                    祝您工作顺利、生活愉快！
                    <br/><br/>
                    <b>中国联通广州市分公司</b><br/>
                    <b>{today_yyyymmdd}</b><br/><br/>

                    <b>政务云订单</b><br/>
                    订单编号 {order_id}<br/>
                    单位名称 {organization}<br/>
                    联系人 {name}<br/>
                    联系方式 {tel}<br/>
                    电子邮箱 {email}<br/>
                    订单金额 {total_price}<br/>
                    下单时间 {order_datetime}<br/>
                    注：因小数点精度限制，实际价格可能有所出入；许可等产品的预定期限，请以最终合同为准。<br/><br/>
                    
                    <b>自动邮件，请勿回复</b>
                    """.format(order_id=order_id, name=order_info['name'], tel=order_info['tel'],
                               email=order_info['email'], total_price=order_info['total_price'],
                               order_datetime=order_info['order_datetime'],
                               organization=order_info['organization'],
                               today_yyyymmdd=str(datetime.datetime.now())[:10])
            attachments = [self.new_xlsx_path]

            cc_addrs = list(
                set([order_info['admin_user']['电子邮箱']] + RECEIVERS))

            # 发给客户，抄给客户经理（和我，但是126邮箱自己抄给自己收不到……）
            send_email([order_info['email']], subject, content,
                       images, attachments, cc=cc_addrs)
            # 发给管理员和客户经理 （为什么抄送发送不成功）
            send_email(cc_addrs, subject, content,
                       images, attachments, cc=None)
            logger.info('订单确认邮件发送成功')
        except Exception as e:
            logger.error('订单确认邮件发送失败')
            logger.error(e)
