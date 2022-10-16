#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 17:30
# @Author  : Jieay
# @File    : model_view_set.py
from django.utils import six
from rest_framework import status
from rest_framework import viewsets
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.models.common.fake_model import FakeModel
from app.serializers.common.fake_serializer import FakeSerializer
from utils.comm.commapi import get_serializer_data_to_json, clean_response_field
from utils.frame.pagination import RbacPageNumberPagination


import logging
logger = logging.getLogger(__name__)


class CustomBaseSessionAuthentication(SessionAuthentication):
    """
    Use Django's session framework for authentication.
    """

    def authenticate(self, request):
        """
        Returns a `User` if the request session currently has a logged in user.
        Otherwise returns `None`.
        """

        # Get the session-based user from the underlying HttpRequest object
        user = getattr(request._request, 'user', None)

        # Unauthenticated, CSRF validation not required
        if not user or not user.is_active:
            return None

        self.enforce_csrf(request)

        # CSRF passed with authenticated user
        return (user, None)


class BaseModelViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, CustomBaseSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)


class BaseReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (TokenAuthentication, CustomBaseSessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)


class BaseOPenReadOnlyModelViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = ()
    permission_classes = (AllowAny,)


class CustomBaseJsonResponse(Response):

    def __init__(self, data=None, code=None, msg=None, status=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.
        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        super(Response, self).__init__(None, status=code)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {"status": status, "code": code, "msg": msg, "data": data}
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in six.iteritems(headers):
                self[name] = value


class CustomBaseViewSet(BaseModelViewSet):
    queryset = FakeModel.objects.all()
    serializer_class = FakeSerializer
    del_fields = ['soft_del']

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
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
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
        instance = self.get_object()
        _id = instance.id
        self.perform_destroy(instance)
        logger.info('Delete: {}'.format([{"id": _id}]))
        return CustomBaseJsonResponse(data=[{"id": _id}],
                                      code=status.HTTP_200_OK,
                                      msg="Deleted successfully.",
                                      status=True)


class CustomBaseReadOnlyViewSet(BaseReadOnlyModelViewSet):
    queryset = FakeModel.objects.all()
    serializer_class = FakeSerializer
    del_fields = ['soft_del']

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = get_serializer_data_to_json(serializer.data)
        data = clean_response_field(data, self.del_fields)
        return CustomBaseJsonResponse(data=data,
                                      code=status.HTTP_200_OK,
                                      msg="Queried successfully.",
                                      status=True)


class CustomBaseOpenReadOnlyViewSet(BaseOPenReadOnlyModelViewSet):
    queryset = FakeModel.objects.all()
    serializer_class = FakeSerializer
    del_fields = ['soft_del']

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = get_serializer_data_to_json(serializer.data)
        data = clean_response_field(data, self.del_fields)
        return CustomBaseJsonResponse(data=data,
                                      code=status.HTTP_200_OK,
                                      msg="Queried successfully.",
                                      status=True)


class RbacOpenReadOnlyViewSet(BaseOPenReadOnlyModelViewSet):
    queryset = FakeModel.objects.all()
    serializer_class = FakeSerializer
    del_fields = ['soft_del']
    pagination_class = RbacPageNumberPagination

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

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = get_serializer_data_to_json(serializer.data)
        data = clean_response_field(data, self.del_fields)
        return CustomBaseJsonResponse(data=data,
                                      code=status.HTTP_200_OK,
                                      msg="Queried successfully.",
                                      status=True)


class CustomOPenBaseViewSet(CustomBaseViewSet):
    authentication_classes = ()
    permission_classes = (AllowAny,)
