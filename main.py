#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : main.py
# @Time    : 2019/11/7 11:18
# @Author  : Kelvin.Ye
from server.app import create_app
from server.common.utils.log_util import get_logger

log = get_logger(__name__)
app = create_app()

# TODO: 改用.env文件配置环境
# https://dormousehole.readthedocs.io/en/latest/cli.html
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
