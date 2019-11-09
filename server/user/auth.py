#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : auth.py
# @Time    : 2019/11/8 15:07
# @Author  : Kelvin.Ye
import datetime
import time

import jwt
from flask import jsonify, request

from server.user.model import TUser
from server.utils import config


class Auth:
    SECRET_KEY = config.get('jwt', 'secret.key')

    @staticmethod
    def encode_auth_token(user_no):
        """生成认证Token

        header:
            - "typ": 令牌的类型，例如 JWT
            - "alg": 使用的散列算法，例如 HMAC SHA256或RSA

        payload:
            Registered Claims:
                - "exp"(expiration):    该jwt销毁的时间（unix时间戳）
                - "nbf"(not before):    该jwt的使用时间不能早于该时间（unix时间戳）
                - "iss"(issuer):        发布者的url地址（token签发者）
                - "aud"(audience):      接受者的url地址（token接收者）
                - "iat"(issued at):     该jwt的发布时间（unix时间戳）

            Public Claims:
            Private Claims:

        signature:

        JWT的签名算法:
            1、对称加密HMAC【哈希消息验证码】 HS256/HS384/HS512
            2、非对称加密RSASSA【RSA签名算法】  RS256/RS384/RS512
            3、ECDSA【椭圆曲线数据签名算法】 ES256/ES384/ES512

        :param user_no: userNo
        :return: token
        """
        header = {
            'typ': 'JWT',
            'alg': 'HS256'
        }

        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=10),
            'iat': datetime.datetime.utcnow(),
            'iss': config.get('jwt', 'issuer'),
            'data': {
                'id': user_no
            }
        }
        return jwt.encode(payload, Auth.SECRET_KEY, algorithm='HS256', headers=header)

    @staticmethod
    def decode_auth_token(auth_token):
        """验证Token

        :param auth_token:
        :return: int | str
        :except: jwt.ExpiredSignatureError（token过期） | jwt.InvalidTokenError（无效token）
        """

        # 取消过期时间验证
        payload = jwt.decode(auth_token, Auth.SECRET_KEY, options={'verify_exp': False})
        if 'data' in payload and 'id' in payload['data']:
            return payload
        else:
            raise jwt.InvalidTokenError

    @staticmethod
    def authenticate(username, password):
        """用户登录，登录成功返回token，将登录时间写入数据库；登录失败返回失败原因

        :param username:
        :param password:
        :return: json
        """
        user_info = TUser.query.filter_by(username=username).first()
        if user_info is None:
            return jsonify(false_return('', '找不到用户'))
        else:
            if TUser.check_password(TUser, user_info.password, password):
                login_time = int(time.time())
                user_info.login_time = login_time
                user_info.update()
                token = Auth.encode_auth_token(user_info.id)
                return jsonify(true_return(token.decode(), '登录成功'))
            else:
                return jsonify(false_return('', '密码不正确'))

    @staticmethod
    def identify():
        """用户鉴权

        :return: list
        """
        auth_header = request.headers.get('Authorization')
        if auth_header:
            auth_token_arr = auth_header.split(" ")
            if not auth_token_arr or auth_token_arr[0] != 'JWT' or len(auth_token_arr) != 2:
                result = false_return('', '请传递正确的验证头信息')
            else:
                auth_token = auth_token_arr[1]
                payload = Auth.decode_auth_token(auth_token)
                if not isinstance(payload, str):
                    user = TUser.get(TUser, payload['data']['id'])
                    if user is None:
                        result = false_return('', '找不到该用户信息')
                    else:
                        if user.login_time == payload['data']['login_time']:
                            result = true_return(user.id, '请求成功')
                        else:
                            result = false_return('', 'Token已更改，请重新登录获取')
                else:
                    result = false_return('', payload)
        else:
            result = false_return('', '没有提供认证token')
        return result


def true_return(data, msg):
    return {
        "status": True,
        "data": data,
        "msg": msg
    }


def false_return(data, msg):
    return {
        "status": False,
        "data": data,
        "msg": msg
    }


if __name__ == '__main__':
    # user_no = '111'
    # token = Auth.encode_auth_token(user_no)
    # print(token)
    t = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1NzMyNzE3NzIsImlhdCI6MTU3MzI3MTc2MiwiaXNzIjoia2VuIiwiZGF0YSI6eyJpZCI6IjExMSJ9fQ.pvngyr929XmpeGpzVJmVJ-LurkQwodg-wRNCQPf54M4'
    payload = Auth.decode_auth_token(t)
    print(payload)
