#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sqlalchemy-util
# @Time    : 2020/1/6 17:07
# @Author  : Kelvin.Ye
from server.common.request import RequestDTO


def paginate(req: RequestDTO):
    offset = (int(req.attr.page) - 1) * int(req.attr.pageSize)
    limit = int(req.attr.pageSize)
    return offset, limit
