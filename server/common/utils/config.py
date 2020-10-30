#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : config.py
# @Time    : 2019/11/7 10:03
# @Author  : Kelvin.Ye
import configparser
import os

__CONFIG_PATH__ = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'config.ini')
)


def get(section, key, filepath=__CONFIG_PATH__) -> str:
    """获取配置文件中的属性值，默认读取config.ini。

    Args:
        section: section名
        key: 属性名
        filepath: 配置文件路径

    Returns:
        属性值
    """
    if not os.path.exists(filepath):
        raise FileExistsError(filepath + ' 配置文件不存在')
    config = configparser.ConfigParser()
    config.read(filepath)
    return config.get(section, key)


def get_project_path():
    """返回项目根目录路径。
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
