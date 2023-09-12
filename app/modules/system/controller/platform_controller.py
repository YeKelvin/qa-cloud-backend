#!/usr/bin python3
# @File    : platform_controller.py
# @Time    : 2023-09-12 12:08:28
# @Author  : Kelvin.Ye
from app.modules.system.controller import blueprint
from app.modules.system.service import platform_service as service


@blueprint.get('/platform/configs')
def query_platform_configs():
    """查询平台配置"""
    return service.query_platform_configs()
