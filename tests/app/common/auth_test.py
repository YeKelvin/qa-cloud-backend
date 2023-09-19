#!/usr/bin/ python3
# @File    : test_auth.py
# @Time    : 2019/11/12 16:29
# @Author  : Kelvin.Ye
from datetime import UTC
from datetime import datetime

from app.tools.auth import JWTAuth


def test_auth_token():
    user_no = 'U00000001'
    token = JWTAuth.encode_token(user_no, datetime.now(UTC))

    print(token)
    payload = JWTAuth.decode_token(token)
    print(payload)
