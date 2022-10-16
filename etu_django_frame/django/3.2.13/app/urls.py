#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/20 4:28 下午
# @Author  : Jieay
# @File    : urls.py

from django.urls import re_path, include
from rest_framework import routers


urlpatterns = []

router = routers.DefaultRouter()

from app.views.user.members_view import MembersViewsSet, MembersView

# 使用 ModelViewSet 方式写接口，通过 router 方式注册 url
# 使用时需要注意，需要以/结尾，例如：/api/v1/users/
router.register(r'users', MembersViewsSet)


# 使用 APIView 方式写接口，用过直接添加 urlpatterns 注册 url
urlpatterns += [
    re_path(r'^v1/members/list/$', MembersView.as_view()),
]


urlpatterns += [
    re_path(r'v1/', include(router.urls)),
]
