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
def query_environment_variable_list(req: RequestDTO):
    pass


@http_service
def query_environment_variable_all(req: RequestDTO):
    pass


@http_service
def create_environment_variable(req: RequestDTO):
    pass


@http_service
def modify_environment_variable(req: RequestDTO):
    pass


@http_service
def delete_environment_variable(req: RequestDTO):
    pass


__seq_env_var_no__ = Sequence('seq_env_var_no')


def generate_env_no():
    return 'ENV' + str(__seq_env_var_no__.next_value()).zfill(10)
