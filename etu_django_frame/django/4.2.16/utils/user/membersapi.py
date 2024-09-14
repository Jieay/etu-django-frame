#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-03 10:29
# @Author  : Jieay
# @File    : membersapi.py

from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.models import Token
from app.models.user.members import Members
from utils.comm.commapi import get_random


def get_aksk():
    """获取 AK SK"""
    access_key = get_random(17, ty='tystr')
    secret_key = get_random(25, ty='tystr')
    return access_key, secret_key


def set_aksk_to_db(username):
    """
    指定用户构造 AK SK 并且存入数据库
    Args:
        username: 用户名

    Returns: `dict`
    """
    access_key, secret_key = get_aksk()
    user_obj = Members.objects.filter(username=username)
    data = {}
    if user_obj.exists():
        if user_obj[0].access_key and user_obj[0].secret_key:
            access_key = user_obj[0].access_key
            secret_key = user_obj[0].secret_key
        else:
            user_obj.update(access_key=access_key, secret_key=secret_key)
        data['access_key'] = access_key
        data['secret_key'] = secret_key
    return data


def up_aksk_to_db(username):
    """
    指定用户更新 AK SK 到数据库
    Args:
        username: 用户名

    Returns: `dict`
    """
    access_key, secret_key = get_aksk()
    user_obj = Members.objects.filter(username=username)
    data = {}
    if user_obj.exists():
        user_obj.update(access_key=access_key, secret_key=secret_key)
        data['access_key'] = access_key
        data['secret_key'] = secret_key
    return data


def get_request_token(request):
    """
    通过请求获取 Token
    Args:
        request: 请求实例

    Returns: `obj`
    """
    auth = get_authorization_header(request).split()
    if len(auth) == 2:
        key = auth[1].decode()
    else:
        key = None
    token = Token.objects.select_related('user').get(key=key)
    return token


class GetUserInfo(object):
    """用户信息"""

    def __init__(self, request):
        self.request = request

    def get_token(self):
        """获取Token"""
        return get_request_token(self.request)

    def get_user_info(self):
        """获取用户信息"""
        token = self.get_token()
        if token is not None:
            return token.user
        return

    def user_id(self):
        """获取用户ID"""
        user_info = self.get_user_info()
        if user_info is not None:
            return user_info.id
        return

    def user_name(self):
        """获取用户名"""
        _name = None
        user_info = self.get_user_info()
        if user_info is not None:
            if user_info.name:
                _name = user_info.name
            elif user_info.username:
                _name = user_info.username
        return _name

    def user_oaid(self):
        """获取用户OAID"""
        user_info = self.get_user_info()
        if user_info is not None:
            return user_info.oaid
        return


def get_user_id(request):
    """
    通过请求获取用户ID
    Args:
        request: 请求实例

    Returns: `int`
    """
    user_info = GetUserInfo(request)
    return user_info.user_id()


def get_user_name(request):
    """
    通过请求获取用户名
    Args:
        request: 请求实例

    Returns: `str`
    """
    user_info = GetUserInfo(request)
    return user_info.user_name()


def get_user_oaid(request):
    """
    通过请求获取用户OAID
    Args:
        request: 请求实例

    Returns: `str`
    """
    user_info = GetUserInfo(request)
    return user_info.user_oaid()


def get_aksk_token(access_key, secret_key):
    """
    通过 AK SK 获取 Token
    Args:
        access_key: AK
        secret_key: SK

    Returns: `str`
    """
    token = None
    if access_key and secret_key:
        user_obj = Members.objects.filter(access_key=access_key, secret_key=secret_key)
        if user_obj.exists():
            user = user_obj[0]
            token_obj = Token.objects.filter(user=user)
            if token_obj.exists():
                token = token_obj[0].key
            else:
                add_token = Token.objects.update_or_create(user=user)
                token = add_token[0].key
    return token
