#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/20 4:31 下午
# @Author  : Jieay
# @File    : fake_model.py
from django.db import models


class FakeModel(models.Model):
    pass

    class Meta:
        db_table = "app_common_fake"