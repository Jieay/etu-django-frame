#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis
from django.conf import settings


class MyRedis(object):

    def __init__(self, **redis_info):
        """
        :param redis_info: host, port, db, password
        """
        self.host = redis_info.get('host', settings.REDIS_HOST)
        self.port = redis_info.get('port', settings.REDIS_PORT)
        self.db = redis_info.get('db', settings.REDIS_BASE_DB)
        self.passwd = redis_info.get('password', settings.REDIS_PASSWORD)
        redis_info = {
            "host": self.host,
            "port": self.port,
            "db": self.db
        }
        if self.passwd:
            redis_info['password'] = self.passwd
        redis_pool_info = redis.ConnectionPool(**redis_info)
        self.__r = redis.Redis(connection_pool=redis_pool_info)

    def conn(self):
        """redis实例化连接"""
        return self.__r

    def set(self, key, value, timeout=None, nx=False):
        """
        添加键值对
        Args:
            key: 键
            value: 值
            timeout: 过期时间 (s)
            nx: True时存在不会创建

        Returns:
        """
        self.__r.set(name=key, value=value, nx=nx)
        if timeout:
            self.__r.expire(key, timeout)

    def get(self, key):
        """
        通过 KEY 获取 VALUE
        Args:
            key: 键

        Returns: `bytes` 值
        """
        return self.__r.get(key)

    def exists(self, key):
        """
        查询 KEY 是否存在
        Args:
            key: 键

        Returns: `int` 1 or 0

        """
        return self.__r.exists(key)

    def l_push(self, key, value):
        """
        Redis 列表(List), 指定列表名称 key , 从左 push 值
        Args:
            key: 键，列表名称
            value: 列表元素

        Returns: `int` 返回列表的长度
        """
        return self.__r.lpush(key, value)

    def r_push(self, key, value):
        """
        Redis 列表(List), 指定列表名称 key , 从右 push 值
        Args:
            key: 键，列表名称
            value: 列表元素

        Returns: `int` 返回列表的长度
        """
        return self.__r.rpush(key, value)

    def l_pop(self, key):
        """
        Redis 列表(List), 指定列表名称 key , 从左 Pop 值, 拿出即删除
        Args:
            key: 键，列表名称

        Returns: `bytes` 值
        """
        return self.__r.lpop(key)

    def r_pop(self, key):
        """
        Redis 列表(List), 指定列表名称 key , 从右 Pop 值, 拿出即删除
        Args:
            key: 键，列表名称

        Returns: `bytes` 值
        """
        return self.__r.rpop(key)

    def l_len(self, key):
        """
        Redis 列表(List), 获取列表长度
        Args:
            key: 键，列表名称

        Returns: `int` 返回列表的长度
        """
        return self.__r.llen(key)

    def l_range(self, key, start, end):
        """
        Redis 列表(List), 获取列表制定位置的元素
        Args:
            key: 键，列表名称
            start: 开始索引
            end: 结束索引

        Returns: `list` [bytes]
        """
        return self.__r.lrange(key, start, end)

    def h_set(self, key, field, value):
        """
        Redis 哈希(Hash), 用于为哈希表中的字段赋值
        Args:
            key: 键，哈希表名称
            field: 哈希表中字段
            value: 哈希表中字段的值

        Returns: `int` 1(新增) or 0(修改)
        """
        return self.__r.hset(key, field, value)

    def h_m_set(self, key, mapping):
        """
        Redis 哈希(Hash), 用于为哈希表中的多对字段赋值
        Args:
            key: 键，哈希表名称
            mapping: `dict` {str: str}

        Returns: `bool`
        """
        return self.__r.hmset(key, mapping)

    def h_get(self, key, field):
        """
        Redis 哈希(Hash), 获取哈希表中的字段的值
        Args:
            key: 键，哈希表名称
            field: 哈希表中字段

        Returns: `bytes`
        """
        return self.__r.hget(key, field)

    def h_exists(self, key, field):
        """
        Redis 哈希(Hash), 判断哈希表中的字段是否存在
        Args:
            key: 键，哈希表名称
            field: 哈希表中字段

        Returns: `bool`
        """
        return self.__r.hexists(key, field)

    def h_keys(self, key):
        """
        Redis 哈希(Hash), 获取哈希表中的所有字段
        Args:
            key: 键，哈希表名称

        Returns: `list` [bytes]
        """
        return self.__r.hkeys(key)

    def h_vals(self, key):
        """
        Redis 哈希(Hash), 获取哈希表中的所有字段的值
        Args:
            key: 键，哈希表名称

        Returns: `list` [bytes]
        """
        return self.__r.hvals(key)

    def h_get_all(self, key):
        """
        Redis 哈希(Hash), 获取哈希表中的所有字段和值
        Args:
            key: 键，哈希表名称

        Returns: `dict` {bytes: bytes}
        """
        return self.__r.hgetall(key)

    def h_del(self, key, fields):
        """
        Redis 哈希(Hash), 删除哈希表中指定字段
        Args:
            key: 键，哈希表名称
            *fields: 哈希表中的多个字段列表

        Returns: None
        """
        self.__r.hdel(key, *fields)

    def h_len(self, key):
        """
        Redis 哈希(Hash), 获取哈希表中长度
        Args:
            key: 键，哈希表名称

        Returns: `int`
        """
        return self.__r.hlen(key)
