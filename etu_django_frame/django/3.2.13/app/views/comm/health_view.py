#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-11-15 11:39
# @Author  : Jieay
# @File    : health_view.py

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.frame.api_view_external import BaseOpenApiView, BaseResponse
from utils.frame.pagination import DrfYasgDjangoRestResponsePagination

import logging
logger = logging.getLogger(__name__)


class GetHealthCheckView(BaseOpenApiView):
    """健康检查信息"""

    data_response = openapi.Response('健康检查', openapi.Schema('check', type=openapi.TYPE_STRING))

    @swagger_auto_schema(operation_description="健康检查接口",
                         responses={200: data_response, 404: 'Data not found.'},
                         paginator_inspectors=[DrfYasgDjangoRestResponsePagination])
    def get(self, request):
        data = {"check": 'ok'}
        return BaseResponse(code=200, data=data, status=True, msg='Queried successfully.')