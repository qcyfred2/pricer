# -*- coding: utf-8 -*-

import xlwings as xw
import pandas as pd
import datetime
import pymysql.cursors
from docxtpl import DocxTemplate
import numpy as np
import os
import shutil
import yaml

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'

with open(BASE_DIR + 'settings.yaml') as f:
    setting_str = f.read()
    f.close()
    setting_dict = yaml.load(setting_str)

db_info = setting_dict.get('database')
DB_USER = db_info['user']
DB_PWD = db_info['pwd']
DB_NAME = db_info['db_name']
DB_HOST = db_info['host']
DB_PORT = db_info['port']
DB_CHARSET = db_info['charset']

N_CONTRACT_INFO = 7  # 合同的基本信息行数
BG_COLOR = (198, 224, 180)
N_FORMULAR_RESERVED_COL = 10
N_ALL_ORDERED_PRODUCTS_COL = 12

base_path = os.path.abspath(os.path.dirname(__file__)) + '/'


def get_dt_str():
    dt_str = str(datetime.datetime.now())[:19].replace(
        '-', '').replace(' ', '_').replace(':', '')
    return dt_str


def connect():
    conn = pymysql.Connect(host=DB_HOST, port=DB_PORT, user=DB_USER,
                           passwd=DB_PWD, db=DB_NAME, charset=DB_CHARSET)
    return conn


# 重置单元格颜色 （激活页面才有用）
def reset_color():
    rng_str = 'A2:H1000'
    rng = xw.Range(rng_str)
    rng.color = None


# 设置单元格背景颜色 （第一页）
def set_bg_color(df):
    if len(df) > 0:
        rng_str = 'A2:H%d' % (len(df) + 1)
        rng = xw.Range(rng_str)
        rng.color = BG_COLOR


# 导入第一页的表格
# 若cutoff=True，仅保留前几列，不会修改到Excel中的公式
def import_current_sheet(sht, cutoff_number):
    rng = sht.range('A1').expand('table')
    nrows = rng.rows.count
    ncols = rng.columns.count

    if nrows > 1 and ncols > 1:
        tmp_df = pd.DataFrame(rng.value)
        df = tmp_df.iloc[1:, 0:]
        df.columns = tmp_df.iloc[0, :]
    else:
        raise ValueError('第一页商品为空')

    # 投标报价、单项价格 用excel的公式
    df = df.iloc[:, :cutoff_number]

    return df


# 按产品编号升序排列
def order_by_prod_id():
    reset_color()
    wb = xw.Book.caller()
    sht = wb.sheets[0]
    raw_df = import_current_sheet(sht, N_FORMULAR_RESERVED_COL)
    df = raw_df.sort_values('产品编号', ascending=True)
    sht.range('A2:J1000').value = None
    sht.range('A2').value = df.values


# 已订购商品
def order_by_ordered_prod():
    reset_color()

    wb = xw.Book.caller()
    sht = wb.sheets[0]
    raw_df = import_current_sheet(sht, N_FORMULAR_RESERVED_COL)

    ordered_prod_df = raw_df.query("预定数量>0.5").copy()
    ordered_prod_df.sort_values('产品编号', ascending=True, inplace=True)

    non_ordered_prod_df = raw_df.query("预定数量<0.5").copy()
    non_ordered_prod_df.sort_values('产品编号', ascending=True, inplace=True)

    df = pd.concat([ordered_prod_df, non_ordered_prod_df])

    sht.range('A2:J1000').value = None
    sht.range('A2').value = df.values

    set_bg_color(ordered_prod_df)


