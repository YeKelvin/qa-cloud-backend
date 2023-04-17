#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : identity.py
# @Time    : 2020/3/20 14:03
# @Author  : Kelvin.Ye
from app import config as CONFIG
from app.utils.snowflake import IdWorker
from app.utils.snowflake import get_datacenter_id
from app.utils.snowflake import get_worker_id


__ID_WORKER__ = IdWorker(
    int(CONFIG.SNOWFLAKE_DATACENTER_ID) or get_datacenter_id(),
    int(CONFIG.SNOWFLAKE_WORKER_ID) or get_worker_id(),
    int(CONFIG.SNOWFLAKE_SEQUENCE) or 1
)


def new_id():
    """生成编号"""
    return str(__ID_WORKER__.new_id())
