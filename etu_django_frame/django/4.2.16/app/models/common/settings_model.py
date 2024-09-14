# -*- coding: utf-8 -*-
# @Time    : 2024/8/16 15:51
# @Author  : Jieay
# @File    : settings_model.py

from django.db import models


class SettingConfigsModel(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name='配置名称(KEY)')
    content = models.TextField(default='{}', blank=True, null=True, verbose_name="配置内容(VALUE)格式JSON")
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    mtime = models.DateTimeField(auto_now=True, verbose_name='修改时间')
    comments = models.TextField(blank=True, null=True, verbose_name='备注', help_text='备注信息。')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "app_common_setting_configs"
        verbose_name_plural = "(SC)公共配置信息"
