#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-09-19 16:24
# @Author  : Jieay
# @File    : user_key.py

from __future__ import absolute_import, unicode_literals
from django.core.management import BaseCommand
from utils.user.membersapi import set_aksk_to_db, up_aksk_to_db


class Command(BaseCommand):
    help = """
    python manage.py user_key
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--add',
            type=str,
            default=None,
            help='创建用户秘钥，用户名',
        )
        parser.add_argument(
            '--update',
            type=str,
            default=None,
            help='修改用户秘钥，用户名',
        )

    def handle(self, *args, **options):
        user_key_add = options.get("add")
        user_key_update = options.get("update")
        key_data = {}
        if user_key_add is not None:
            key_data = set_aksk_to_db(user_key_add)
        elif user_key_update is not None:
            key_data = up_aksk_to_db(user_key_update)
        else:
            print('请输入的用户名。')
        if key_data:
            print('access_key：{access_key} \nsecret_key：{secret_key}'.format(**key_data))
        else:
            print('输入的用户名不正确。')