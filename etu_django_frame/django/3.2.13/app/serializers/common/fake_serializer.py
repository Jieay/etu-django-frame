#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/20 4:36 下午
# @Author  : Jieay
# @File    : fake_serializer.py

from rest_framework import serializers
from app.models.common.fake_model import FakeModel


class FakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FakeModel
        fields = '__all__'