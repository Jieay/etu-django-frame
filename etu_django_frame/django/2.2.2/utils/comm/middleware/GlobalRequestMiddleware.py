#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/10 2:36 下午
# @Author  : Jieay
# @File    : GlobalRequestMiddleware.py

import threading
import uuid
from django.utils.deprecation import MiddlewareMixin


threading_local = threading.local()


class GlobalRequestMiddleware(MiddlewareMixin):
    """
    全局request中间件
    """

    def process_request(self, request):
        request.id = self.generate_request_id()
        request.ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
        threading_local.request = request

    @staticmethod
    def generate_request_id():
        return uuid.uuid4().hex[:4]


class GlobalRequest(object):

    def __getattr__(self, item):
        return getattr(getattr(threading_local, 'request', None), item, None)


global_request = GlobalRequest()
