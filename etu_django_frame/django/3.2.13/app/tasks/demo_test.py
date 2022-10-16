#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019-09-23 17:23
# @Author  : Jieay
# @File    : demo_test.py
from frame_server.celery import celery_app as app
from celery import shared_task
import time


# 异步任务
# 使用方式：add.delay(2,8)
@app.task
def add(x, y):
    time.sleep(15)
    return x + y


# 定时任务两种写法
# 未指定队列，使用默认队列，在分布式中所有worker都可执行
@shared_task()
def timed_test():
    msg = f'测试定时任务'
    return msg


# 指定队列，在分布式中只在demo队列的节点上执行，如未启动demo队列worker，则不执行
@app.task(queue='demo', name='app.tasks.demo_test.demo_queue_test')
def demo_queue_test():
    msg = f'指定队列，测试定时任务'
    return msg

