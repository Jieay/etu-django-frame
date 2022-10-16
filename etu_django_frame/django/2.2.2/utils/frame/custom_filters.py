#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 17:42
# @Author  : Jieay
# @File    : custom_filters.py

from django_filters.rest_framework import BaseInFilter, NumberFilter, BaseRangeFilter


class NumberInFilter(BaseInFilter, NumberFilter):
    pass


class NumberRangeFilter(BaseRangeFilter, NumberFilter):
    pass
