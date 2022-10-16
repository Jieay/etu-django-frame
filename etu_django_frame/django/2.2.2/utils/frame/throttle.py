#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 17:25
# @Author  : Jieay
# @File    : throttle.py
from rest_framework.throttling import ScopedRateThrottle


class CustomBaseThrottle(ScopedRateThrottle):

    def get_cache_key(self, request, view):
        """
        Should return a unique cache-key which can be used for throttling.
        Must be overridden.

        May return `None` if the request should not be throttled.
        """
        if not request.user:
            ident = self.get_ident(request)
        else:
            ident = request.user

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
