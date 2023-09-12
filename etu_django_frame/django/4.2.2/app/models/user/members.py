#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/20 4:32 下午
# @Author  : Jieay
# @File    : members.py
import json
from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.comm.commapi import check_json_format


class UserDepartmentsModel(models.Model):
    id = models.IntegerField(primary_key=True, unique=True, verbose_name='ID')
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name='部门名称')
    parentid = models.IntegerField(blank=True, null=True, verbose_name='上级部门ID')
    order = models.IntegerField(blank=True, null=True, verbose_name='排序ID')
    desc = models.TextField(blank=True, null=True, verbose_name='描述')
    comments = models.TextField(blank=True, null=True, verbose_name='备注')
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    mtime = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "app_user_department"
        verbose_name_plural = "部门信息"


class Members(AbstractUser):
    name = models.CharField(max_length=32, blank=True, null=True, verbose_name="姓名", help_text="中文用户名称")
    unit_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="公司名称")
    dept_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="部门名称")
    department = models.TextField(
        default=[], blank=True, null=True,
        verbose_name='部门列表', help_text="填写的是部门ID列表，格式是JSON字符串，例如：[1,2]"
    )
    employee_code = models.CharField(max_length=32, blank=True, null=True, verbose_name="员工编号")
    employee_name = models.CharField(max_length=32, blank=True, null=True, verbose_name="员工姓名")
    oaid = models.CharField(max_length=32, blank=True, null=True, verbose_name="OAID", help_text="公司OAID，唯一标识")
    post_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="职位")
    telephone = models.CharField(max_length=11, blank=True, null=True, verbose_name="手机", help_text="11位数字")
    access_key = models.CharField(max_length=64, blank=True, null=True, verbose_name="access_key", help_text="秘钥 AK")
    secret_key = models.CharField(max_length=64, blank=True, null=True, verbose_name="secret_key",  help_text="秘钥 SK")
    ctime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    mtime = models.DateTimeField(auto_now=True, verbose_name='修改时间')

    def __str__(self):
        return self.username

    @property
    def department_info(self):
        data_info = []
        if check_json_format(self.department):
            department = json.loads(self.department)
            for dep in department:
                dep_obj = UserDepartmentsModel.objects.filter(id=dep)
                if dep_obj.exists():
                    data = {'id': dep, 'name': dep_obj[0].name}
                    data_info.append(data)
        return data_info

    class Meta:
        db_table = "app_user_members"
        verbose_name_plural = "用户信息"