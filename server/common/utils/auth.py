#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : auth.py
# @Time    : 2019/11/8 15:07
# @Author  : Kelvin.Ye

"""
JWT

jwt组成:
    header.payload.signature

header:
    - "typ": 令牌的类型，例如 JWT
    - "alg": 使用的散列算法，例如 HMAC SHA256或RSA

payload:
    Registered Claims:
        - "exp"(expiration):    该jwt销毁的时间（unix时间戳）
        - "nbf"(not before):    该jwt的使用时间不能早于该时间（unix时间戳）
        - "iss"(issuer):        发布者的url地址（token签发者）
        - "aud"(audience):      接受者的url地址（token接收者）
        - "iat"(issued at):     该jwt的签发时间（unix时间戳）

    Public Claims:
    Private Claims:

signature:
    JWT的签名算法:
        1、对称加密HMAC【哈希消息验证码】 HS256/HS384/HS512
        2、非对称加密RSASSA【RSA签名算法】  RS256/RS384/RS512
        3、ECDSA【椭圆曲线数据签名算法】 ES256/ES384/ES512
"""

import datetime

import jwt

from server.common.utils import config


class JWTAuth:
    SECRET_KEY = config.get('jwt', 'secret.key')
    EXPIRE_TIME = int(config.get('jwt', 'expire.time'))

    @staticmethod
    def encode_auth_token(user_no, login_time):
        """生成认证Token

        Args:
            user_no:    用户编号
            login_time: 登录时间

        Returns:
            token
        """
        header = {
            'typ': 'JWT',
            'alg': 'HS256'
        }

        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=JWTAuth.EXPIRE_TIME),  # 销毁的时间
            'iat': datetime.datetime.utcnow(),  # 签发时间
            'iss': config.get('jwt', 'issuer'),  # 签发者
            'data': {
                'id': user_no,
                'loginTime': login_time
            }
        }
        token = jwt.encode(payload, JWTAuth.SECRET_KEY, algorithm='HS256', headers=header)
        return str(token, encoding='utf-8')

    @staticmethod
    def decode_auth_token(auth_token) -> dict:
        """验证Token

        Args:
            auth_token:

        Returns:

        Raises:
            jwt.ExpiredSignatureError（token过期）
            jwt.InvalidTokenError（无效token）
        """

        # 取消过期时间验证
        payload = jwt.decode(auth_token, JWTAuth.SECRET_KEY, options={'verify_exp': True})
        if 'data' in payload and 'id' in payload['data']:
            return payload
        else:
            raise jwt.InvalidTokenError
