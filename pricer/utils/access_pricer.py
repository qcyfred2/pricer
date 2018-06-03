# -*- coding: utf-8 -*-
import urllib.request
import socket
import winsound
import time
from qcy.windows_utils.win_notify import send_win_msg
from qcy.email_utils.email_utils import send_email
import datetime

headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
timeout = 5
socket.setdefaulttimeout(timeout)


def check_scheduler():
    check_result = True

    t1_str = str(datetime.datetime.now())[:19]
    print(t1_str)
    try:
        req = urllib.request.Request(url='http://123.207.249.51/pricer/mobile/index/', headers=headers)
        data = urllib.request.urlopen(req).read()
        content = data.decode('utf-8')

        if "<title>报价系统</title>" not in content:
            check_result = False
        else:
            print('Pricer - 正常访问 OK')

    except Exception as e:
        print(e)
        check_result = False

    if not check_result:
        winsound.Beep(600, 1000)
        print('Pricer - 不能访问')
        # win32api.MessageBox(None, "无法打开任务管理系统，请检查",
        #                     "任务管理系统", win32con.MB_OK)
        send_win_msg(title='Pricer', msg='网页无法打开')
        send_email(['qcy_1993@126.com', 'liaorx3@chinaunicom.cn'], 'Pricer网页无法访问',
                   'Pricer网页无法访问，请尽快处理', [], [], cc=None)


while 1:
    check_scheduler()
    time.sleep(10)
