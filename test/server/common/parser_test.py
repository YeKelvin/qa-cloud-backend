#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_parser.py
# @Time    : 2019/11/14 15:22
# @Author  : Kelvin.Ye
from server.common.parser import JsonParser, Argument


def test_argument():
    arg = Argument('ka').parse(True, 'va')
    print(f'arg={arg}')


def test_json_parser():
    data = {'ka': 'va', 'kb': 'vb'}
    req, error = JsonParser(
        Argument('ka')
    ).parse(data)
    print(req)
