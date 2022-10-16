#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 18:28
# @Author  : Jieay
# @File    : members_serializer.py

from rest_framework import serializers
from app.models.user.members import Members


class MembersModelSerializer(serializers.ModelSerializer):
    department_info = serializers.ReadOnlyField(help_text="部门列表详细信息字段")

    class Meta:
        model = Members
        fields = '__all__'


class CreateMembersModelSerializer(MembersModelSerializer):

    def __init__(self, *args, **kwargs):
        super(CreateMembersModelSerializer, self).__init__(*args, **kwargs)
        self.fields['oaid'].required = True


class UpdateMembersModelSerializer(CreateMembersModelSerializer):
    pass


class GetMembersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Members
        fields = [
            'id', 'username', 'name', 'email', 'unit_name', 'dept_name', 'employee_code',
            'employee_name', 'oaid', 'post_name', 'telephone'
        ]
