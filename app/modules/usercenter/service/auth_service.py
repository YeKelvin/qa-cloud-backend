#!/usr/bin/ python3
# @File    : auth_service.py
# @Time    : 2020/6/12 18:30
# @Author  : Kelvin.Ye
from app.modules.usercenter.model import TUserSecretKey
from app.tools.identity import new_id
from app.tools.service import http_service
from app.utils.rsa_util import generate_rsa_key


@http_service
def create_rsa_public_key():
    # 索引编号
    index = new_id()
    # 生成RSA的公钥和秘钥
    rsa_public_key, rsa_private_key = generate_rsa_key()
    # 数据库记录密钥
    TUserSecretKey.insert(
        INDEX=index,
        DATA=str(rsa_private_key, encoding='utf8'),
        record=False
    )
    return {
        'index': index,
        'publicKey': str(rsa_public_key, encoding='utf8')
    }
