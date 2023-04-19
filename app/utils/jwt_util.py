#!/usr/bin/ python3
# @File    : jwt_util.py
# @Time    : 2022/11/7 11:37
# @Author  : Kelvin.Ye
import jwt


ENCODE_HEADERS = {
    'typ': 'JWT',
    'alg': 'HS256'
}
DECODE_OPTIONS = {'require': ['exp', 'iat'], 'verify_exp': True}


def jwt_encode(payload: dict, secret_key: str) -> str:
    return jwt.encode(payload, secret_key, algorithm='HS256', headers=ENCODE_HEADERS)


def jwt_decode(encoded: str, secret_key: str) -> dict:
    return jwt.decode(encoded, secret_key, algorithms=['HS256'], options=DECODE_OPTIONS)


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
