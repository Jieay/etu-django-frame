#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 18:21
# @Author  : Jieay
# @File    : urls.py

from django.conf.urls import url, include, re_path
from rest_framework import routers


urlpatterns = []

router = routers.DefaultRouter()

from app.views.user.members_view import MembersViewsSet, MembersView
from app.views.comm.comm_view import GetWebUrlView

router.register(r'users', MembersViewsSet)


urlpatterns += [
    re_path(r'v1/members/list', MembersView.as_view()),
    re_path(r'v1/web/url', GetWebUrlView.as_view()),
]


urlpatterns += [
    url(r'v1/', include(router.urls)),
]
