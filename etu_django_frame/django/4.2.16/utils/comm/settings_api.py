# -*- coding: utf-8 -*-
# @Time    : 2024/8/16 15:52
# @Author  : Jieay
# @File    : settings_api.py
import json
from utils.comm.commapi import check_json_format, str_to_int, get_function_name
from app.models.common.settings_model import SettingConfigsModel
from utils.comm.settings_docs import ConstSettingConfigData
import logging
logger = logging.getLogger(__name__)


class SettingConfig(object):
    """数据库自定义系统配置管理API"""

    # 获取自定义公共配置注册数据
    setting_config_data = ConstSettingConfigData()

    def docs(self):
        """
        获取所有注册配置信息
        Returns: `list` [('配置KEY', '配置说明')]
        """
        return ConstSettingConfigData.choices()

    def sc_keys(self):
        """
        获取所以注册配置 KEY 列表
        Returns: `list` ['KEY1', 'KEY2']
        """
        return ConstSettingConfigData.keys()

    def sc_values(self):
        """
        获取所以注册配置 KEY 说明列表
        Returns: `list` ['说明1', '说明2']
        """
        return ConstSettingConfigData.values()

    def sc_obj(self, **kwargs):
        """
        获取数据库实例
        Args:
            **kwargs: 数据库字段和值

        Returns: `obj` model
        """
        try:
            db_obj = SettingConfigsModel.objects.filter(**kwargs)
        except Exception as e:
            logger.warning(e)
            db_obj = None
        return db_obj

    def sc_obj_all(self):
        """
        获取数据库中所有配置
        Returns: `obj` model
        """
        if self.sc_obj() is None:
            return None
        return self.sc_obj().all()

    def dict(self):
        """
        获取公共配置键值对字典，来自数据库数据
        Returns: `dict` {'KEY1': 'VALUE1', 'KEY2': 'VALUE2'}
        """
        if self.sc_obj_all() is None:
            return {}
        data = dict(self.sc_obj_all().values_list('name', 'content'))
        return data

    def keys(self):
        """
         获取公共配置所有键，来自数据库数据
        Returns: `list` ['KEY1', 'KEY2']
        """
        return list(self.dict().keys())

    def check_key(self, name):
        """
        检查数据库中公共配置 KEY 是否存在， 不存在则新增
        Args:
            name: KEY

        Returns: `bool`
        """
        check_obj = self.sc_obj(name=name)
        if check_obj is None:
            return False
        comments = ConstSettingConfigData.get(key=name)
        if comments:
            if not check_obj.exists():
                SettingConfigsModel.objects.update_or_create(name=name, comments=comments)
                return False
            else:
                check_obj.update(comments=comments)
        return True

    def get_value(self, name, default=None, s_t_i=False):
        """
        获取指定 KEY 的值
        Args:
            name: KEY
            default: 默认值，在数据库中未查询到值，则返回默认值
            s_t_i: 是否字符串转换数字

        Returns: value
        """
        __c_f_name = get_function_name(c_name=self.__class__.__name__)
        try:
            self.check_key(name=name)
            data = self.dict().get(name, None)
            if check_json_format(data):
                data = json.loads(data)
            if not data and default is not None:
                data = default
            if s_t_i is True and data:
                data = str_to_int(data)
            return data
        except Exception as e:
            logger.warning('{} 获取公共自定义配置值异常，name: {}'.format(__c_f_name, name))
            logger.warning('{} {}'.format(__c_f_name, e))
            return None

    def check_keys(self):
        """检查自定义公共配置，用于初始化注册 key 更新到数据库"""
        __c_f_name = get_function_name(c_name=self.__class__.__name__)
        try:
            logger.info('自定义公共配置，开始检查')
            sc_keys = self.sc_keys()
            for key in sc_keys:
                self.check_key(name=key)
            logger.info('自定义公共配置，检查完成')
        except Exception as e:
            logger.warning('{} 自定义公共配置，检查出错：{}'.format(__c_f_name, e))
            return None

    def update_key_content(self, name, content):
        """
        更新公共配置指定key内容
        Args:
            name: KEY
            content: VALUE

        Returns: `bool`
        """
        self.check_key(name=name)
        check_obj = self.sc_obj(name=name)
        if check_obj.exists():
            if not isinstance(content, str):
                content = json.dumps(content)
            check_obj.update(content=content)
            return True
        return False

