#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : parser.py
# @Time    : 2019/11/7 15:30
# @Author  : Kelvin.Ye
from server.utils.log_util import get_logger

log = get_logger(__name__)


class Argument:
    def __init__(self, name, location, default=None, required=True, type=str, filter=None, help=None, nullable=False):
        self.name = name
        self.location = location
        self.default = default
        self.type = (type,)
        self.required = required
        self.nullable = nullable
        self.help = help


class JsonParser:
    pass
