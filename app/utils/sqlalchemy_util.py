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

    def __init__(self, *agrs):
        super().__init__()
        for arg in agrs:
            self.add_table(arg)

    def add_table(self, table):
        if table:
            self.append(table.DEL_STATE == 0)

    def like(self, column, value):
        """模糊匹配"""
        if value:
            self.append(column.like(f'%{value}%'))

    def equal(self, column, value):
        """完全匹配"""
        if value:
            self.append(column == value)
