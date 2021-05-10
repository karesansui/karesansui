# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2012 HDE, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
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
    salt = str()
    for x in range(0,16):
        salt += random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
 
    r = sha(v.encode('ascii')+salt.encode('ascii')).hexdigest()
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
    print('word=' + word)
    v, salt = sha1encrypt(word)
    print('encrypt=' + v)
    print('salt=' + salt)
    if sha1compare(v, word, salt) is True:
        print('Success')
    else:
        print('Failure')
