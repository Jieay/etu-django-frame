#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/20 4:37 下午
# @Author  : Jieay
# @File    : members_serializer.py

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from app.models.user.members import Members


class MembersModelSerializer(serializers.ModelSerializer):
    department_info = serializers.SerializerMethodField(help_text="部门列表详细信息字段")

    # 生成接口文档时，使用 @extend_schema_field 手动指定字段的类型
    @extend_schema_field({
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
            'name': {'type': 'string'},
        }
    })
    def get_department_info(self, obj):
        return obj.department_info

    class Meta:
        model = Members
        fields = '__all__'


class ListMembersModelSerializer(MembersModelSerializer):
    """列表接口序列化"""

    class Meta:
        model = Members
        fields = [
            'id', 'username', 'name', 'email', 'unit_name', 'dept_name', 'employee_code',
            'employee_name', 'oaid', 'post_name', 'telephone', 'department_info'
        ]


class CreateMembersModelSerializer(MembersModelSerializer):
    """新增接口序列化"""

    def __init__(self, *args, **kwargs):
        super(CreateMembersModelSerializer, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['oaid'].required = True

    class Meta:
        model = Members
        exclude = ('password', 'access_key', 'secret_key', 'groups', 'user_permissions')


class UpdateMembersModelSerializer(CreateMembersModelSerializer):
    """更新接口序列化"""
    pass


class PartialUpdateMembersModelSerializer(MembersModelSerializer):
    """部分更新接口序列化"""

    class Meta:
        model = Members
        exclude = ('password', 'access_key', 'secret_key', 'groups', 'user_permissions')


class RetrieveMembersModelSerializer(MembersModelSerializer):
    """检索接口序列化"""

    class Meta:
        model = Members
        exclude = ('password', 'access_key', 'secret_key', 'groups', 'user_permissions')


class CreateDrfSRequestMembersSerializer(serializers.Serializer):
    """创建用户，接口文档请求Body参数"""
    name = serializers.CharField(required=True, help_text='用户')
    username = serializers.CharField(required=True, help_text='用户名')
    password = serializers.CharField(required=True, help_text='密码')
    email = serializers.EmailField(required=True, help_text='邮箱地址')
    oaid = serializers.CharField(required=True, help_text='OAID')
    unit_name = serializers.CharField(required=False, help_text='公司名称')
    dept_name = serializers.CharField(required=False, help_text='部门名称')
    employee_code = serializers.CharField(required=False, help_text='员工编号')
    employee_name = serializers.CharField(required=False, help_text='员工姓名')
    post_name = serializers.CharField(required=False, help_text='职位')


class DestroyDrfSRequestMembersSerializer(serializers.Serializer):
    """删除用户，接口文档请求Body参数"""
    username = serializers.CharField(required=True, help_text='用户名')


class DestroyDrfSResponseMembersSerializer(serializers.Serializer):
    """删除用户，接口文档返回data数据"""
    id = serializers.IntegerField(help_text='ID')


class GetDetailDrfSResponseMembersSerializer(serializers.ModelSerializer):
    """自定义用户详情，接口文档返回data数据"""

    class Meta:
        model = Members
        fields = [
            'id', 'username', 'name', 'email', 'unit_name', 'dept_name', 'employee_code',
            'employee_name', 'oaid', 'post_name', 'telephone', 'is_active', 'is_superuser', 'last_login'
        ]


class GetDrfSRequestMembersSerializer(serializers.Serializer):
    """获取Token，接口文档请求Body参数"""
    accesskey = serializers.CharField(required=True, help_text='AK')
    secretkey = serializers.CharField(required=True, help_text='SK')


class GetDrfSResponseMembersSerializer(serializers.Serializer):
    """获取Token，接口文档返回data数据"""
    token = serializers.CharField(help_text='Token')
