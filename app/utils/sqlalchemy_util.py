#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : sqlalchemy_util.py
# @Time    : 2020/1/6 17:07
# @Author  : Kelvin.Ye


def paginate(page, page_size):
    offset = (int(page) - 1) * int(page_size)
    limit = int(page_size)
    return offset, limit


class QueryCondition(list):

    def add_fuzzy_match(self, column, value):
        if value is None:
            return
        self.append(column.like(f'%{value}%'))

    def add_fully_match(self, column, value):
        if value is None:
            return
        self.append(column == value)
