#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-03 10:29
# @Author  : Jieay
# @File    : membersapi.py
import json
from rest_framework.authentication import get_authorization_header
from rest_framework.authtoken.models import Token
from app.models.user.members import Members


def get_request_token(request):
    auth = get_authorization_header(request).split()
    if len(auth) == 2:
        key = auth[1].decode()
    else:
        key = None
    token = Token.objects.select_related('user').get(key=key)
    return token


class GetUserInfo(object):

    def __init__(self, request):
        self.request = request

    def get_token(self):
        return get_request_token(self.request)

    def get_user_info(self):
        token = self.get_token()
        if token is not None:
            return token.user
        return

    def user_id(self):
        user_info = self.get_user_info()
        if user_info is not None:
            return user_info.id
        return

    def user_name(self):
        _name = None
        user_info = self.get_user_info()
        if user_info is not None:
            if user_info.name:
                _name = user_info.name
            elif user_info.username:
                _name = user_info.username
        return _name

    def user_oaid(self):
        user_info = self.get_user_info()
        if user_info is not None:
            return user_info.oaid
        return


def get_user_id(request):
    user_info = GetUserInfo(request)
    return user_info.user_id()


def get_user_name(request):
    user_info = GetUserInfo(request)
    return user_info.user_name()


def get_user_oaid(request):
    user_info = GetUserInfo(request)
    return user_info.user_oaid()


def get_aksk_token(access_key, secret_key):
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