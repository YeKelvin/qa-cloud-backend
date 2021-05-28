#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : test_parser.py
# @Time    : 2019/11/14 15:22
# @Author  : Kelvin.Ye
from app.common.parser import JsonParser, Argument


def test_argument():
    arg = Argument('ka').parse(True, 'va')
    print(f'arg={arg}')


def test_json_parser():
    data = {'ka': 'va', 'kb': 'vb'}
    req, error = JsonParser(
        Argument('ka')
    ).parse(data)
    print(f'arg={req}')


def test_json_parser_type():
    data = {'ka': 'va', 'kb': 'vb', 'kc': '111'}
    req, error = JsonParser(
        Argument('kc', type=int)
    ).parse(data)
    print(f'arg={req}')


def test_json_parser_default():
    data = {'ka': 'va', 'kb': 'vb'}
    req, error = JsonParser(
        Argument('kc', default='default-value')
    ).parse(data)
    print(f'req={req}')


def test_json_parser_required():
    data = {'ka': 'va', 'kb': 'vb'}
    req, error = JsonParser(
        Argument('kc', required=True)
    ).parse(data)
    print(f'req={req}')
    print(f'error={error}')


def test_json_parser_nullable():
    data = {'ka': 'va', 'kb': 'vb', 'kc': ''}
    req, error = JsonParser(
        Argument('kc', nullable=False)
    ).parse(data)
    print(f'req={req}')
    print(f'error={error}')


def test_json_parser_help():
    data = {'ka': 'va', 'kb': 'vb', 'kc': ''}
    req, error = JsonParser(
        Argument('kc', required=True, nullable=False, help='kc 不允许为空')
    ).parse(data)
    print(f'req={req}')
    print(f'error={error}')
