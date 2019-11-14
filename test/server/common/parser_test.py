#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_parser.py
# @Time    : 2019/11/14 15:22
# @Author  : Kelvin.Ye
from server.common.parser import JsonParser, Argument


def test_():
    req, error = JsonParser(
        Argument('')
    )
