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
from utils.frame.drf_spectacular_external import CustomDrfSpectacularResponse
from app.models.user.members import Members
from app.serializers.user.members_serializer import MembersModelSerializer, CreateMembersModelSerializer, \
    UpdateMembersModelSerializer, RetrieveMembersModelSerializer, GetDrfSRequestMembersSerializer, \
    PartialUpdateMembersModelSerializer, DestroyDrfSRequestMembersSerializer, DestroyDrfSResponseMembersSerializer, \
    GetDrfSResponseMembersSerializer, \
    ListMembersModelSerializer, GetDetailDrfSResponseMembersSerializer
from utils.comm.commapi import get_serializer_data_to_json, clean_response_field, check_model_field
from utils.user.membersapi import get_aksk_token
from drf_spectacular.utils import extend_schema, OpenApiParameter
from utils.frame.drf_spectacular_external import SerializerDrfSpectacularResponse, DrfSResponseFailedSerializer

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
            'employee_name', 'oaid', 'post_name', 'telephone', 'is_active', 'is_superuser', 'last_login'
        ]
        ck_obj = Members.objects.filter(id=token.user.id)
        if ck_obj.exists():
            data.update(ck_obj.values(*v_fields)[0])
        return data

    @extend_schema(
        tags=['User'],
        summary='GetV1MembersDetail',
        description='查询用户详情接口',
        methods=['GET'],
        responses=CustomDrfSpectacularResponse().api_response(
            data={
                200: CustomDrfSpectacularResponse().success_response(
                    code=200,
                    data=GetDetailDrfSResponseMembersSerializer().data
                ),
                400: CustomDrfSpectacularResponse().failed_response(
                    code=400,
                    data={}
                )
            }
        ),
    )
    def get(self, request):
        token = self.get_token(request)
        data = {}
        if token is not None:
            data = self.get_user_info(token)
            return BaseResponse(code=200, data=data, status=True, msg='Queried successfully.')
        return BaseResponse(code=400, data=data)


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

    @extend_schema(
        tags=['User'],
        summary='ListV1Users',
        description='查询用户信息列表接口',
        methods=['GET'],
        parameters=[
            OpenApiParameter(name='id', description='用户ID', required=False, type=int),
            OpenApiParameter(name='username', description='用户名', required=False, type=str),
            OpenApiParameter(name='name', description='用户名称', required=False, type=str),
            OpenApiParameter(name='oaid', description='用户OAID', required=False, type=str),
            OpenApiParameter(name='telephone', description='电话', required=False, type=str),
        ],
        responses=ListMembersModelSerializer
    )
    def list(self, request, *args, **kwargs):
        self.serializer_class = ListMembersModelSerializer
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

    @extend_schema(
        tags=['User'],
        summary='CreateV1Users',
        description='新增用户信息接口',
        methods=['POST'],
        request=CreateMembersModelSerializer,
        responses=SerializerDrfSpectacularResponse().api_response(
            data=[
                {
                    'is_dynamic': True,
                    'code': 201,
                    'msg': 'Created successfully.',
                    'serializer_name': CreateMembersModelSerializer,
                    'description': '创建成功'
                }
            ]
        )
    )
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

    @extend_schema(
        tags=['User'],
        summary='UpdateV1Users',
        description='更新用户信息接口',
        methods=['PUT'],
        request=UpdateMembersModelSerializer,
        responses=SerializerDrfSpectacularResponse().api_response(
            data=[
                {
                    'is_dynamic': True,
                    'code': 200,
                    'msg': 'Updated successfully.',
                    'serializer_name': UpdateMembersModelSerializer,
                    'description': '更新成功'
                }
            ]
        )
    )
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

    @extend_schema(
        tags=['User'],
        summary='PartialUpdateV1Users',
        description='更新部分用户信息接口',
        methods=['PATCH'],
        responses=SerializerDrfSpectacularResponse().api_response(
            data=[
                {
                    'is_dynamic': True,
                    'code': 200,
                    'msg': 'Updated successfully.',
                    'serializer_name': PartialUpdateMembersModelSerializer,
                    'description': '更新成功'
                }
            ]
        )
    )
    def partial_update(self, request, *args, **kwargs):
        self.serializer_class = PartialUpdateMembersModelSerializer
        return super(MembersViewsSet, self).partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=['User'],
        summary='RetrieveV1Users',
        description='检索用户信息接口',
        methods=['GET'],
        responses=SerializerDrfSpectacularResponse().api_response(
            data=[
                {
                    'is_dynamic': True,
                    'code': 200,
                    'msg': 'Queried successfully.',
                    'serializer_name': RetrieveMembersModelSerializer,
                    'description': '查询成功'
                }
            ]
        )
    )
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = RetrieveMembersModelSerializer
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = get_serializer_data_to_json(serializer.data)
        data = clean_response_field(data, self.del_fields)
        return CustomBaseJsonResponse(data=data,
                                      code=status.HTTP_200_OK,
                                      msg="Queried successfully.",
                                      status=True)

    @extend_schema(
        tags=['User'],
        summary='DestroyV1Users',
        description='删除用户信息接口',
        methods=['DELETE'],
        request=DestroyDrfSRequestMembersSerializer,
        responses=SerializerDrfSpectacularResponse().api_response(
            data=[
                {
                    'is_dynamic': True,
                    'code': 200,
                    'msg': 'Deleted successfully.',
                    'serializer_name': DestroyDrfSResponseMembersSerializer,
                    'description': '删除成功'
                }
            ]
        )
    )
    def destroy(self, request, *args, **kwargs):
        check_model_field(request.data, self.model_name, ck_field='username')
        instance = self.get_object()
        _id = instance.id
        self.perform_destroy(instance)
        logger.info('Delete: {}'.format([{"id": _id}]))
        return CustomBaseJsonResponse(data={"id": _id},
                                      code=status.HTTP_200_OK,
                                      msg="Deleted successfully.",
                                      status=True)


class APIGetTokenView(BaseOpenApiView):
    """获取token"""

    @extend_schema(
        tags=['Token'],
        summary='GetToken',
        description='获取Token接口',
        methods=['POST'],
        request=GetDrfSRequestMembersSerializer,
        responses=SerializerDrfSpectacularResponse().api_response(
            data=[
                {
                    'is_dynamic': True,
                    'code': 200,
                    'serializer_name': GetDrfSResponseMembersSerializer,
                    'description': '查询成功'
                },
                {
                    'code': 400,
                    'serializer_name': DrfSResponseFailedSerializer,
                    'description': '查询失败'
                },
            ]
        )
    )
    def post(self, request):
        access_key = request.data.get('accesskey')
        secret_key = request.data.get('secretkey')
        token = get_aksk_token(access_key, secret_key)
        data = {}
        if token is not None:
            data['token'] = token
            return BaseResponse(code=200, data=data, status=True, msg='Queried successfully.')
        return BaseResponse(code=400, data=data)
