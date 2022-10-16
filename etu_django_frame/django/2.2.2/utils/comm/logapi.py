#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/10 2:31 下午
# @Author  : Jieay
# @File    : logapi.py

import logging
import uuid

"""
linux终端下输出带颜色的文字只需在文字前面添加如下格式
\033[显示方式;前景色;背景色m

显示方式	意义
0	终端默认设置
1	高亮显示
4	使用下划线
5	闪烁
7	反白显示
8	不可见

前景色	背景色	颜色
30	40	黑色
31	41	红色
32	42	绿色
33	43	黃色
34	44	蓝色
35	45	紫红色
36	46	青蓝色
37	47	白色
"""
NONE = '\033[0m'
BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = ('\033[0;%dm' % i for i in range(30, 38))


class DefaultServerFormatter(logging.Formatter):
    COLORS = {
        'CRITICAL': RED,
        'ERROR': RED,
        'WARNING': YELLOW,
        'INFO': GREEN,
        'DEBUG': BLUE,
    }

    def __init__(self, *args, **kwargs):
        super(DefaultServerFormatter, self).__init__(*args, **kwargs)

    def format(self, record):
        # region 添加一些其他相关的数据
        try:
            from .middleware.GlobalRequestMiddleware import global_request
            record.user = getattr(global_request.user, 'username', '-----------')
            record.ip = getattr(global_request, 'ip', None) or global_request.META.get('REMOTE_ADDR', None)
            record.request_id = global_request.id
        except Exception as ex:
            record.user = 'NotUser'
            record.ip = 'NotIp'
            record.request_id = uuid.uuid4().hex[:4]
        # endregion

        message = super(DefaultServerFormatter, self).format(record)
        from django.conf import settings
        if record.levelname in self.COLORS and settings.ENVIRONMENT in ('dev', 'test'):
            message = self.COLORS[record.levelname] + message + NONE
        return message