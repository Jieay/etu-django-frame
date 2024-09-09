#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-11-15 11:39
# @Author  : Jieay
# @File    : health_view.py

from utils.frame.api_view_external import BaseOpenApiView, BaseResponse

import logging
logger = logging.getLogger(__name__)


class GetHealthCheckView(BaseOpenApiView):
    """健康检查信息"""

    def get(self, request):
        data = {"check": 'ok'}
        return BaseResponse(code=200, data=data, status=True, msg='Queried successfully.')