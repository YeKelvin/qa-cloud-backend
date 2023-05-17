#!/usr/bin python3
# @File    : element_context.py
# @Time    : 2023-05-17 11:11:12
# @Author  : Kelvin.Ye
from contextvars import ContextVar


# 脚本加载时的配置，用于递归间的传递
loads_config = ContextVar('loads-config')

# 脚本加载时的缓存，用于递归间的传递
loads_cache = ContextVar('loads-cache')

# 脚本加载时的配置器，用于递归间的传递
loads_configurator = ContextVar('loads-configurator')
