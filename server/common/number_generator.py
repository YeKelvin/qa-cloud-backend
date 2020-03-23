#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : number_generator
# @Time    : 2020/3/20 14:03
# @Author  : Kelvin.Ye
from server.librarys.sequence import Sequence

__number_length__ = 10

__seq_user_no__ = Sequence('seq_user_no')
__seq_role_no__ = Sequence('seq_role_no')
__seq_permission_no__ = Sequence('seq_permission_no')

__seq_item_no__ = Sequence('seq_item_no')
__seq_topic_no__ = Sequence('seq_topic_no')
__seq_element_no__ = Sequence('seq_element_no')
__seq_package_no__ = Sequence('seq_package_no')
__seq_env_var_no__ = Sequence('seq_env_var_no')
__seq_http_header_no__ = Sequence('seq_http_header_no')


def generate_user_no():
    """生成用户编号
    """
    return 'U' + str(__seq_user_no__.next_value()).zfill(__number_length__)


def generate_role_no():
    """生成角色编号
    """
    return 'R' + str(__seq_role_no__.next_value()).zfill(__number_length__)


def generate_permission_no():
    """生成权限编号
    """
    return 'P' + str(__seq_permission_no__.next_value()).zfill(__number_length__)


def generate_item_no():
    return 'ITEM' + str(__seq_item_no__.next_value()).zfill(__number_length__)


def generate_topic_no():
    return 'TOPIC' + str(__seq_topic_no__.next_value()).zfill(__number_length__)


def generate_element_no():
    return 'EL' + str(__seq_element_no__.next_value()).zfill(__number_length__)


def generate_package_no():
    return 'EP' + str(__seq_package_no__.next_value()).zfill(__number_length__)


def generate_env_no():
    return 'ENV' + str(__seq_env_var_no__.next_value()).zfill(__number_length__)


def generate_header_no():
    return 'HEADER' + str(__seq_http_header_no__.next_value()).zfill(__number_length__)
