#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : randoms.py
# @Time    : 2019/11/18 11:19
# @Author  : Kelvin.Ye
from random import randint


def get_number(length: int, prefix: str = '', suffix: str = '') -> str:
    """根据前缀、后缀和长度生成随机数

    :param length:  随机数的长度
    :param prefix:  前缀
    :param suffix:  后缀
    :return:        随机数
    """
    number = []
    for x in range(length):
        number.append(str(randint(0, 9)))
    return prefix.join(number).join(suffix)
