#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : id_generator.py
# @Time    : 2020/3/20 14:03
# @Author  : Kelvin.Ye
from app.utils import config
from app.utils.snowflake import IdWorker

__ID_WORKER__ = IdWorker(
    int(config.get('snowflake', 'datacenter.id')),
    int(config.get('snowflake', 'worker.id')),
    int(config.get('snowflake', 'sequence'))
)


def new_id():
    """生成编号"""
    return __ID_WORKER__.new_id()
