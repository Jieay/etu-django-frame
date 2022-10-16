#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 17:31
# @Author  : Jieay
# @File    : fake_model.py
from django.db import models


class FakeModel(models.Model):
    pass

    class Meta:
        db_table = "app_common_fake"
