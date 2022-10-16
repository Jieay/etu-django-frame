#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 17:19
# @Author  : Jieay
# @File    : pagination.py
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination, CursorPagination
from collections import OrderedDict
from rest_framework.response import Response
from drf_yasg.inspectors import DjangoRestResponsePagination
from drf_yasg import openapi


class DrfYasgDjangoRestResponsePagination(DjangoRestResponsePagination):
    """Provides response schema pagination warpping for django-rest-framework's LimitOffsetPagination,
    PageNumberPagination and CursorPagination
    """

    def get_paginated_response(self, paginator, response_schema):
        assert response_schema.type == openapi.TYPE_ARRAY, "array return expected for paged response"
        paged_schema = None
        if isinstance(paginator, (LimitOffsetPagination, PageNumberPagination, CursorPagination)):
            has_count = not isinstance(paginator, CursorPagination)
            paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ('status', openapi.Schema(type=openapi.TYPE_BOOLEAN)),
                    ('code', openapi.Schema(type=openapi.TYPE_NUMBER)),
                    ('msg', openapi.Schema(type=openapi.TYPE_STRING)),
                    ('count', openapi.Schema(type=openapi.TYPE_INTEGER) if has_count else None),
                    ('next', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                    ('previous', openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                    ('data', response_schema),
                )),
                required=['data']
            )

            if has_count:
                paged_schema.required.insert(0, 'count')

        return paged_schema


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
