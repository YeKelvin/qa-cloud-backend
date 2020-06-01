#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : rsa_util
# @Time    : 2020/6/1 11:57
# @Author  : Kelvin.Ye

"""
生成的公私钥文件格式如下
私钥:
-----BEGIN RSA PRIVATE KEY-----
MIICX......./fx7KHM=
-----END RSA PRIVATE KEY-----

公钥:
-----BEGIN PUBLIC KEY-----
MIGDA.......AQAB
-----END PUBLIC KEY-----
"""

import base64

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

# PUBLIC_KEY = rf'-----BEGIN PUBLIC KEY-----\n{}\n-----END PUBLIC KEY-----\n'.format(json['PUBLIC KEY'])
# RIVATE_KEY = rf'-----BEGIN RSA PRIVATE KEY-----\n{}\n-----END RSA PRIVATE KEY-----\n'.format(json['PRIVATE KEY'])

# rsa_public_key = PUBLIC_KEY.encode('utf8')
# rsa_private_key = RIVATE_KEY.encode('utf8')

if __name__ == '__main__':
    message = b"this is test"

    random_generator = Random.new().read
    rsa = RSA.generate(2048, random_generator)

    rsa_private_key = rsa.exportKey()
    rsa_public_key = rsa.publickey().exportKey()

    rsakey = RSA.importKey(rsa_public_key)
    cipher = PKCS1_v1_5.new(rsakey)
    cipher_text = base64.b64encode(cipher.encrypt(message))
    print(cipher_text)

    rsakey = RSA.importKey(rsa_private_key)
    cipher = PKCS1_v1_5.new(rsakey)
    random_generator = Random.new().read
    text = cipher.decrypt(base64.b64decode(cipher_text), None)
    print(text.decode('utf8'))
