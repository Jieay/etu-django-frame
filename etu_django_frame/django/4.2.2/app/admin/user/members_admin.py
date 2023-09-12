#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 19:04
# @Author  : Jieay
# @File    : members_admin.py
from django.contrib import admin
from app.models.user.members import Members


@admin.register(Members)
class MembersAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'name', 'is_staff', 'is_active', 'email', 'access_key', 'secret_key', 'ctime', 'mtime'
    )
    list_display_links = ('username',)
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'name')
    ordering = ('-id',)
    list_per_page = 10
