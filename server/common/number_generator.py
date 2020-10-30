#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : number_generator
# @Time    : 2020/3/20 14:03
# @Author  : Kelvin.Ye
from server.common.utils import config
from server.common.utils.snowflake import IdWorker

__ID_WORKER__ = IdWorker(
    int(config.get('snowflake', 'datacenter.id')),
    int(config.get('snowflake', 'worker.id')),
    int(config.get('snowflake', 'sequence'))
)


def generate_no():
    """生成编号"""
    return __ID_WORKER__.new_id()
