#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020-05-01 18:19
# @Author  : Jieay
# @File    : celery.py
import logging
import os

from celery import Celery
from celery import Task
from django.conf import settings


logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frame_server.settings')


class LogErrorsTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logging.exception(exc)


celery_app = Celery('frame_server', broker=settings.BROKER_URL, task_cls=LogErrorsTask)

celery_app.config_from_object('django.conf:settings')

celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
