#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : token_util.py
# @Time    : 2019/11/7 15:50
# @Author  : Kelvin.Ye

"""
简介：
HMAC是密钥相关的哈希运算消息认证码，HMAC运算利用哈希算法，以一个密钥和一个消息为输入，生成一个消息摘要作为输出。

典型应用：
HMAC的一个典型应用是用在“质疑/应答”（Challenge/Response）身份认证中。

认证流程：
(1) 先由客户端向服务器发出一个验证请求。
(2) 服务器接到此请求后生成一个随机数并通过网络传输给客户端（此为质疑）。
(3) 客户端将收到的随机数提供给ePass，由ePass使用该随机数与存储在ePass中的密钥进行HMAC-MD5运算并得到一个结果作为认证证据传给服务器（此为响应）。
(4) 与此同时，服务器也使用该随机数与存储在服务器数据库中的该客户密钥进行HMAC-MD5运算，如果服务器的运算结果与客户端传回的响应结果相同，则认为客户端是一个合法用户。
"""

import base64
import hmac
import time


def generate_token(key, expire=60):
    """生成token
    :param key:     用户给定的key，需要用户保存以便之后验证token,每次产生token时的key 都可以是同一个key
    :param expire:  最大有效时间，单位为s
    :return:
    """
    ts_str = str(time.time() + expire)
    ts_byte = ts_str.encode('utf-8')
    sha1_tshex_str = hmac.new(key.encode('utf-8'), ts_byte, 'sha1').hexdigest()
    token = ts_str + ':' + sha1_tshex_str
    b64_token = base64.urlsafe_b64encode(token.encode('utf-8'))

    return b64_token.decode('utf-8')


def verify_token(key, token):
    """验证token
    :param key:     用户给定的key，需要用户保存以便之后验证token,每次产生token时的key 都可以是同一个key
    :param token:   token
    :return:
    """
    token_str = base64.urlsafe_b64decode(token).decode('utf-8')
    token_list = token_str.split(':')
    if len(token_list) != 2:
        return False
    ts_str = token_list[0]
    if float(ts_str) < time.time():
        return False
    known_sha1_tsstr = token_list[1]
    sha1 = hmac.new(key.encode("utf-8"), ts_str.encode('utf-8'), 'sha1')
    calc_sha1_tsstr = sha1.hexdigest()
    if calc_sha1_tsstr != known_sha1_tsstr:
        # token certification failed
        return False
    # token certification success
    return True
