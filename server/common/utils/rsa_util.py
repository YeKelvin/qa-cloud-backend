#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : rsa_util
# @Time    : 2020/6/1 11:57
# @Author  : Kelvin.Ye
import base64

from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


def generate_rsa_key() -> (bytes, bytes):
    """生产RSA公钥和私钥
    """
    rsa = RSA.generate(2048, Random.new().read)
    public_key = rsa.publickey().exportKey()
    private_key = rsa.exportKey()
    return public_key, private_key


def encrypt_by_rsa_public_key(content, public_key):
    """通过RSA公钥加密

    :param content:     加密内容
    :param public_key:  RSA公钥
    :return:            密文
    """
    rsakey = RSA.importKey(public_key)
    cipher = PKCS1_v1_5.new(rsakey)
    ciphertext = base64.b64encode(cipher.encrypt(content))
    return ciphertext


def decrypt_by_rsa_private_key(ciphertext, private_key):
    """通过RSA私钥解密

    :param ciphertext:  密文
    :param private_key: RSA私钥
    :return:            明文
    """
    rsakey = RSA.importKey(private_key)
    cipher = PKCS1_v1_5.new(rsakey)
    plaintext = cipher.decrypt(base64.b64decode(ciphertext), None)
    return plaintext.decode('utf8')
