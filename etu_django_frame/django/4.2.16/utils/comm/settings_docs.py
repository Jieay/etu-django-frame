# -*- coding: utf-8 -*-
# @Time    : 2024/8/16 15:53
# @Author  : Jieay
# @File    : settings_docs.py
from utils.comm.commapi import Choices

"""
自定义公共配置信息，在管理台操作配置

使用方式：
from utils.comm.settings_api import SettingConfig
sc = SettingConfig()
demo_test = sc.get_value(name='DEMO_TEST')
"""


class ConstSettingConfigData(Choices):
    """
    自定义公共配置信息，注册配置 KEY 和说明
    配置内容存储在数据库中，可以实现热更新配置。使用场景：分布式微服务、动态环境变量等
    """

    SC_000001 = ('DEMO_TEST', '数据库配置环境变量，动态生效。')
