#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/20 4:25 下午
# @Author  : Jieay
# @File    : __init__.py.py
from django.conf import settings
from app.admin.user.members_admin import *
from app.admin.common.settings_admin import *

admin.site.site_header = settings.PROJECT_NAME
admin.site.site_title = settings.PROJECT_NAME