# 选择产品类别
def select_prod_type(prod_type):
    reset_color()
    wb = xw.Book.caller()
    sht = wb.sheets[0]
    raw_df = import_current_sheet(sht, N_FORMULAR_RESERVED_COL)

    prod_type_df = raw_df.query("产品类别==@prod_type").copy()
    prod_type_df.sort_values('产品编号', ascending=True, inplace=True)

    other_prod_type_df = raw_df.query("产品类别!=@prod_type").copy()
    other_prod_type_df.sort_values('产品编号', ascending=True, inplace=True)
    df = pd.concat([prod_type_df, other_prod_type_df])

    sht.range('A2:J1000').value = None
    sht.range('A2').value = df.values

    set_bg_color(prod_type_df)


# 获取所有预定产品
def prev_ordered_prod():
    order_by_ordered_prod()

    wb = xw.Book.caller()
    sht = wb.sheets[0]
    raw_df = import_current_sheet(sht, N_ALL_ORDERED_PRODUCTS_COL)

    ordered_prod_df = raw_df.query("预定数量>0.5").copy()
    ordered_prod_df.sort_values('产品编号', ascending=True, inplace=True)

    # print(ordered_prod_df.head())

    sht2 = wb.sheets[1]
    sht2.range('A2').expand('table').value = None
    sht2.range('A2').value = ordered_prod_df.values


# 清除所有订购的产品（慎用）
def reset_order():
    order_by_prod_id()
    wb = xw.Book.caller()
    sht = wb.sheets[0]
    raw_df = import_current_sheet(sht, N_FORMULAR_RESERVED_COL)
    # df = raw_df.copy()
    df = raw_df
    df['预定数量'] = 0
    df['预定年限'] = 0
    # df['单项价格'] = 0

    sht.range('A2:J1000').value = None
    sht.range('A2').value = df.values

    # sheet2
    sht2 = wb.sheets[1]
    sht2.range('A2: L1000').value = None


# 更新xlsm文件（excel第三页，点击更新订单，更新第1页的订单列表）

def update_xlsm_by_order_id(order_id):
    wb = xw.Book.caller()

    conn = connect()
    try:
        sql = """select * from t_product;"""
        prod_df = pd.read_sql(sql, conn)

        sql = """select * from t_order_component where 订单编号 = {order_id};""".format(
            order_id=order_id)
        ordered_prod_df = pd.read_sql(sql, conn)
        df = pd.merge(prod_df[['产品编号', '产品类别', '产品简称', '产品名称', '产品品牌', '规格描述',
                               '投标报价', '报价单位', '产品量词']], ordered_prod_df[['产品编号', '预定数量', '预定年限', '单项价格']],
                      on='产品编号', how='outer').fillna(0)

        # 第一页
        sht = wb.sheets[0]
        # 重置第一页的所有颜色
        rng = sht.range('A2:H1000')
        rng.color = None

        del df['单项价格']
        del df['投标报价']  # excel中的投标报价，由excel的VBA计算得到

        sht.range('A2:J1000').value = None
        sht.range('A2').value = df.values

    except Exception as e:
        print(e)

    finally:
        conn.close()


def get_all_orders():
    conn = connect()
    try:
        sql = """select * from v_orders;"""
        df = pd.read_sql(sql, conn, index_col='订单编号')
    except Exception as e:
        print(e)
    finally:
        conn.close()

    # 第3页
    wb = xw.Book.caller()
    sht = wb.sheets[2]
    sht.range('D1').expand('table').value = None
    sht.range('D1').value = df


# 所有产品
def get_all_prods():
    conn = connect()
    try:
        sql = """SELECT * FROM t_product;"""
        df = pd.read_sql(sql, conn, index_col='产品编号')
    except Exception as e:
        print(e)
    finally:
        conn.close()

    wb = xw.Book.caller()
    sht = wb.sheets[3]
    sht.range('A1').expand('table').value = None
    sht.range('A1').value = df
    # print(df.head())


# 查询所有客户经理的信息
def get_all_admins():
    conn = connect()
    try:
        sql = """SELECT * FROM v_admin;"""
        df = pd.read_sql(sql, conn, index_col='编号')
    except Exception as e:
        print(e)
    finally:
        conn.close()

    wb = xw.Book.caller()
    sht = wb.sheets[4]
    sht.range('A1').expand('table').value = None
    sht.range('A1').value = df


