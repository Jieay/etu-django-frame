#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 18:29
# @Author  : Jieay
# @File    : members_view.py
from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.models import Token
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter

from utils.frame.model_view_set import CustomBaseViewSet, CustomBaseJsonResponse
from utils.frame.api_view_external import BaseAdminApiView, BaseOpenApiView, BaseResponse
from app.models.user.members import Members
from app.serializers.user.members_serializer import MembersModelSerializer, CreateMembersModelSerializer, \
    UpdateMembersModelSerializer, GetMembersSerializer
from utils.comm.commapi import get_serializer_data_to_json, clean_response_field, check_model_field
from utils.user.membersapi import get_aksk_token

import logging
logger = logging.getLogger(__name__)


class MembersView(BaseAdminApiView):
    """成员信息"""

    def get_token(self, request):
        auth = get_authorization_header(request).split()
        if len(auth) == 2:
            key = auth[1].decode()
        else:
            key = None
        token = Token.objects.select_related('user').get(key=key)
        return token

    def get_user_info(self, token):
        data = {}
        v_fields = [
            'id', 'username', 'name', 'email', 'unit_name', 'dept_name', 'employee_code',
            'employee_name', 'oaid', 'post_name', 'telephone'
        ]
        ck_obj = Members.objects.filter(id=token.user.id)
        if ck_obj.exists():
            data.update(ck_obj.values(*v_fields)[0])
        return data

    def get(self, request):
        token = self.get_token(request)
        data = {}
        if token is not None:
            data = self.get_user_info(token)
            return BaseResponse(code=200, data=data, status=True, msg='Queried successfully.')
        return BaseResponse(data=data)


class MembersFilter(filters.FilterSet):
    username = filters.CharFilter(field_name='username', lookup_expr='exact')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    oaid = filters.CharFilter(field_name='oaid', lookup_expr='exact')
    telephone = filters.CharFilter(field_name='telephone', lookup_expr='exact')

    class Meta:
        model = Members
        fields = [
            'id', 'username', 'name', 'oaid', 'telephone'
        ]
        ordering_fields = '__all__'


class MembersViewsSet(CustomBaseViewSet):
    """用户信息"""

    serializer_class = MembersModelSerializer
    queryset = Members.objects.all()
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filter_class = MembersFilter
    ordering = ['-ctime']
    model_name = Members

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = get_serializer_data_to_json(serializer.data)
            data = clean_response_field(data, self.del_fields)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = get_serializer_data_to_json(serializer.data)
        data = clean_response_field(data, self.del_fields)
        return CustomBaseJsonResponse(data)

    def create(self, request, *args, **kwargs):
        self.serializer_class = CreateMembersModelSerializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        logger.info('Create: {}'.format(serializer.data))
        data = get_serializer_data_to_json(serializer.data)
        return CustomBaseJsonResponse(data=data,
                                      code=status.HTTP_201_CREATED,
                                      headers=headers,
                                      msg="Created successfully.",
                                      status=True)

    def update(self, request, *args, **kwargs):
        self.serializer_class = UpdateMembersModelSerializer
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        logger.info('Update: {}'.format(serializer.data))
        data = get_serializer_data_to_json(serializer.data)
        return CustomBaseJsonResponse(data=data,
                                      code=status.HTTP_200_OK,
                                      msg="Updated successfully.",
                                      status=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = get_serializer_data_to_json(serializer.data)
        data = clean_response_field(data, self.del_fields)
        return CustomBaseJsonResponse(data=data,
                                      code=status.HTTP_200_OK,
                                      msg="Queried successfully.",
                                      status=True)

    def destroy(self, request, *args, **kwargs):
        check_model_field(request.data, self.model_name, ck_field='username')
        instance = self.get_object()
        _id = instance.id
        self.perform_destroy(instance)
        logger.info('Delete: {}'.format([{"id": _id}]))
        return CustomBaseJsonResponse(data=[{"id": _id}],
                                      code=status.HTTP_200_OK,
                                      msg="Deleted successfully.",
                                      status=True)


class APIGetTokenView(BaseOpenApiView):
    """获取token"""

    def post(self, request):
        access_key = request.data.get('accesskey')
        secret_key = request.data.get('secretkey')
        token = get_aksk_token(access_key, secret_key)
        data = {}
        if token is not None:
            data['token'] = token
            return BaseResponse(code=200, data=data, status=True, msg='Queried successfully.')
        return BaseResponse(data=data)
