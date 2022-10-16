#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-09-17 08:58
# @Author  : Jieay
# @File    : commapi.py

import os
import re
import json
import copy
import time
import string
import random
import uuid
import fcntl
import inspect
import datetime
import functools
import subprocess


from rest_framework.exceptions import APIException


def func_execution_time(func):
    """
    方法执行时间 装饰器
    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        print('{} took execution time {} ms'.format(func.__name__, (end - start) * 1000))
        return res
    return wrapper


def get_random(mun, ty=None):
    """
    获取随机唯一字符串
    :param mun: 随机字符长度
    :param ty: 头部前缀字符
    :return:
    """
    if ty == 'tyint':
        restr = string.digits
    elif ty == 'tystr':
        restr = string.ascii_letters
    else:
        restr = string.digits + string.ascii_letters

    str_list = []
    for i in range(int(mun)):
        cs = random.choice(restr)
        str_list.append(cs)
    return ''.join(str_list)


def get_unique_id(title=None):
    """
    :param title: unique_id 的头部， 默认无
    :return: str 默认为28位数字
    """
    today_time = datetime.datetime.now()
    date_time = today_time.strftime("%Y%m%d%H%M%S")
    time_stamp = today_time.strftime("%s")
    time_str = str(date_time) + str(time_stamp)
    random_mun = get_random(4, ty='tyint')
    if title:
        str_id = '{0}{1}{2}'.format(str(title), time_str, random_mun)
    else:
        str_id = '{0}{1}'.format(time_str, random_mun)
    return str_id


def str_to_float(data):
    """
    将字符串转化成浮点数
    """
    try:
        data = float(data)
    except:
        data = data
    return data


def datetime_to_str(o):
    """
    封装将 datetime 时间对象转换字符串格式
    :param o: 时间对象：datetime.datetime or datetime.date
    :return:
    """
    if isinstance(o, datetime.datetime):
        return o.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(o, datetime.date):
        return o.strftime('%Y-%m-%d')
    else:
        return str(o)


def get_time_stamp(datetime_obj):
    """
    获取时间戳
    :param datetime_obj: 时间对象
    :return:
    """
    if isinstance(datetime_obj, datetime.datetime):
        return int(time.mktime(datetime_obj.timetuple()))
    elif re.match(r'\d+-\d+-\d+ \d+:\d+:\d+', datetime_obj):
        time_strp = time.strptime(datetime_obj, '%Y-%m-%d %H:%M:%S')
        return int(time.mktime(time_strp))
    return


def check_json_format(raw_msg):
    """
    用于判断一个字符串是否符合Json格式
    :param raw_msg: 源字符
    :return: 布尔值
    """
    if raw_msg == 'null':
        return False

    if isinstance(raw_msg, str):
        try:
            json.loads(raw_msg, encoding='utf-8')
        except ValueError:
            return False
        return True
    else:
        return False


def get_serializer_data_to_json(serializer_data):
    data = copy.deepcopy(serializer_data)
    if isinstance(data, dict):
        for k, v in data.items():
            if check_json_format(v):
                serializer_data[k] = json.loads(v)
            if isinstance(v, dict):
                for kk, vv in v.items():
                    if check_json_format(vv):
                        serializer_data[k][kk] = json.loads(vv)

    if isinstance(data, list):
        for nu, me in enumerate(data):
            if isinstance(me, dict):
                for k, v in me.items():
                    if check_json_format(v):
                        serializer_data[nu][k] = json.loads(v)
                    if isinstance(v, dict):
                        for kk, vv in v.items():
                            if check_json_format(vv):
                                serializer_data[nu][k][kk] = json.loads(vv)
    return serializer_data


class ApiLimitException(APIException):
    status_code = 503
    default_detail = 'Task already exists, try again later.'


class ApiFieldCheckException(APIException):
    status_code = 507
    default_detail = 'Field check exception.'


def api_limit_from_db(model, ck_field, key=None):
    """
    通过查询数据库指定字段条件，限制API接口请求
    :param model: 数据库model
    :param ck_field: 获取 request.data 查询的字段名称
    :param key: 自定义字段筛选条件，类型为 dict
    """
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            assert isinstance(key, dict), ApiLimitException(
                detail="@api_limit_from_db() missing required argument: 'key'"
            )

            request_data = args[1].data
            db_key = {}
            if isinstance(ck_field, (list, tuple)):
                ck_field_list = ck_field
            else:
                ck_field_list = [ck_field]
            for i in ck_field_list:
                db_field = request_data.get(i)
                if db_field is not None:
                    db_key[i] = db_field
            assert db_key, ApiLimitException(
                detail="api_limit_from_db() missing required data: 'ck_field'"
            )

            if isinstance(key, dict):
                key.update(db_key)
                obj = model.objects.filter(**key)
                for ok, ov in db_key.items():
                    key.pop(ok)
                if obj:
                    the_object = True
                else:
                    the_object = False
            else:
                the_object = False
            assert not the_object, ApiLimitException(
                detail="@api_limit_from_db() check db task already exists."
            )

            res = func(*args, **kwargs)
            return res
        return wrapper
    return decorate


def check_request_field(data, ck_field):
    """
    检查请求中是否存在指定的字段
    :param data: 请求数据
    :param ck_field: 指定的字段，可以是多个
    """
    if not isinstance(data, dict):
        raise ApiFieldCheckException(detail='The request is not JSON.')
    field_list = []
    if isinstance(ck_field, (list, tuple)):
        field_list.extend([x for x in ck_field])
    else:
        field_list.append(ck_field)

    ck_field_list = copy.deepcopy(field_list)
    for i in ck_field_list:
        ck_data_field = data.get(i, None)
        if ck_data_field is not None:
            field_list.remove(i)
    if field_list:
        msg_filed = ','.join(field_list)
        raise ApiFieldCheckException(detail='The request data {} is not exist.'.format(msg_filed))

    return data


def check_model_field(data, model, **kwargs):
    """
    检查请求的数据，指定字段是否存在数据库中，is_exist: 默认不存在则报异常，否则存在报异常
    :param data: 请求数据
    :param model: 数据库 model
    :param kwargs: ck_field 指定检查的字段，可以是多个
    """
    field_list = []
    exclude_fields = ['ck_field', 'is_exist', 'check_del']
    ck_field = kwargs.get('ck_field', None)
    if isinstance(ck_field, (list, tuple)):
        field_list.extend(ck_field)
    if ck_field:
        field_list.append(ck_field)
    if isinstance(kwargs, dict):
        _ks = list(kwargs.keys())
        for ef in exclude_fields:
            if ef in _ks:
                _ks.remove(ef)
        field_list.extend(_ks)
    check_request_field(data=data, ck_field=field_list)

    ck_dict = {}
    for i in field_list:
        fd = data.get(i, None)
        if fd:
            ck_dict[i] = fd

    is_exist = kwargs.get('is_exist', False)
    check_del = kwargs.get('check_del', None)
    if check_del:
        ck_dict['soft_del'] = False

    ck_obj = model.objects.filter(**ck_dict)
    if is_exist is True:
        if ck_obj.exists():
            msg_filed = ', '.join(ck_dict)
            raise ApiFieldCheckException(detail='The request data {} is exist for model.'.format(msg_filed))
    else:
        if not ck_obj.exists():
            msg_filed = ', '.join(ck_dict)
            raise ApiFieldCheckException(detail='The request data {} is not exist for model.'.format(msg_filed))

    return data


def clean_response_field(data, ck_field):
    """
    删除请求返回值中的字段
    :param data: 返回数据
    :param ck_field: 需要删除的字段
    """
    data_cp = copy.deepcopy(data)

    if not isinstance(data, (dict, list)):
        raise ApiFieldCheckException(detail='The response is not JSON.')
    field_list = []
    if isinstance(ck_field, (list, tuple)):
        field_list.extend([x for x in ck_field])
    else:
        field_list.append(ck_field)

    if isinstance(data, dict):
        for k, v in data_cp.items():
            if k in field_list:
                data.pop(k)
    if isinstance(data, list):
        for m, obj in enumerate(data_cp):
            if isinstance(obj, dict):
                for kk, vv in obj.items():
                    if kk in field_list:
                        data[m].pop(kk)
    return data


def get_model_field_data(model, ck_field, *args, **kwargs):
    """
    获取指定字段的数据，并且可以指定字段排序
    :param model: 数据库 model
    :param ck_field: 自定字段，单个或者一个列表
    :param args: 指定字段，多个字段
    :param kwargs: 排序字段order_by， 正序'xxx'|倒序'-xxx'
    """
    filed_list = []
    if isinstance(ck_field, (list, tuple)):
        filed_list.extend(ck_field)
    else:
        filed_list.append(ck_field)
    for i in args:
        if isinstance(i, (list, tuple)):
            filed_list.extend(i)
        else:
            filed_list.append(i)
    order_by = kwargs.get('order_by')
    if order_by is not None:
        ck_obj = model.objects.all().order_by(order_by).values(*filed_list)
    else:
        ck_obj = model.objects.all().values(*filed_list)
    return list(ck_obj)


def check_dict_fields(data, ck_fields):
    """
    检查数据字典中，查询的字段不存在值则 返回 False
    :param data: 数据字典
    :param ck_fields: 查询字段 列表
    :return: False or True
    """
    if not isinstance(ck_fields, (list, tuple)):
        ck_fields = [ck_fields]

    _info = copy.deepcopy(ck_fields)
    if isinstance(data, dict):
        for i in ck_fields:
            ck_v = data.get(i, None)
            if ck_v is not None:
                _info.remove(i)
    if _info:
        return False
    return True


def str_to_int(data):
    """
    将字符串转化成数字
    :param data: str
    :return: int
    """
    try:
        data_info = int(data)
    except:
        data_info = data
    return data_info


def get_str_to_class(data):
    """
    解析对象字符串，将字符串转化成类名称和包的路径
    :param data: 对象字符串
    :return: (类名称, 包路径)
    """
    # data = "<class 'app.models.asset.envs_model.EnvsModel'>"
    data = data.replace('<', '').replace('>', '').replace("'", "").split(' ')
    if len(data) == 2:
        path_str = None
        m_name = None
        if data[0] == 'class':
            p_k = data[1].split('.')
            path_str = '.'.join(p_k[:-1])
            m_name = p_k[-1]
        return m_name, path_str
    return


def get_model_data_from_id(_id, model):
    """
    通过 ID 获取数据库中该条记录的数据
    :param _id: ID
    :param model: 表对象
    :return: `dict`
    """
    obj = model.objects.filter(id=_id).values()
    return obj[0]


def set_mark_delete(_id, model, **kwargs):
    """
    数据软删除，更新数据的标记记录
    :param _id: ID
    :param model: model
    :param kwargs: soft_del=True
    """
    if not kwargs:
        kwargs['soft_del'] = True
    obj = model.objects.filter(id=_id).update(**kwargs)
    return obj


def set_base_response_data(data=None):
    """
    处理自定义接口返回值的 data 数据中的状态字段
    """
    _data = {}
    if isinstance(data, dict):
        _data = copy.deepcopy(data)
        for i in ['status', 'code', 'msg']:
            if data.get(i, None) is not None:
                _data.pop(i)
    else:
        if data is not None:
            _data = data
    return _data


def check_telephone(telephone):
    """
    检查手机号码的合法性
    :param telephone: 手机号字符
    """
    regx = re.match('^[1-9][1-9][0-9]{9}$', telephone)
    if regx is None:
        return False
    return True


def modify_dict_mapping_dict(data, mapping_dict):
    """
    实现将一个字典的key映射成另外的key
    :param data: 要进行处理的数据字典，旧数据字典
    :param mapping_dict: 映射表，字典类型
    :return: 进过修改key名字的新数据字典
    """
    new_data = {}
    # 判断是否是JSON格式
    if check_json_format(data):
        data = json.loads(data)

    # 判断传入的参数是否为dict类型
    if not isinstance(data, dict):
        return new_data
    if not isinstance(mapping_dict, dict):
        return new_data
    for d_k, d_v in data.items():
        if check_json_format(d_v):
            d_v = json.loads(d_v)
        n_d_v = copy.deepcopy(d_v)
        # if isinstance(d_v, list):
        #     if d_v and isinstance(d_v[0], dict):
        #         n_d_v = d_v[0].get('name')

        if isinstance(n_d_v, (list, dict, tuple)):
            n_d_v = json.dumps(n_d_v)

        new_ks = mapping_dict.get(d_k)
        if isinstance(new_ks, list):
            for kk in new_ks:
                new_data[kk] = n_d_v
        else:
            if new_ks:
                new_data[new_ks] = n_d_v
    return new_data


def remove_fields_not_exists_model(model, dict_data):
    """
    删除不存在model字段中的dict keys
    :param model: 数据库模型
    :param dict_data: 字典对象
    :return:
    """
    field_names = [f.name for f in model._meta.fields]
    temp_dict = copy.copy(dict_data)
    for key in temp_dict.keys():
        if key not in field_names:
            dict_data.pop(key)


def order_time_mg(location_datetime, time_type=None, leadtime=10, timeout=10):
    """
    订单超时或者提前时间管理
    :param location_datetime: 指定时间
    :param time_type: 时间类型，超时或者提前，[ leadtime | timeout ]
    :param leadtime: 提前几分钟， 默认提前10分钟
    :param timeout: 超时几分钟，默认10分钟
    :return: bool
    """
    ck_time = False
    location_stamp = get_time_stamp(location_datetime)

    if time_type == 'timeout':
        # 超时
        timeout_limit_datetime = datetime.datetime.now() - datetime.timedelta(minutes=timeout)
        timeout_limit_stamp = get_time_stamp(timeout_limit_datetime)
        if timeout_limit_stamp > location_stamp:
            ck_time = True
    elif time_type == 'leadtime':
        # 提前
        leadtime_limit_datetime = datetime.datetime.now() + datetime.timedelta(minutes=leadtime)
        leadtime_limit_stamp = get_time_stamp(leadtime_limit_datetime)
        if leadtime_limit_stamp > location_stamp:
            ck_time = True

    return ck_time


def get_function_name(c_name=None):
    """
    动态获取正在运行函数(或方法)名称
    :param c_name: 类名称
    """
    if c_name is not None:
        f_name = '%s.%s' % (c_name, inspect.stack()[1][3])
    else:
        f_name = '%s' % inspect.stack()[1][3]
    return f_name


def func_exe_retry(ExceptionToCheck, tries=4, delay=3, back_off=2, logger=None):
    """
    函数运行重试装饰器
    :param ExceptionToCheck: 异常参数元组（TypeError,ValueError）
    :param tries: 重试次数
    :param delay: 重试延时时间 （秒）
    :param back_off: 重试延时倍数
    :param logger: 日志参数
    """
    def deco_retry(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            m_tries, m_delay = tries, delay
            while m_tries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), m_delay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(m_delay)
                    m_tries -= 1
                    m_delay *= back_off
            return f(*args, **kwargs)
        return f_retry  # true decorator
    return deco_retry


def random_sleep_ms():
    """随机毫秒休眠"""
    sleep_time = random.randint(0, 100) * 0.01
    time.sleep(sleep_time)
    return sleep_time


def filter_attrs(attrs):
    for k, v in attrs.items():
        if k.startswith("__"):
            yield k, v
        else:
            if isinstance(v, tuple):
                yield k, v[0]
                yield f'{k}_NAME', v[1]
            else:
                yield k, v


class ChoicesMeta(type):
    def __new__(cls, name, bases, attrs):
        real_attrs = dict(filter_attrs(attrs))
        cls = super(ChoicesMeta, cls).__new__(cls, name, bases, real_attrs)
        cls._dict = {v[0]: v[1] for k, v in attrs.items() if not k.startswith("__") and isinstance(v, tuple)}
        cls._items = list(cls._dict.items())
        cls._values = list(map(lambda x: x[1], cls._items))
        cls._keys = list(map(lambda x: x[0], cls._items))
        return cls

    def __contains__(self, val):
        return val in self.keys()

    def __getitem__(self, k):
        return self._dict[k]

    def keys(cls):
        return cls._keys

    def values(self):
        return self._values

    def items(self):
        return self._items

    def dict(self):
        return self._dict

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def choices(self):
        return self.items()


class Choices(object, metaclass=ChoicesMeta):
    """ 自定义选择常量构造的用法
        In [18]: class FeedType(Choices):
            ...:     IMAGE = (1, '⽂文字图⽚片')
            ...:     VIDEO = (2, '⽂文字视频')
            ...:     ARTICLE = (3, '⽂文章')
            ...:

        In [19]: FeedType.IMAGE == 1
        Out[19]: True

        In [20]: FeedType.IMAGE_NAME == '文字图片'
        Out[20]: False

        In [21]: FeedType.IMAGE in FeedType
        Out[21]: True

        In [22]: FeedType.keys()
        Out[22]: [1, 2, 3]

        In [23]: FeedType.values()
        Out[23]: ['⽂文字图⽚片', '⽂文字视频', '⽂文章']

        In [24]: FeedType.items()
        Out[24]: [(1, '⽂文字图⽚片'), (2, '⽂文字视频'), (3, '⽂文章')]

        In [25]: FeedType.dict()
        Out[25]: {1: '⽂文字图⽚片', 2: '⽂文字视频', 3: '⽂文章'}

        In [26]: FeedType.choices()
        Out[26]: [(1, '⽂文字图⽚片'), (2, '⽂文字视频'), (3, '⽂文章')]

        In [27]: FeedType.get(FeedType.IMAGE)
        Out[27]: '⽂文字图⽚片'
    """


class ModelChoicesMeta(type):
    """数据库模型选择常量元类"""
    def __new__(cls, name, bases, data):
        cls = super(ModelChoicesMeta, cls).__new__(cls, name, bases, data)
        model_name, fields = data.get('data', [None, []])
        data_dict = []
        if model_name:
            try:
                ck_obj = model_name.objects.all().values_list(*fields)
                if ck_obj:
                    data_dict = list(ck_obj)
            except Exception as e:
                print(e)
        cls._dict = dict(data_dict)
        cls._items = list(cls._dict.items())
        cls._values = cls._dict.values()
        cls._keys = cls._dict.keys()
        return cls

    def __contains__(self, val):
        return val in self.keys()

    def __getitem__(self, k):
        return self._dict[k]

    def keys(cls):
        return cls._keys

    def values(self):
        return self._values

    def items(self):
        return self._items

    def dict(self):
        return self._dict

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def choices(self):
        return self.items()


class ModelChoices(object, metaclass=ModelChoicesMeta):
    """
    使用数据库模型，指定字段，构造自定义选择常量的用法
    In [2]: class OAWorkFlowTypeChoices(ModelChoices):
       ...:
       ...:     data = (OAWorkFlowTypesModel, ('number', 'name'))
       ...:

    In [3]: OAWorkFlowTypeChoices.choices()
    Out[3]: [(1, 'KJ008'), (2, 'KJ021')]

    In [4]: OAWorkFlowTypeChoices.get(1)
    Out[4]: 'KJ008'

    In [5]: OAWorkFlowTypeChoices.get(2)
    Out[5]: 'KJ021'

    In [6]: OAWorkFlowTypeChoices.keys()
    Out[6]: dict_keys([1, 2])

    In [7]: OAWorkFlowTypeChoices.values()
    Out[7]: dict_values(['KJ008', 'KJ021'])

    In [8]: OAWorkFlowTypeChoices.items()
    Out[8]: [(1, 'KJ008'), (2, 'KJ021')]

    In [9]: OAWorkFlowTypeChoices.dict()
    Out[9]: {1: 'KJ008', 2: 'KJ021'}

    """


def set_custom_transaction_lock_data(new_data, old_data):
    """
    构造自定义事务锁数据更新
    :param new_data: `dict` 新数据库数据，数据库字段的对象数据需要反序列化，json.loads
    :param old_data: `dict` 旧的数据
    """
    # 防止数据调用被更新，做深度拷贝
    data = copy.deepcopy(new_data)
    _old_data = copy.deepcopy(old_data)
    # 遍历旧的数据，取出字段和字段值
    for o_k, o_v in _old_data.items():
        new_v = new_data.get(o_k)
        # 判断新的字段值是否为序列化对象
        if check_json_format(new_v):
            new_v = json.loads(new_v)
        # 判断旧的字段值是否为序列化对象
        if check_json_format(o_v):
            o_v = json.loads(o_v)

        # 新字段值是否为空
        if new_v:
            # 将新字段值，做深度拷贝
            _new_v = copy.deepcopy(new_v)
            if isinstance(new_v, list) and isinstance(o_v, list):
                new_vv = _new_v
                for ov in o_v:
                    if ov not in new_vv:
                        new_vv.append(ov)
                data[o_k] = json.dumps(new_vv)

            elif isinstance(new_v, dict) and isinstance(o_v, dict):
                new_vv = _new_v.update(o_v)
                data[o_k] = json.dumps(new_vv)

            elif new_v and o_v:
                if isinstance(o_v, (list, dict)):
                    o_v = json.dumps(o_v)
                data[o_k] = o_v
            else:
                pass
        else:
            if isinstance(o_v, (list, dict)):
                o_v = json.dumps(o_v)
            data[o_k] = o_v
    return data


def get_command_exec_result(command_str):
    """
    执行shell命令，且返回执行结果
    :param command_str: shell 命令字符串
    :return: (0, stdout)
    """
    return subprocess.getstatusoutput(command_str)


def check_and_mkdir_file_path_dir(file_path, is_dir=False):
    """
    检查传入文件的目录是否存在， 没有则创建
    :param file_path: 文件绝对路径
    :param is_dir: 传入路径是否只包含目录路径
    :return:
    """
    if not is_dir:
        file_dir_name = os.path.dirname(file_path)
    else:
        file_dir_name = file_path
    try:
        if not os.path.exists(file_dir_name):
            os.makedirs(file_dir_name)
        return True
    except Exception as e:
        return False


def write_text_file_add_lock(data, file_path, write_type="w"):
    """
    编写文本文件(加等待锁， 防止写入冲突)
    :param data: str
    :param file_path: 写入文件绝对路径, str
    :param write_type: 写类型, str, w或a, 即覆盖或追加
    :return:
    """
    try:
        check_and_mkdir_file_path_dir(file_path=file_path)
        with open(file_path, write_type) as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.write(data)
            fcntl.flock(f, fcntl.LOCK_UN)
        return True
    except Exception as e:
        return False


def get_a_uuid():
    """
    获取一个UUID
    :return: str
    """
    uuid_obj = uuid.uuid4()
    uuid_str = str(uuid_obj)
    return uuid_str


def get_cur_host_mac_addr():
    """
    获取当前主机节点MAC地址
    :return:
    """
    addr = hex(uuid.getnode())[2:].upper()
    standard_addr = '0' * (12 - len(addr)) + addr
    standard_mac_addr = '-'.join(standard_addr[i:i + 2] for i in range(0, len(standard_addr), 2))
    return standard_mac_addr


def is_ip(ip_str):
    """检查字符串是否是IP"""
    ip_str = str(ip_str)
    p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if p.match(ip_str):
        return True
    else:
        return False
