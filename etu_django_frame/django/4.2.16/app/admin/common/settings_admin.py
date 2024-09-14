# -*- coding: utf-8 -*-
# @Time    : 2024/8/16 16:13
# @Author  : Jieay
# @File    : settings_admin.py

from django.contrib import admin
from app.models.common.settings_model import SettingConfigsModel


@admin.register(SettingConfigsModel)
class SettingConfigsModelAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'content', 'comments', 'ctime', 'mtime'
    )
    list_display_links = ['id', 'name']
    list_per_page = 15
    search_fields = ['id', 'name', 'content']
    list_editable = ('content',)
