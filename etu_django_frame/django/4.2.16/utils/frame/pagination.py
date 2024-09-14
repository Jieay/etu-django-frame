#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 17:19
# @Author  : Jieay
# @File    : pagination.py
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from collections import OrderedDict
from rest_framework.response import Response


class CustomBasePagination(LimitOffsetPagination):
    """自定义偏移量分页器基类"""

    def get_paginated_response(self, data):
        status = True
        code = 200
        msg = 'Queried successfully.'
        if not data:
            # status = False  # 查不到，理论来说，只是结果为空，但不是出错。
            code = 404
            msg = "Data not found."

        return Response(OrderedDict([
            ('status', status),
            ('code', code),
            ('msg', msg),
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data),
        ]))

    def get_paginated_response_schema(self, schema):
        """
        接口文档返回自定义结构
        使用 drf_spectacular 自动生成接口文档，有效 type 类型如下
        from drf_spectacular.utils import OpenApiTypes
        type: string | integer | number | boolean | object | array

        Args:
            schema:

        Returns:

        """
        return {
            'type': 'object',
            'required': ['count', 'data'],
            'properties': {
                'status': {
                    'type': 'boolean',
                    'example': True,
                },
                'code': {
                    'type': 'integer',
                    'example': 200,
                },
                'msg': {
                    'type': 'string',
                    'example': 'Queried successfully.',
                },
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/?{offset_param}=400&{limit_param}=100'.format(
                        offset_param=self.offset_query_param, limit_param=self.limit_query_param),
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/accounts/?{offset_param}=200&{limit_param}=100'.format(
                        offset_param=self.offset_query_param, limit_param=self.limit_query_param),
                },
                'data': schema,
            },
        }


class CustomBasePageNumberPagination(PageNumberPagination):
    """自定义页码分页器基类"""

    # 默认显示每页的数据条数限制
    page_size = 10
    # 每页最大显示数据条数
    max_page_size = 200
    # 页码请求传参参数字段名
    page_query_param = 'number'
    # 每页数据限制请求传参参数字段名
    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        status = True
        code = 200
        msg = 'Queried successfully.'
        if not data:
            # status = False  # 查不到，理论来说，只是结果为空，但不是出错。
            code = 404
            msg = "Data not found."

        return Response(OrderedDict([
            ('status', status),
            ('code', code),
            ('msg', msg),
            ('count', self.page.paginator.count),
            ('number', self.page.number),
            ('size', len(data)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data)
        ]))


class RbacPageNumberPagination(CustomBasePageNumberPagination):
    # 每页最大显示数据条数
    max_page_size = 9999

    def get_paginated_response(self, data):
        status = True
        code = 200
        msg = 'Queried successfully.'
        if not data:
            # status = False  # 查不到，理论来说，只是结果为空，但不是出错。
            code = 404
            msg = "Data not found."

        data_info = {'data': OrderedDict([
            ('status', status),
            ('code', code),
            ('msg', msg),
            ('count', self.page.paginator.count),
            ('number', self.page.number),
            ('size', len(data)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('content', data)
        ])}
        return Response(data_info, content_type="application/json; charset=utf-8")
