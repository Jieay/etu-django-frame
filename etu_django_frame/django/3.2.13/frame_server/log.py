#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/9/10 2:11 下午
# @Author  : Jieay
# @File    : log.py
# Logging setting


class CustomLogConfig(object):
    """全局日志格式定义"""

    def get_logging(self, level):
        # settings LOGGING
        logging = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '%(levelname)s [%(asctime)s] %(pathname)s %(lineno)d %(funcName)s %(process)d '
                              '%(thread)d \n \t %(message)s \n',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'main': {
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                    'format': '%(asctime)s [%(module)s %(levelname)s] %(message)s',
                },
                'simple': {
                    'format': "[%(levelname)s %(asctime)s %(process)d %(name)s %(module)s:%(lineno)d] %(message)s",
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'msg': {
                    'format': '%(message)s'
                },
                "custom_log": {
                    # 使用自定义日志输出格式中间件
                    "()": "utils.comm.middleware.logapi.DefaultServerFormatter",
                    "format": "%(levelname)1.1s [%(process)s-%(request_id)s %(asctime)s %(ip)s %(user)s "
                              "%(name)s|%(lineno)s] %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            'handlers': {
                "console": {
                    "level": level,
                    "class": "logging.StreamHandler",
                    # "formatter": 'simple',
                    # "formatter": 'verbose',
                    "formatter": 'custom_log',
                    "stream": "ext://sys.stdout"
                }
            },
            'loggers': {
                "django.server": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False
                },
                "django.request": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False
                },
                "app": {
                    "level": level,
                    "handlers": ["console"],
                    "propagate": False
                },
            }
        }
        return logging

    def set_logging(self, level, loggers_app):
        logging = self.get_logging(level)

        loggers_comm = {
            "level": level,
            "handlers": ["console"],
            "propagate": False
        }

        for log_app in loggers_app:
            logging['loggers'][log_app] = loggers_comm

        return logging
