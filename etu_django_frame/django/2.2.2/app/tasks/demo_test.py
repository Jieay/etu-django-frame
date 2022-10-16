#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-09-23 17:23
# @Author  : Jieay
# @File    : demo_test.py
from frame_server.celery import celery_app as app
from celery import shared_task
from celery.schedules import crontab
import time


@app.task
def add(x, y):  # yui = add.delay(2,8)
    time.sleep(15)
    return x + y


@app.task()
def mul(x, y):
    time.sleep(20)
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)


@shared_task()
def timed_test():
    msg = '{}'.format('lai a ce shi a')
    return msg


@app.task(queue='democi', name='app.tasks.demo_test.demo_ci_queue_test')
def demo_ci_queue_test(x, y):
    time.sleep(20)
    return x * y