def my_df_to_sql(data_df, conn, cursor, table_name):
    sql = """SHOW COLUMNS FROM {table_name};""".format(table_name=table_name)
    df = pd.read_sql(sql, conn)

    df = df[df['Extra'] != 'auto_increment']

    fields = df.Field.tolist()
    field_str = ','.join(fields)

    data_df = data_df[fields]
    data_mat = data_df.values

    nrow, ncol = data_mat.shape
    value_list = []

    for i in range(nrow):
        row_value_list = []
        for j in range(ncol):
            row_value_list.append("'%s'" % data_mat[i, j])

        value_list.append('(' + ','.join(row_value_list) + ')')

    value_str = ','.join(value_list)

    sql = """insert into {table_name} ({field_str}) values {value_str};""".format(
        table_name=table_name, field_str=field_str, value_str=value_str)
    cursor.execute(sql)


# 更新订单
def update_ordered_prod_in_db(order_id):
    wb = xw.Book.caller()
    sht = wb.sheets[1]  # 从 预览订单 sheet上获取最新订单

    try:
        df = pd.DataFrame(sht.range('A2').expand(
            'table').value, columns=sht.range('A1').expand(
            'right').value)
    except Exception as e:
        print(e)
        print('只有一行，series转df')
        df = pd.DataFrame([sht.range('A2').expand(
            'table').value], columns=sht.range('A1').expand(
            'right').value)

    df['订单编号'] = order_id
    if df.empty:
        print('无任何预定商品，请放弃该订单')
    else:
        conn = connect()
        try:
            with conn.cursor() as cursor:
                sql = """DELETE  FROM t_order_component WHERE 订单编号 = {order_id};""".format(
                    order_id=order_id)
                cursor.execute(sql)

                total_price = df['单项价格'].sum()
                sql = """UPDATE t_order_info SET 订单价格 = {total_price} WHERE 订单编号 = {order_id};""".format(
                    order_id=order_id, total_price=total_price)
                cursor.execute(sql)

                my_df_to_sql(df, conn, cursor, 't_order_component')
            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()


# 生成订单预览的excel（）
def gen_order_detail(order_id):
    wb = xw.Book.caller()
    sht = wb.sheets[1]  # Sheet：订单预览

    try:
        df = pd.DataFrame(sht.range('A2').expand(
            'table').value, columns=sht.range('A1').expand(
            'right').value)
    except Exception as e:
        print(e)
        print('只有一行，series转df')
        df = pd.DataFrame([sht.range('A2').expand(
            'table').value], columns=sht.range('A1').expand(
            'right').value)

    if not df.empty:
        tpl_xlsx_path = base_path + 'prod.xlsx'
        dt_str = get_dt_str()
        new_xlsx_path = base_path + \
            'prod_{order_id}_{dt_str}.xlsx'.format(
                order_id=order_id, dt_str=dt_str)
        shutil.copy(tpl_xlsx_path, new_xlsx_path)

        app = xw.App(visible=False, add_book=False)
        wb = app.books.open(new_xlsx_path)
        sht = wb.sheets[0]
        sht.range('A2').value = df.values

        wb.save()
        wb.close()
        app.quit()


