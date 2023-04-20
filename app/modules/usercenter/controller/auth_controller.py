#!/usr/bin/ python3
# @File    : auth_controller.py
# @Time    : 2020/6/12 18:24
# @Author  : Kelvin.Ye
from app.modules.usercenter.controller import blueprint
from app.modules.usercenter.service import auth_service as service


@blueprint.get('/encryption/factor')
def create_rsa_public_key():
    """获取加密因子"""
    return service.create_rsa_public_key()
