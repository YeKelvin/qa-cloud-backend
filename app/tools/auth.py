#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : auth.py
# @Time    : 2019/11/8 15:07
# @Author  : Kelvin.Ye
import datetime

import jwt

from app import config as CONFIG
from app.tools.logger import get_logger
from app.utils.jwt_util import jwt_decode
from app.utils.jwt_util import jwt_encode
from app.utils.time_util import timestamp_to_utc8_datetime


log = get_logger(__name__)


class JWTAuth:
    SECRET_KEY = CONFIG.JWT_SECRET_KEY
    EXPIRE_TIME = int(CONFIG.JWT_EXPIRE_TIME)

    @staticmethod
    def encode_token(user_no, issued_at):
        """生成认证Token

        Args:
            user_no:    用户编号
            issued_at:  签发时间

        Returns:
            token
        """
        payload = {
            'exp': timestamp_to_utc8_datetime(issued_at) + datetime.timedelta(days=0, seconds=JWTAuth.EXPIRE_TIME),
            'iat': issued_at,
            'iss': CONFIG.JWT_ISSUER,
            'data': {
                'id': user_no
            }
        }
        return jwt_encode(payload, JWTAuth.SECRET_KEY)

    @staticmethod
    def decode_token(auth_token) -> dict:
        """验证Token

        Args:
            auth_token:

        Returns:

        Raises:
            jwt.ExpiredSignatureError（token过期）
            jwt.InvalidTokenError（token无效）
        """
        payload = jwt_decode(auth_token, JWTAuth.SECRET_KEY)
        if 'data' in payload and 'id' in payload['data']:
            return payload
        else:
            raise jwt.InvalidTokenError
