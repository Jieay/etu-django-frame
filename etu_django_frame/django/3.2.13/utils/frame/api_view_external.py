#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 17:18
# @Author  : Jieay
# @File    : api_view_external.py
import copy
from rest_framework import status as rest_status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import JsonResponse
from django.db.models import Q
from urllib.parse import quote
from utils.comm.commapi import set_base_response_data
from utils.frame.pagination import CustomBasePagination
from utils.user.membersapi import GetUserInfo


code_msg_map = {
    0: '',
    301: '资源地址重定向',
    400: '参数错误',
    401: '用户校验失败',
    403: '访问未授权资源',
    404: '访问资源不存在',
    405: '访问method错误',
    406: '拒绝接受此请求',
    429: '请求过于频繁，请过会儿来试试~',
    500: '服务器迷路了。',
    507: '数据异常'
}

# 自定义错误码
custom_error_codes = [401, 405, 406, 429]
http_error_codes = [400]


class BaseApiView(APIView):
    """标准接口基类"""
    @classmethod
    def as_v1_view(cls):
        v3_view = cls.as_view()
        
        def view(request, *args, **kwargs):
            response = v3_view(request, *args, **kwargs)
            if isinstance(response, BaseResponse):
                code = response.data.get("code", 0)
                msg = response.data.get("msg", "")
                data = response.data.get("data", {})
                status = 200
                if code in custom_error_codes:
                    status = code
                    data = {
                        "msg": msg,
                        "err_code": code,
                        "data": data,
                    }
                if code in http_error_codes:
                    status = code
                    data = {
                        "msg": msg,
                        "err_code": code,
                        "data": data,
                    }
                return JsonResponse(data=data, status=status, safe=False)
            else:
                return response
        if hasattr(v3_view, 'csrf_exempt'):
            view.csrf_exempt = getattr(v3_view, 'csrf_exempt')
        return view


class BaseAdminApiView(BaseApiView):
    """认证接口基类"""
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)


class BaseOpenApiView(BaseApiView):
    """开放接口基类"""
    authentication_classes = ()
    permission_classes = (AllowAny,)


class BaseResponse(Response):
    """自定义接口返回基类，标准化输出返回字段"""

    def __init__(self, code=0, msg='', data=None, status=False):
        if not isinstance(data, list):
            data = data or {}
        if isinstance(data, dict):
            code = data.get('code', code)
            msg = data.get('msg', msg) or code_msg_map[code] or msg
        else:
            msg = msg or code_msg_map[code]

        if isinstance(data, dict):
            _data = {'status': status, 'code': code, 'msg': msg}
            if data.get('data', None) is None:
                _data['data'] = set_base_response_data(data)
            else:
                _data.update(data)
        else:
            _data = {
                'status': status,
                'code': code,
                'msg': msg,
                'data': data
            }
        super(BaseResponse, self).__init__(data=_data, status=rest_status.HTTP_200_OK)


class CustomBaseLimitOffsetPagination(CustomBasePagination):
    """自定义偏移量分页器"""
    pass


class CustomBaseFilter(object):
    """自定义接口过滤基类"""
    # 数据模型
    model = None
    # 显示字段列表 ['field1', 'field2']
    fields = []
    # 排序字段列表
    ordering_fields = []

    # 过滤器字段必须是显示字段，单个字段值匹配，精确或者模糊查询，过滤器对象 {'field1': 'contains', 'field2': 'exact'}
    filter_single = {}
    # 过滤器字段必须是显示字段，模糊搜索，一个值查询多个指定字段，过滤器对象 {'key_words': ['field1', 'field2']}
    # key_words: 是指定义查询key，匹配多个指定字段值，例如：key_words='aaa' 会在数据库的field1、field2字段进行模糊匹配
    filter_multiple = {}
    queryset = None

    def get_filter_single(self, request):
        """单个字段过滤器，每个字段对应1个值"""
        check_exacts = {}
        if self.filter_single:
            for sk, sv in self.filter_single.items():
                req_v = request.GET.get(sk)
                ck_fields_name = '{}__{}'.format(sk, sv)
                if req_v:
                    check_exacts[ck_fields_name] = req_v
        return check_exacts

    def get_filter_multiple(self, request):
        """模糊搜索，多字段过滤器查询"""
        mq_keys = ''
        mq_obj = Q()
        mq_obj.connector = 'OR'
        if self.filter_multiple:
            key_fields = []
            for mqk, mqv in self.filter_multiple.items():
                req_mqk = request.GET.get(mqk)
                for i in mqv:
                    mq_name = '{}__contains'.format(i)
                    if req_mqk:
                        r_mq = Q()
                        r_mq.connector = 'OR'
                        r_mq.children.append((mq_name, req_mqk))
                        mq_obj.add(r_mq, 'OR')
                        key_fields.append(mq_name)
            if key_fields:
                mq_keys = ' | '.join(key_fields)
        if mq_keys:
            return True, mq_obj
        return False, mq_obj

    def get_queryset(self, request):
        """查询器"""
        check_exacts = self.get_filter_single(request)
        mq_keys, mq_obj = self.get_filter_multiple(request)
        if mq_keys:
            if self.queryset is not None:
                queryset = self.queryset.filter(mq_obj)
            else:
                queryset = self.model.objects.filter(mq_obj)
        else:
            if self.queryset is not None:
                queryset = self.queryset
            else:
                queryset = self.model.objects.all()

        if check_exacts:
            queryset = queryset.filter(**check_exacts)

        queryset = queryset.values(*self.fields)
        queryset = queryset.order_by(*self.ordering_fields)
        return list(queryset)


class CustomBaseAdminApiView(BaseAdminApiView, CustomBaseFilter):
    """自定义认证接口基类"""

    def get(self, request):
        """封装列表请求支持分页"""
        data_list = self.get_queryset(request)
        page = CustomBaseLimitOffsetPagination()
        data_list_page = page.paginate_queryset(queryset=data_list, request=request, view=self)
        if data_list_page:
            return page.get_paginated_response(data_list_page)
        data = data_list
        return BaseResponse(code=404, data=data)


class BaseAdminSubServerProxyApiView(BaseAdminApiView):
    """子服务，代理类型API基类"""

    URL_PREFIX = '/sub-server/xxxxxxx/'

    def get_url(self, request):
        """获取请求URL，去除固定前缀，返回原服务URL"""
        full_path = request.path
        return full_path.replace(self.URL_PREFIX, '/')

    def get_params(self, request):
        """获取GET类型请求参数"""
        return request.GET

    def get_req_data(self, request):
        """获取POST类型请求参数"""
        return request.data

    def get_headers(self, request):
        """获取请求"""
        headers = request.headers
        new_headers = copy.deepcopy(headers)
        new_headers = dict(new_headers)
        new_headers.pop('Content-Length', False)
        new_headers.pop('User-Agent', False)
        new_headers.pop('Accept', False)
        new_headers.pop('Postman-Token', False)
        new_headers.pop('Connection', False)
        new_headers.pop('Accept-Encoding', False)
        new_headers.pop('Authorization', False)
        new_headers.pop('Host', False)
        user_info = GetUserInfo(request=request)
        username = user_info.user_name() or ''
        new_headers['Username'] = quote(username)
        name = user_info.user_name() or ''
        new_headers['Name'] = quote(name)
        return new_headers
