# -*- coding: utf-8 -*-
# 引入pricer的路径
import sys

sys.path.append(r'C:\Users\Administrator\Desktop\work\code\pricer\pricer')
from pricer.daos.order_dao import OrderDao
import os
from pricer.constants import CONTRACT_DIR_PATH


def start_task(*args, **kwargs):
    old_folder_dict = {int(x.split('_')[0]): x for x in os.listdir(CONTRACT_DIR_PATH)}

    order_dao = OrderDao()
    df = order_dao.get_all_orders_df()

    new_folder_dict = dict()

    for a, b, c, d in zip(df['订单编号'], df['订单状态'], df['下单时间'], df['单位名称']):
        new_folder_dict[a] = str(a) + '_' + b + '_' + c.strftime('%Y%m%d_%H%M%S') + '_' + d

    for k, v in new_folder_dict.items():
        if k not in old_folder_dict:
            # 新建文件夹
            os.mkdir(CONTRACT_DIR_PATH + v)
        else:
            if old_folder_dict[k] == v:
                pass
            else:
                os.rename(CONTRACT_DIR_PATH + old_folder_dict[k], CONTRACT_DIR_PATH + v)


if __name__ == '__main__':
    start_task()
