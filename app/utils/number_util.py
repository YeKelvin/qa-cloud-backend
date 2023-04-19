#!/usr/bin/ python3
# @File    : number_util.py
# @Time    : 2019/11/7 10:13
# @Author  : Kelvin.Ye


def decimal_to_percentage(decimal: float) -> str:
    """小数转百分比

    Args:
        decimal: 小数

    Returns: 百分比值

    """
    return '%.2f%%' % (decimal * 100)
