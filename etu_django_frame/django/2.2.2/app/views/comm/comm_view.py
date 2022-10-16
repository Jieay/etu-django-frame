#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-06 12:51
# @Author  : Jieay
# @File    : comm_view.py
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils.frame.api_view_external import BaseAdminApiView, BaseResponse
from django.conf import settings
from utils.frame.pagination import DrfYasgDjangoRestResponsePagination

import logging
logger = logging.getLogger(__name__)


class GetWebUrlView(BaseAdminApiView):

    data_response = openapi.Response('Web URL response', openapi.Schema('web_url', type=openapi.TYPE_STRING))

    @swagger_auto_schema(operation_description="前端地址查询",
                         responses={200: data_response, 404: 'Data not found.'},
                         paginator_inspectors=[DrfYasgDjangoRestResponsePagination])
    def get(self, request):
        web_url = settings.WEB_BASE_URL
        data = {}
        if web_url:
            data['web_url'] = web_url
            return BaseResponse(code=200, data=data, status=True, msg='Queried successfully.')
        return BaseResponse(data=data)
