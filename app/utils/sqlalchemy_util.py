#!/usr/bin/ python3
# @File    : sqlalchemy_util.py
# @Time    : 2020/1/6 17:07
# @Author  : Kelvin.Ye
from sqlalchemy import or_


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
            self.append(table.DELETED == 0)

    def add(self, condition):
        self.append(condition)

    def like(self, column, value):
        """模糊匹配"""
        if value:
            self.append(column.like(f'%{value}%'))

    def equal(self, column, value):
        """完全匹配"""
        if value:
            self.append(column == value)

    def notequal(self, column, value):
        """完全匹配"""
        if value:
            self.append(column != value)

    def lt(self, column, value):
        """小于(less than)"""
        if value:
            self.append(column < value)

    def le(self, column, value):
        """小于等于(less than or equal to)"""
        if value:
            self.append(column <= value)

    def gt(self, column, value):
        """大于(greater than)"""
        if value:
            self.append(column > value)

    def ge(self, column, value):
        """大于等于(greater than or equal to)"""
        if value:
            self.append(column >= value)

    def in_(self, column, *args):
        if args := [arg for arg in args if arg]:
            self.append(column.in_(*args))

    def notin_(self, column, *args):
        if args := [arg for arg in args if arg]:
            self.append(column.notin_(*args))

    def or_(self, *args):
        self.append(or_(*args))
