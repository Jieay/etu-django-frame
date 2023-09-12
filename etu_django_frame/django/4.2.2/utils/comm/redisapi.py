#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
import redis

RDHSOT = settings.REDIS_HOST
RDPASSWORD = settings.REDIS_PASSWORD
RDPORT = settings.REDIS_PORT
RDDB = settings.REDIS_BASE_DB


class MyRedis(object):

    def __init__(self, **redisinfo):
        """
        :param redisinfo: host, port, db, password
        """
        self.host = redisinfo.get('host', RDHSOT)
        self.port = redisinfo.get('port', RDPORT)
        self.db = redisinfo.get('db', RDDB)
        self.passwd = redisinfo.get('password', RDPASSWORD)
        redis_info = {
            "host": self.host,
            "port": self.port,
            "db": self.db
        }
        if self.passwd:
            redis_info['password'] = self.passwd
        redis_poolinfo = redis.ConnectionPool(**redis_info)
        self.__r = redis.Redis(connection_pool=redis_poolinfo)

    def set(self, key, value, timeout):
        self.__r.set(key, value)
        self.__r.expire(key, timeout)
        
    def get(self, key):
        return self.__r.get(key)
        
    def exists(self, key):
        return self.__r.exists(key)
    