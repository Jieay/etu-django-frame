#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-11-15 11:39
# @Author  : Jieay
# @File    : health_view.py

from utils.frame.api_view_external import BaseOpenApiView, BaseResponse
from utils.frame.drf_spectacular_external import CustomDrfSpectacularResponse
from drf_spectacular.utils import extend_schema
import logging

logger = logging.getLogger(__name__)


class GetHealthCheckView(BaseOpenApiView):
    """健康检查信息"""

    @extend_schema(
        tags=['Common'],
        summary='HealthCheck',
        description='健康检查接口',
        methods=['GET'],
        responses=CustomDrfSpectacularResponse().api_response(
            data={
                200: CustomDrfSpectacularResponse().success_response(
                    code=200,
                    data={'check': 'ok'}
                ),
                400: CustomDrfSpectacularResponse().failed_response(code=400)
            }
        )
    )
    def get(self, request):
        data = {'check': 'ok'}
        return BaseResponse(code=200, data=data, status=True, msg='Queried successfully.')
