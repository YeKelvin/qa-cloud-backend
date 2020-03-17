#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : env_var_service
# @Time    : 2020/3/13 16:59
# @Author  : Kelvin.Ye
from server.librarys.decorators.service import http_service
from server.librarys.request import RequestDTO
from server.librarys.sequence import Sequence
from server.utils.log_util import get_logger

log = get_logger(__name__)


@http_service
def environment_variable_list(req: RequestDTO):
    """分页查询环境变量列表
    """
    pass


@http_service
def environment_variable_all(req: RequestDTO):
    """查询所有环境变量
    """
    pass


@http_service
def create_environment_variable(req: RequestDTO):
    """新增环境变量
    """
    pass


@http_service
def modify_environment_variable(req: RequestDTO):
    """修改环境变量
    """
    pass


@http_service
def delete_environment_variable(req: RequestDTO):
    """删除环境变量
    """
    pass


def generate_env_no():
    seq_item_no = Sequence('seq_env_var_no')
    return 'ENV' + str(seq_item_no.next_value()).zfill(10)
