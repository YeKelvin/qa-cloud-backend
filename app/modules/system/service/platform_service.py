#!/usr/bin python3
# @File    : platform_service.py
# @Time    : 2023-09-12 14:07:41
# @Author  : Kelvin.Ye
from app.config import CONFIGS
from app.tools.service import http_service


@http_service
def query_platform_configs():
    return {
        'enterpriseAuthEnabled': bool(CONFIGS.SSO_ENTERPRISE_URL)
    }