# 生成合同
def gen_contract(order_id, two_or_three):
    wb = xw.Book.caller()
    sht = wb.sheets[5]  # Sheet：生成合同

    if two_or_three == 'two':
        df = pd.DataFrame(sht.range('A3').expand(
            'table').value, columns=['参数名', '参数值'])
    else:
        df = pd.DataFrame(sht.range('G3').expand(
            'table').value, columns=['参数名', '参数值'])

    if len(df) < N_CONTRACT_INFO:
        print('合同信息不全')
    else:
        df.index = df['参数名']
        basic_info = dict(df['参数值'])

        basic_info['价格合计'] = '{:,.2f}'.format(basic_info['价格合计'])

        # 编写doc文档

        if two_or_three == 'two':
            tpl = DocxTemplate(base_path + '政务云两方合同模板.docx')
        else:
            tpl = DocxTemplate(base_path + '政务云三方合同模板.docx')

        col_labels = ['序号', '资源租赁产品名称', '品牌',
                      '单价（元/年/单位）', '数量（单位）', '期限（年）', '小计（元）']
        # 数据从预览订单的sheet中取
        sht = wb.sheets[1]  # Sheet：预览订单
        try:
            ordered_df = pd.DataFrame(sht.range('A2').expand(
                'table').value, columns=sht.range('A1').expand(
                'right').value)
        except Exception as e:
            print(e)
            print('只有一行，series转df')
            ordered_df = pd.DataFrame([sht.range('A2').expand(
                'table').value], columns=sht.range('A1').expand(
                'right').value)

        if ordered_df.empty:
            print('未订产品，不能保存！')
        else:
            ordered_df['序号'] = np.arange(1, len(ordered_df) + 1)
            # print(ordered_df)
            ordered_df = ordered_df[['序号', '产品名称',
                                     '产品品牌', '投标报价', '预定数量', '预定年限', '单项价格']]
            ordered_df['投标报价'] = ordered_df['投标报价'].apply(
                lambda x: '{:,.2f}'.format(x))
            ordered_df['单项价格'] = ordered_df['单项价格'].apply(
                lambda x: '{:,.2f}'.format(x))
            table_data = []
            for idx, row in ordered_df.iterrows():
                table_data.append({'cols': list(row)})

            basic_info['table_data'] = table_data
            basic_info['col_labels'] = col_labels

            tpl.render(basic_info)
            dt_str = get_dt_str()
            tpl.save(
                base_path + '合同_{order_id}_{dt_str}.docx'.format(order_id=order_id, dt_str=dt_str))


# 把合同的基本基本信息存入数据库
def save_contract_basic_info(order_id, two_or_three):
    conn = connect()
    wb = xw.Book.caller()
    sht = wb.sheets[5]  # Sheet：生成合同

    try:
        if two_or_three == 'two':
            df = pd.DataFrame(sht.range('A5').expand(
                'table').value, columns=['参数名', '参数值'])
        else:
            df = pd.DataFrame(sht.range('G5').expand(
                'table').value, columns=['参数名', '参数值'])
        df['订单编号'] = order_id
    except Exception as e:
        print('合同信息不全？')
        print(e)
        return

    if len(df) < N_CONTRACT_INFO:
        print('合同基本信息不全')
    else:
        try:

            with conn.cursor() as cursor:
                sql = """delete from t_contract_info where 订单编号 = {order_id};""".format(
                    order_id=order_id)
                cursor.execute(sql)
                my_df_to_sql(df, conn, cursor, 't_contract_info')

            conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
        finally:
            conn.close()


def get_contract_basic_info(order_id, two_or_three):
    conn = connect()
    wb = xw.Book.caller()
    sht = wb.sheets[5]  # Sheet：生成合同

    try:
        sql = """select * from t_contract_info where 订单编号 = {order_id};""".format(
            order_id=order_id)
        df = pd.read_sql(sql, conn, index_col='订单编号')
        if len(df) < N_CONTRACT_INFO:
            if two_or_three == 'two':
                number_of_params = len(sht.range('A5').expand('down').value)
                sht.range('B5:B%d' % (5+number_of_params-1)).value = '待定'
            else:
                number_of_params = len(sht.range('G5').expand('down').value)
                sht.range('H5:H%d' % (5+number_of_params-1)).value = '待定'
        else:
            if two_or_three == 'two':
                sht.range('A5').expand('table').value = None
                sht.range('A5').value = df.values
            else:
                sht.range('G5').expand('table').value = None
                sht.range('G5').value = df.values
    except Exception as e:
        print(e)
    finally:
        conn.close()
