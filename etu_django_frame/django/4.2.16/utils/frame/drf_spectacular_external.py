# -*- coding: utf-8 -*-
# @Time    : 2024/9/12 10:32
# @Author  : Jieay
# @File    : drf_spectacular_external.py
from rest_framework import serializers
from drf_spectacular.utils import OpenApiResponse, OpenApiExample, OpenApiTypes
from drf_spectacular.extensions import OpenApiAuthenticationExtension
import logging

logger = logging.getLogger(__name__)


class CustomDrfSpectacularAuthenticationExtension(OpenApiAuthenticationExtension):
    """
    为自定义认证类创建 OpenApiAuthenticationExtension ，此类需要在初始化注册
    """
    target_class = 'utils.frame.model_view_set.CustomBaseSessionAuthentication'  # 自定义认证类指定的完整路径
    name = 'CustomBaseSessionAuthentication'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Cookie',
            'description': 'Cookie: sessionid=abc123xyz456',
        }


class DrfSResponseBaseSerializer(serializers.Serializer):
    """接口文档返回的序列化器基础类"""
    status = serializers.BooleanField(help_text='状态', default=True)
    code = serializers.IntegerField(help_text='状态码', default=200)
    msg = serializers.CharField(help_text='日志信息', default='')

    def __init__(self, *args, **kwargs):
        # 获取动态字段配置
        dynamic_fields = kwargs.pop('dynamic_fields', None)
        status = kwargs.pop('status', None)
        code = kwargs.pop('code', None)
        msg = kwargs.pop('msg', None)
        super().__init__(*args, **kwargs)

        if dynamic_fields:
            for field_name, field_type in dynamic_fields.items():
                # 动态添加字段
                self.fields[field_name] = field_type

        if status is not None:
            self.fields['status'].default = status

        if code is not None:
            self.fields['code'].default = code

        if msg is not None:
            if isinstance(msg, str):
                self.fields['msg'] = serializers.CharField(help_text='日志信息', default=msg)
            elif isinstance(msg, dict):
                self.fields['msg'] = serializers.DictField(help_text='日志信息', default=msg)
            elif isinstance(msg, (list, tuple)):
                self.fields['msg'] = serializers.ListField(help_text='日志信息', default=msg)


class DrfSResponseSuccessSerializer(DrfSResponseBaseSerializer):
    """接口文档返回的序列化器成功类"""
    status = serializers.BooleanField(help_text='状态', default=True)
    code = serializers.IntegerField(help_text='状态码', default=200)
    msg = serializers.CharField(help_text='日志信息', default='Queried successfully.')
    data = serializers.DictField(help_text='数据', default={})


class DrfSResponseFailedSerializer(DrfSResponseBaseSerializer):
    """接口文档返回的序列化器失败类"""
    status = serializers.BooleanField(help_text='状态', default=False)
    code = serializers.IntegerField(help_text='状态码', default=400)
    msg = serializers.CharField(help_text='日志信息', default='Queried failed.')
    data = serializers.DictField(help_text='数据', default={})


class DrfSResponseQueriedExceptionSerializer(DrfSResponseBaseSerializer):
    """接口文档返回的序列化器异常类"""
    status = serializers.BooleanField(help_text='状态', default=False)
    code = serializers.IntegerField(help_text='状态码', default=507)
    msg = serializers.DictField(help_text='日志信息', default={})
    data = serializers.DictField(help_text='数据', default={})


class SerializerDrfSpectacularResponse:
    """序列化器接口文档返回构造"""
    def custom_response(self, serializer_name, description='', is_dynamic=False, **kwargs):
        """
        序列化器自定义构造返回数据
        Args:
            serializer_name: `serializers.Serializer` 序列化类
            description: `str` 显示名称
            is_dynamic: `bool` 是否动态新增 data 字段
            **kwargs:

        Returns: `OpenApiResponse`
        """
        _fields = {}
        status = kwargs.get('status', None)
        if status is not None:
            _fields['status'] = status
        code = kwargs.get('code', None)
        if code is not None:
            _fields['code'] = code
        msg = kwargs.get('msg', None)
        if msg is not None:
            _fields['msg'] = msg

        serializer_many = kwargs.get('serializer_many', False)

        if is_dynamic is True:
            if serializer_many is True:
                data = serializer_name(many=True)
            else:
                data = serializer_name()

            _fields['dynamic_fields'] = {
                'data': data,
            }
            # 重新构造序列化类，避免接口文档 Schema 类名称重复
            new_class_name = f'{serializer_name.__name__}Schema'  # 构造类名称
            new_serializer_class = type(new_class_name, (DrfSResponseBaseSerializer,), {})  # 构造新类
            _serializer_class = new_serializer_class(**_fields)
        else:
            _serializer_class = serializer_name(**_fields)

        return OpenApiResponse(
            response=_serializer_class,
            description=description
        )

    def api_response(self, data: list):
        """
        序列化器接口文档构造返回数据
        Args:
            data: `list` [{}]
                    'is_dynamic': `bool` 是否启用 data 字段, True
                    'code': `int` 状态码, 200
                    'status': `bool` 状态, True
                    'msg': `str|list|dict` 日志信息, 'Queried successfully.'
                    'serializer_name': `serializers.Serializer` 序列化类, TokenDataSerializer
                    'description': `str` 显示名称, '查询成功'

        Returns: `dict`
        """
        res_data = {
            507: self.custom_response(
                serializer_name=DrfSResponseQueriedExceptionSerializer,
                description='请求异常',
            )
        }
        for i in data:
            code = i.get('code', 0)
            res_data[code] = self.custom_response(**i)
        return res_data


class CustomDrfSpectacularResponse:
    """自定义接口文档返回构造"""

    def response_data(self, code=0, msg='', data=None, status=False):
        """
        返回格式化数据
        Args:
            code: `int` 状态码
            msg: 日志
            data: 数据
            status: `bool` 状态

        Returns: `obj`
        """
        return {
            "status": status,
            "code": code,
            "msg": msg,
            "data": data
        }

    def success_response(self, code=200, msg='Queried successfully.', data=None, status=True):
        """
        接口文档示例返回成功对象类型
        Args:
            code: `int` 状态码
            msg: 日志
            data: 数据
            status: `bool` 状态

        Returns: `obj`
        """
        return OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    'Success Example',
                    description="成功",
                    value=self.response_data(code, msg, data, status)
                )
            ]
        )

    def failed_response(self, code=400, msg='Queried failed.', data=None, status=False):
        """
        接口文档示例返回失败对象类型
        Args:
            code: `int` 状态码
            msg: 日志
            data: 数据
            status: `bool` 状态

        Returns: `obj`
        """
        return OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    'Failed Example',
                    description="失败",
                    value=self.response_data(code, msg, data, status)
                )
            ]
        )

    def custom_response(self, name, code, msg, data=None, status=False, description=''):
        """
        接口文档示例返回自定义对象类型
        Args:
            name: Examples名称
            code: `int` 状态码
            msg: 日志
            data: 数据
            status: `bool` 状态
            description: Example Description

        Returns: `obj`
        """
        if not description:
            description = name
        return OpenApiResponse(
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    name=name,
                    description=description,
                    value=self.response_data(code, msg, data, status)
                )
            ]
        )

    def api_response(self, data: dict):
        """
        接口文档生成示例返回对象 Responses
        Args:
            data: `dict` 状态码为键，值是 OpenApiResponse 对象

        Returns: `obj`
        """
        res_data = {
            507: self.custom_response(
                name='QueriedException',
                code=507,
                msg={},
                data={},
                description='请求异常'
            )
        }
        res_data.update(data)
        return res_data
