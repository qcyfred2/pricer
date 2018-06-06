from pricer.daos.order_dao import OrderDao
import os
from pricer.constants import CONTRACT_DIR_PATH


old_folder_dict = {int(x.split('_')[0]): x for x in os.listdir(CONTRACT_DIR_PATH)}

order_dao = OrderDao()
df = order_dao.get_all_orders_df()

new_folder_dict = dict()

for x, y in zip(df['订单编号'], df['单位名称']):
    new_folder_dict[x] = str(x) + '_' + y

for k, v in new_folder_dict.items():
    if k not in old_folder_dict:
        # 新建文件夹
        os.mkdir(CONTRACT_DIR_PATH + v)
    else:
        os.rename(CONTRACT_DIR_PATH + old_folder_dict[k], CONTRACT_DIR_PATH + v)
