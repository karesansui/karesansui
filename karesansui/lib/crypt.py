# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#

import random
try:
  from hashlib import sha1 as sha
except:
  import sha
  from sha import sha

def sha1encrypt(v):
    """<comment-ja>
    自動生成したsaltを加えた文字列をSHA1で暗号化します。
    @param v: SHA1で暗号化する文字列
    @type v: str
    @rtype: str, str
    @return: SHA1で暗号化された文字列, salt
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    salt = ''
    for x in xrange(0,16):
        salt += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

    r = sha(v+salt).hexdigest()
    return r, salt

def sha1compare(target, plain, salt=''):
    """<comment-ja>
    SHA1で暗号化された文字列と平文+saltを比較します。
    @param target: SHA1で暗号化された文字列
    @type target: str
    @param plain: 比較対象の平文
    @type plain: str
    @param salt: salt
    @type salt: str
    @rtype: bool
    @return: 一致すればTrue, 不一致ならばFalseを返却します。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    x = sha(plain+salt).hexdigest()
    if target == x:
        return True
    else:
        return False

if __name__ == '__main__':
    """Testing
    """
    word = 'password'
    print 'word=' + word
    v, salt = sha1encrypt(word)
    print 'encrypt=' + v
    print 'salt=' + salt
    if sha1compare(v, word, salt) is True:
        print 'Success'
    else:
        print 'Failure'
