#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 17:42
# @Author  : Jieay
# @File    : exception_handler.py
from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.views import exception_handler

import logging
logger = logging.getLogger(__name__)


def CustomBaseExceptionHandler(exc, context):
    """自定义异常返回"""

    detail_msg = str(exc)
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    if response is None:
        # 自定义数据异常，response 为空的时候返回报错信息
        data = {
            'msg': {
                'detail': detail_msg,
                'error': '数据异常'
            },
            'data': [],
            'code': 507
        }
        data_list = [
            ('status', False),
            ('code', data.get('code')),
            ('msg', data.get('msg')),
            ('data', data.get('data'))
        ]
        logger.info('Custom Exception: {}'.format(data_list))
        return Response(OrderedDict(data_list))

    # Now add the HTTP status code to the response.
    if response is not None:
        logger.info('exception_handler: {}'.format(response))
        exception_error_msg = '{}'.format(response.data)
        logger.info('exception_error: {}'.format(exception_error_msg))
        response.data.clear()
        response.data['status'] = False
        response.data['code'] = response.status_code
        response.data['data'] = []

        http_error_status_code = {
            400: "HTTP_400_BAD_REQUEST",
            401: "HTTP_401_UNAUTHORIZED",
            402: "HTTP_402_PAYMENT_REQUIRED",
            403: "HTTP_403_FORBIDDEN",
            404: "HTTP_404_NOT_FOUND",
            405: "HTTP_405_METHOD_NOT_ALLOWED",
            406: "HTTP_406_NOT_ACCEPTABLE",
            407: "HTTP_407_PROXY_AUTHENTICATION_REQUIRED",
            408: "HTTP_408_REQUEST_TIMEOUT",
            409: "HTTP_409_CONFLICT",
            410: "HTTP_410_GONE",
            411: "HTTP_411_LENGTH_REQUIRED",
            412: "HTTP_412_PRECONDITION_FAILED",
            413: "HTTP_413_REQUEST_ENTITY_TOO_LARGE",
            414: "HTTP_414_REQUEST_URI_TOO_LONG",
            415: "HTTP_415_UNSUPPORTED_MEDIA_TYPE",
            416: "HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE",
            417: "HTTP_417_EXPECTATION_FAILED",
            422: "HTTP_422_UNPROCESSABLE_ENTITY",
            423: "HTTP_423_LOCKED",
            424: "HTTP_424_FAILED_DEPENDENCY",
            428: "HTTP_428_PRECONDITION_REQUIRED",
            429: "HTTP_429_TOO_MANY_REQUESTS",
            431: "HTTP_431_REQUEST_HEADER_FIELDS_TOO_LARGE",
            451: "HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS",
            500: "HTTP_500_INTERNAL_SERVER_ERROR",
            501: "HTTP_501_NOT_IMPLEMENTED",
            502: "HTTP_502_BAD_GATEWAY",
            503: "HTTP_503_SERVICE_UNAVAILABLE",
            504: "HTTP_504_GATEWAY_TIMEOUT",
            505: "HTTP_505_HTTP_VERSION_NOT_SUPPORTED",
            507: "HTTP_507_INSUFFICIENT_STORAGE",
            511: "HTTP_511_NETWORK_AUTHENTICATION_REQUIRED",
        }

        response.data['msg'] = {}
        response.data['msg']['http_status'] = http_error_status_code[response.status_code]
        response.data['msg']['error_msg'] = exception_error_msg

    return Response(OrderedDict([
        ('status', response.data['status']),
        ('code', response.data['code']),
        ('msg', response.data['msg']),
        ('data', response.data['data']),
    ]))

