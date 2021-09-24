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
        - exp(expiration):    该jwt销毁的时间（unix时间戳）
        - nbf(not before):    该jwt的使用时间不能早于该时间（unix时间戳）
        - iss(issuer):        发布者的url地址（token签发者）
        - aud(audience):      接受者的url地址（token接收者）
        - iat(issued at):     该jwt的签发时间（unix时间戳）

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

from app.utils import config
from app.utils.log_util import get_logger
from app.utils.time_util import timestamp_to_utc8_datetime

log = get_logger(__name__)


class JWTAuth:
    SECRET_KEY = config.get('jwt', 'secret.key')
    EXPIRE_TIME = int(config.get('jwt', 'expire.time'))

    @staticmethod
    def encode_auth_token(user_no, issued_at):
        """生成认证Token

        Args:
            user_no:    用户编号
            issued_at:  签发时间

        Returns:
            token
        """
        header = {
            'typ': 'JWT',
            'alg': 'HS256'
        }

        payload = {
            'exp': timestamp_to_utc8_datetime(issued_at) + datetime.timedelta(days=0, seconds=JWTAuth.EXPIRE_TIME),
            'iat': issued_at,
            'iss': config.get('jwt', 'issuer'),
            'data': {
                'id': user_no
            }
        }
        token = jwt.encode(payload, JWTAuth.SECRET_KEY, algorithm='HS256', headers=header)
        return token

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

        payload = jwt.decode(auth_token, JWTAuth.SECRET_KEY, algorithms=['HS256'], options={'verify_exp': True})
        if 'data' in payload and 'id' in payload['data']:
            return payload
        else:
            raise jwt.InvalidTokenError
