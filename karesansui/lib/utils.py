#!/usr/bin/env python
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

""" 
<comment-ja>
ユーティリティ関数群を定義する
</comment-ja>
<comment-en>
Define the utility functions
</comment-en>

@file:   utils.py

@author: Taizo ITO <taizo@karesansui-project.info>

@copyright:    

"""
import string
import os
import os.path
import stat
import random
import subprocess
import shutil
import time
import datetime
import re
import pwd
import grp
import sys
import math
import glob
import fcntl
import gzip

import karesansui
import karesansui.lib.locale

from karesansui import KaresansuiLibException
from karesansui.lib.const import CHECK_DISK_QUOTA
from karesansui.lib.networkaddress import NetworkAddress

def preprint_r(var,indent=2,depth=None,return_var=False):
    import pprint

    pp = pprint.PrettyPrinter(indent=indent,depth=depth)
    if return_var is True:
        return pp.pformat(var)
    else:
        pp.pprint(var)
        return True

def dotsplit(val):
    """<comment-ja>
    ドット(.)区切りで文字列分割する。ドット(.)は)
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    rf = val.rfind('.')
    if rf == -1:
        return val, ''
    else:
        return val[:rf], val[rf+1:]

def toplist(val):
    """<comment-ja>
    リスト型に変換する。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if type(val) is list:
        return val
    else:
        return [val,]
        
def comma_split(s):
    """<comment-ja>
    カンマ(,)単位で文字列分割しリスト型に変換する。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    ret = []
    for y in [x.strip() for x in s.split(',') if x]:
        ret.append(y)
    return ret

def uniq_sort(array):
    """<comment-ja>
    配列の要素をソートし重複した要素を取り除く
    @param array: 配列
    @return: 配列
    @rtype: list
    </comment-ja>
    <comment-en>
    run a unique sort and return an array of sorted

    @param array: list
    @return: list
    </comment-en>
    """
    array = sorted(array)
    #array = [x for i,x in enumerate(array) if array.index(x) == i]
    array = [_x for _x, _y in zip(array, array[1:] + [None]) if _x != _y]
    return array

def dict_ksort(dt):
    """<comment-ja>
    辞書配列をキーを元にソートし重複する

    @param dt: 辞書
    @type dt: dict
    @return: ソート後の辞書配列
    @rtype: dict
    </comment-ja>
    <comment-en>
    run a key sort in dict
    </comment-en>
    """
    new_dict = {}
    for k,v in sorted(dt.items()):
        new_dict[k] = v
    return new_dict

def dict_search(search_key, dt):
    """<comment-ja>
    辞書配列から指定した値に対応するキーを取得する

    @param dt: 辞書
    @type dt: dict
    @return: 取得したキーを要素とする配列
    @rtype: array
    </comment-ja>
    <comment-en>
    Searches the dictionary for a given value and returns the corresponding key.
    </comment-en>
    """
    def map_find(_x, _y):
        if _y == search_key:
            return _x
    def except_None(_z):
        return _z != None
    rlist = list(map(map_find, list(dt.keys()), list(dt.values())))
    return list(filter(except_None, rlist))

def dec2hex(num):
    """<comment-ja>
    整数値を１６進数の文字列に変換する
    @param num: 整数値
    @return: １６進数の文字列
    @rtype: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return "%X" % num

def dec2oct(num):
    """<comment-ja>
    整数値を８進数の文字列に変換する
    @param num:整数値
    @return: ８進数の文字列
    @rtype: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return "%o" % num

def hex2dec(s):
    """<comment-ja>
    １６進数の文字列を整数値に変換する
    @param string:１６進数の文字列
    @return int16
    @rtype: int
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return int(s, 16)

def oct2dec(string):
    """<comment-ja>
    ８進数の文字列を整数値に変換する
    @param string:８進数の文字列
    @rtype: integer
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return int(string, 8)

def float_from_string(string):
    """<comment-ja>
    浮動小数点表記の文字列を数値に変換する
    @param string: 浮動小数点表記
    @rtype: float
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>

    >>> from karesansui.lib.utils import float_from_string
    >>> 
    >>> float_from_string("9.95287e+07")        # 99528700
    99528700.0
    >>> float_from_string("2.07499e+08")        # 207499000
    207499000.0
    >>> float_from_string("-2.07499e+02")       # -207.499
    -207.499
    >>> float_from_string("+2.07499e+02")       # 207.499
    207.499
    >>> float_from_string("+2.07499e-02")       # 0.0207499
    0.0207499
    >>> float_from_string("3.39112632978e+001") # 3391126329780.0
    33.9112632978
    """

    if type(string) != str:
        return False

    regex = re.compile("^([\+\-]?)(([0-9]+|[0-9]*[\.][0-9]+))([eE])([\+\-]?)([0-9]+)$")
    m = regex.match(string)
    if m:
        sign = m.group(1)
        mantissa = float(m.group(2))
        sign_exponent = m.group(5)
        exponent = int(m.group(6))

        data = float(1)

        if sign == "-":
            data = data * -1

        if sign_exponent == "-":
            exponent = -1 * exponent

        data = data * mantissa * (10**exponent)

    else:
        return False

    return data

def ucfirst(string):
    return string[0].upper() + string[1:]

def lcfirst(string):
    return string[0].lower() + string[1:]

def next_number(min,max,exclude_numbers):
    """
    <comment-ja>
    指定範囲内における除外対象整数以外の次の整数を取得する
    
    @param min: 範囲中の最小の整数
    @param max: 範囲中の最大の整数
    @param exclude_numbers: 除外対象整数を要素にもつ配列
    @return: 整数
    @rtype: int
    </comment-ja>
    <comment-en>
    @param min: Minimum interger in specified range
    @param max: Maximum interger in specified range
    @param exclude_numbers: array that has the element of exclusive interger
    @return: Interger
    </comment-en>
    """
    for _x in range(min,max):
      if not _x in exclude_numbers:
        return _x

def isset(string, vars=globals(), verbose=False):
    """
    bool isset(str string  [,bool verbose=False])
    <comment-ja>
    変数名がセットされていることを検査する
    
    @param string: 変数名を示す文字列
    @type string: str
    @param vars: 検査対象の変数配列
    @type vars: dict
    @param verbose: エラーメッセージを表示する場合はTrue
    @type verbose: bool
    @return: 変数名がセットされていればTrue、いなければFalse
    @rtype: bool
    </comment-ja>
    <comment-en>
    Determine if a variable is set.

    @param string: The variable name, as a string. 
    @type string: str
    @param vars: all variables available in scope
    @type vars: dict
    @param verbose: If used and set to True, isset() will output error messages.
    @type verbose: bool
    @return: Returns True if a variable is set, False otherwise. 
    @rtype: bool
    </comment-en>
    """
    retval = False
    try:
        for _k,_v in vars.items():
            exec("%s = _v" % _k)
        exec("%s" % string)
        retval = True
    except NameError as e:
        if verbose is True:
            print(_("Notice: Undefined variable \"%s\"") % str(e.args))
    except KeyError as e:
        if verbose is True:
            print(_("Notice: Undefined index \"%s\"") % str(e.args))
    except Exception as e:
        if verbose is True:
            print(_("Notice: Undefined variable \"%s\"") % str(e.args))
        pass
    return retval

def is_uuid(uuid=None):
    """<comment-ja>
    KaresansuiのUUIDフォーマットに対応しているか。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    uuid_regex = re.compile(r"""^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$""")
    if uuid != None and uuid_regex.match(uuid):
        return True

    return False

def generate_uuid():
    """
    <comment-ja>
    ランダムなUUIDを生成する

    @return: UUID用の16個のバイト要素を持つ配列
    </comment-ja>
    <comment-en>
    Generate UUID

    @return: Array UUID
    </comment-en>
    """
    uuid = []
    for _x in range(0, 16):
      uuid.append(random.randint(0x00,0xff))
    return uuid

def string_from_uuid(uuid):
    """
    <comment-ja>
    UUIDデータを文字列に変換する

    @param uuid: generate_uuid関数等で生成されたUUIDデータ
    @return: UUID文字列
    </comment-ja>
    <comment-en>
    Convert UUID data to string

    @param uuid: UUID data that was generated by certain function like as generate_uuid()
    @return: The string that stands for uuid
    </comment-en>
    """
    tuuid = tuple(uuid)
    return "-".join(["%02x"*4 % tuuid[0:4],
                    "%02x"*2 % tuuid[4:6],
                    "%02x"*2 % tuuid[6:8],
                    "%02x"*2 % tuuid[8:10],
                    "%02x"*6 % tuuid[10:16]
                   ]);

def string_to_uuid(string):
    """
    <comment-ja>
    文字列をUUIDデータに変換する

    @param string: UUID文字列
    @return: UUIDデータ
    </comment-ja>
    <comment-en>
    Convert string to UUID data

    @param string: The string that stands for uuid
    @return: UUID data
    </comment-en>
    """
    string = string.replace('-', '')
    return [ int(string[i : i + 2], 16) for i in range(0, 32, 2) ]

def generate_mac_address(type="XEN"):
    """
    <comment-ja>
    ランダムなMACアドレスを生成する
    (XENなら、00:16:3e:00:00:00 から 00:16:3e:7f:ff:ff の範囲)
    (KVMなら、52:54:00:00:00:00 から 52:54:00:ff:ff:ff の範囲)

    @param type: ハイパーバイザのタイプ (XEN or KVM)
    @return: MACアドレス
    </comment-ja>
    <comment-en>
    Generate random MAC address
    (if hypervisor is XEN, generates address by range between 00:16:3e:00:00:00 and 00:16:3e:7f:ff:ff)
    (if hypervisor is KVM, generates address by range between 52:54:00:00:00:00 and 52:54:00:ff:ff:ff)

    @param type: The type of hypervisor (XEN or KVM)
    @return: The string that stands for MAC address
    </comment-en>
    """
    if type == "KVM":
        mac = [ 0x52, 0x54, 0x00,
                random.randint(0x00, 0xff),
                random.randint(0x00, 0xff),
                random.randint(0x00, 0xff) ]
    else:
        mac = [ 0x00, 0x16, 0x3e,
                random.randint(0x00, 0x7f),
                random.randint(0x00, 0xff),
                random.randint(0x00, 0xff) ]
    return ':'.join(["%02x" % x for x in mac])

def generate_phrase(len,letters=None):
    """<comment-ja>
    ランダムな文字列を生成する

    @param len: 文字列の長さ
    @return: ランダム文字列
    @rtype: str
    </comment-ja>
    <comment-en>
    Generate random string

    @param len: length of string
    @return: The generated string
    @rtype: str
    </comment-en>
    """
    if letters is None:
        letters = string.digits + string.letters + '-.'
    random.seed()
    return ''.join(random.choice(letters) for i in range(len))

def detect_encoding(string,encoding_list=None):
    """
    <comment-ja>
    文字エンコーディングを検出する

    @param string: 検出する文字列データ
    @param encoding_list: エンコーディングのリスト。エンコーディング検出の順番を配列で指定。省略時は、[ 'euc-jp', 'utf-8', 'shift-jis', 'iso2022-jp' ]
    @return: 検出した文字エンコーディング
    </comment-ja>
    <comment-en>
    Detect character encoding

    @param string: The string being detected
    @param encoding_list: list of character encoding. Encoding order will be specified by array. if it is omitted, detect order is [ 'euc-jp', 'utf-8', 'shift-jis', 'iso2022-jp' ]
    @return: The detected character encoding
    </comment-en>
    """
    func = lambda data,encoding: data.decode(encoding) and encoding

    if not encoding_list:
        encoding_list = [ 'euc-jp', 'utf-8', 'shift-jis', 'iso2022-jp' ]

    for encoding in encoding_list:
        try:
            return func(string, encoding)
        except:
            pass

    return None

def execute_command(command_args,user=None,env=None):
    """
    <comment-ja>
    コマンドを実行する

    @param command_args: 実行するコマンドとその引数を要素とする配列
    @param user: 実行するユーザー名 (省略時はgetuidによる)
    @param env:  実行時に適用する環境変数の辞書配列
    @return: 終了ステータスと実行時の出力結果の配列
    </comment-ja>
    <comment-en>
    Execute command

    @param command_args: The array that consists of command name and its arguments.
    @param user: the effective user id 
    @param env:  dictionary of environ variables
    @return: The return status of the executed command
    </comment-en>
    """
    ret = -1
    res = []

    curdir  = os.getcwd()

    if user is None:
        homedir = pwd.getpwuid(os.getuid())[5]
    else:
        try:
            int(user)
            homedir = pwd.getpwuid(int(user))[5]
        except:
            try:
                homedir = pwd.getpwnam(user)[5]
            except:
                homedir = pwd.getpwuid(os.getuid())[5]

    subproc_args = { 'stdin': subprocess.PIPE,
                     'stdout': subprocess.PIPE,
                     'stderr': subprocess.STDOUT,
#                     'shell': True,
                     'cwd': homedir,
                     'close_fds': True,
                   }

    if env is not None:
        subproc_args['env'] = env

    try:
        pp = subprocess.Popen(command_args, **subproc_args)
    except OSError as e:
        #raise KaresansuiLibException("Failed to execute command: %s" % command_args[0])
        return [ret,res]

    (stdouterr, stdin) = (pp.stdout, pp.stdin)
    while True:
        line = stdouterr.readline()
        if not line:
            break
        line = line.rstrip()

        try:
            res.append(str(line, detect_encoding(line)).encode("utf-8"))
        except:
            res.append(line)

    try:
        ret = pp.wait()
    except:
        ret = 0

    return [ret,res]


def pipe_execute_command(commands):
    """
    <comment-ja>
    PIPE付きコマンドを実行する

    @param commands: パイプ付きのコマンドを分割した、配列  example) [['rpm', '-qa'], ['grep', 'karesansui'],]
    @return: 終了ステータスと実行時の出力結果の配列
    </comment-ja>
    <comment-en>
    </comment-en>
    """
    ret = -1
    res = []
    out = []
    for cmd in commands:
        subproc_args = {'stdin': subprocess.PIPE,
                        'stdout': subprocess.PIPE,
                        }
        if 0 < len(out):
            subproc_args['stdin'] = out[len(out)-1]

        pp = subprocess.Popen(cmd, **subproc_args)

        (stdout, stdin) = (pp.stdout, pp.stdin)
        out.append(stdout)
        ret = pp.wait()
    res = out[len(out)-1].read()
    return (ret,res)


def create_file(file, value) :
    """
    <comment-ja>
    ファイルを作成する。

    @param file: 作成するファイル名
    @param value: 書き込む値
    @return: なし
    </comment-ja>
    <comment-en>
    create file

    @param file: The name of generated file
    @param value: The value of generated file
    @return: None
    </comment-en>
    """
    if os.path.exists(file):
        raise KaresansuiLibException("Error: %s already exists" % file)

    fd = open(file, 'w')
    try:
        try:
            fd.write(value)
        except IOError as err:
            raise KaresansuiLibException("IOError: %s" % str(err))
    finally:
        fd.close()

def remove_file(file) :
    """
    <comment-ja>
    ファイルを削除する。

    @param file: 削除するファイル名
    @return: なし
    </comment-ja>
    <comment-en>
    remove file

    @param file: The name of removed file
    @return: None
    </comment-en>
    """
    if not os.path.exists(file):
        raise KaresansuiLibException("Error: %s not exists" % file)

    try:
        os.remove(file)
    except OSError as err:
        raise KaresansuiLibException("OSError: %s" % str(err))

def create_raw_disk_img(file,size,is_sparse=True) :
    """
    <comment-ja>
    rawディスクファイルを生成する

    @param file: 生成するファイル名
    @param size: ファイルサイズ(MB)
    @param sparse: スパースファイル？
    @return: なし
    </comment-ja>
    <comment-en>
    Create raw disk file

    @param file: The name of generated file
    @param size: The size of generated file
    @return: None
    </comment-en>
    """
    if is_sparse is True:
        command_args = [
            "dd",
            "if=/dev/zero",
            "of=%s" % file,
            "seek=%s" % str(size),
            "bs=1M",
            "count=0",
            ]
    else:
        command_args = [
            "dd",
            "if=/dev/zero",
            "of=%s" % file,
            "bs=1M",
            "count=%s" % str(size) ,
            ]

    (rc,res) = execute_command(command_args)
    if rc != 0:
        return None
    return rc

#    if os.path.exists(file):
#        raise KaresansuiLibException("Error: %s already exists" % file)
#
#    try:
#        fd = open(file, 'w')
#        try:
#            fd.truncate(1024L * 1024L * size)
#        except IOError, err:
#            raise KaresansuiLibException("IOError: %s" % str(err))
#    finally:
#        fd.close()

def create_qemu_disk_img(file,size,type="raw") :
    """
    <comment-ja>
    qemu用ディスクイメージファイルを生成する

    @param file: 生成するファイル名
    @param size: ファイルサイズ(MB)
    @param type: ディスクイメージのタイプ raw/qcow/qcow2/cow/vmdk/cloop
    @return: なし
    </comment-ja>
    <comment-en>
    Create qemu disk image file

    @param file: The name of generated file
    @param size: The size of generated file
    @return: None
    </comment-en>
    """
    from karesansui.lib.const import DISK_QEMU_FORMAT
    #available_formats = [ "raw","qcow","qcow2","cow","vmdk","cloop" ]
    available_formats = list(DISK_QEMU_FORMAT.values())

    if type in available_formats:
        command_args = [
            "qemu-img",
            "create",
            "-f",
            type,
            file,
            "%sM" % str(size),
            ]
        (rc,res) = execute_command(command_args)
        if rc != 0:
            return None
    else:
        rc = None

    return rc

def create_disk_img(file,size,type="raw",is_sparse=True) :
    """
    <comment-ja>
    ディスクイメージファイルを生成する

    @param file: 生成するファイル名
    @param size: ファイルサイズ(MB)
    @param type: ディスクイメージのタイプ raw/qcow/qcow2/cow/vmdk/cloop
    @param sparse: スパースファイル？(rawのときのみ)
    @return: なし
    </comment-ja>
    <comment-en>
    Create disk image file

    @param file: The name of generated file
    @param size: The size of generated file
    @return: None
    </comment-en>
    """
    from karesansui.lib.const import DISK_QEMU_FORMAT
    #available_formats = [ "raw","qcow","qcow2","cow","vmdk","cloop" ]
    available_formats = list(DISK_QEMU_FORMAT.values())

    if type in available_formats:
        if type == "raw":
            rc = create_raw_disk_img(file,size,is_sparse)
        else:
            rc = create_qemu_disk_img(file,size,type)
    else:
        rc = None
        raise KaresansuiLibException("Unsupported disk image format. [%s]" % type)

    return rc

def copy_file(src_file,dest_file):
    """
    <comment-ja>
    ファイルをコピーする

    @param src_file: コピー元ファイル名
    @param dest_file: コピー先ファイル名
    @return: コピー先ファイル名
    </comment-ja>
    <comment-en>
    Copy file

    @param src_file: Path to the source file
    @param dest_file: The destination path
    @return: The destination path
    </comment-en>
    """
    #ret = shutil.copy2(src_file, dest_file)
    ret = False
    if os.path.exists(src_file):
        try:
            if dest_file[0] != "/":
                dest_path = "%s/%s" % (os.getcwd(),os.path.dirname(dest_file),)
            else:
                dest_path = os.path.dirname(dest_file)
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            (ret, res) = execute_command(["cp","-rfp",src_file,dest_file])
            if ret == 0:
                ret = True
        except:
            return False
    else:
        return False

    return ret


def copy_file_cb(src,dst,callback=None,sparse=False,each=True):
    default_block_size = 4096

    if type(src) == str:
        src = [src]

    if type(dst) == str:
        dst = [dst]

    if len(src) != len(dst):
        raise

    if each is not True:
        all_bytes = 0
        for _src in src:
            all_bytes = all_bytes + os.path.getsize(_src)

        text = "Copying"
        callback.start(filename=None, size=int(all_bytes), text=text)
        cnt = 0

    i = 0
    all_bytes = 0
    for _src in src:
        try:
            _dst = str(dst[i])
        except:
            _dst = dst[i]

        if os.path.exists(os.path.dirname(_dst)) is False:
            os.makedirs(os.path.dirname(_dst))

        bytes = os.path.getsize(_src)
        all_bytes = all_bytes + bytes

        if each is True:
            text = _("Copying %s") % os.path.basename(_src)
            callback.start(filename=_src, size=int(bytes), text=text)
            cnt = 0


        if os.path.exists(_dst) is False and sparse is True:
            block_size = default_block_size
            fd = None
            try:
                fd = os.open(_dst, os.O_WRONLY|os.O_CREAT)
                os.ftruncate(fd, bytes)
            finally:
                if fd:
                    os.close(fd)
        else:
            block_size = 1024*1024*10

        #nulls = '\0' * default_block_size
        nulls = 0x00 * default_block_size

        src_fd = None
        dst_fd = None
        try:
            try:
                src_fd = os.open(_src, os.O_RDONLY)
                dst_fd = os.open(_dst, os.O_WRONLY|os.O_CREAT)

                while 1:
                    data = os.read(src_fd, block_size)
                    sz = len(data)
                    if sz == 0:
                        if each is True:
                            callback.end(bytes)
                        else:
                            callback.update(all_bytes)
                        break
                    if sparse and nulls == data:
                        os.lseek(dst_fd, sz, 1)
                    else:
                        b = os.write(dst_fd, data)
                        if sz != b:
                            if each is True:
                                callback.end(cnt)
                            else:
                                callback.update(cnt)
                            break
                    cnt += sz
                    if cnt < bytes:
                        callback.update(cnt)
            except OSError as e:
                raise RuntimeError(_("ERROR: copying %s to %s: %s") % (_src,_dst,str(e)))
        finally:
            if src_fd is not None:
                os.close(src_fd)
            if dst_fd is not None:
                os.close(dst_fd)

        i = i + 1
    callback.end(all_bytes)

def move_file(src_file,dest_file):
    """
    <comment-ja>
    ファイルを移動する

    @param src_file: 移動元ファイル名
    @param dest_file: 移動先ファイル名
    @return: 移動先先ファイル名
    </comment-ja>
    <comment-en>
    Copy file

    @param src_file: Path to the source file
    @param dest_file: The destination path
    @return: The destination path
    </comment-en>
    """
    #ret = shutil.copy2(src_file, dest_file)
    ret = False
    if os.path.exists(src_file):
        try:
            if dest_file[0] != "/":
                dest_path = "%s/%s" % (os.getcwd(),os.path.dirname(dest_file),)
            else:
                dest_path = os.path.dirname(dest_file)
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            (ret, res) = execute_command(["mv","-f",src_file,dest_file])
            if ret == 0:
                ret = True
        except:
            return False
    else:
        return False

    return ret

def get_xml_parse(file):
    from xml.dom import minidom

    if os.path.exists(file):
        document = minidom.parse(file)
    else:
        document = minidom.parseString(file)

    return document

def get_xml_xpath(document, expression):
    """
    <comment-ja>
    XPathロケーションパスを評価する

    @param document: xml.dom.minidom.Document
    @param expression: 実行する XPath 式
    @return: 与えられた XPath 式 にマッチするすべてのノードを含む ノード一覧
    </comment-ja>
    <comment-en>
    Evaluates the XPath Location Path in the given string

    @param file: Path to XML file
    @param expression: The XPath expression to execute
    @return: Returns node list containing all nodes matching the given XPath expression
    </comment-en>
    """

    from lxml import etree

    tree = etree.fromstring(document.toxml())

    result = tree.xpath(expression)
    if result:
        return result[0]
    else:
        return None


def get_nums_xml_xpath(document, expression):
    """
    <comment-ja>
    XPathロケーションパスを評価する

    @param file: XMLファイルパス、または、XMLデータそのもの
    @param expression: 実行する XPath 式
    @return: 与えられた XPath 式 にマッチするすべてのノードを含む ノード数
    </comment-ja>
    <comment-en>
    Evaluates the XPath Location Path in the given string

    @param file: Path to XML file
    @param expression: The XPath expression to execute
    @return: Returns the number of node containing all nodes matching the given XPath expression
    </comment-en>
    """
    from lxml import etree

    tree = etree.fromstring(document.toxml())
    result = tree.xpath('count(%s)' % expression)
    return result

def gettimeofday():
    """
    <comment-ja>
    現在の時刻を取得する

    @return: 紀元 (the Epoch: time(2) を参照) からの秒とマイクロ秒
    </comment-ja>
    <comment-en>
    Get current time

    @return: the number of seconds and microseconds since the  Epoch  (see time(2))
    </comment-en>
    """
    d = datetime.datetime.now()
    return int(time.mktime(d.timetuple())),d.microsecond


def load_locale():

    import karesansui
    import gettext
    try:
      t = gettext.translation('messages', karesansui.dirname + "/locale")
    except IOError as err:
      old_lang = os.environ['LANG']
      os.environ['LANG'] = 'en'
      t = gettext.translation('messages', karesansui.dirname + "/locale")
      os.environ['LANG'] = old_lang

    return t.gettext

def get_no_overlap_list(target_list):
    """
    <comment-ja>
    リストから重複要素を取り除く

    @param target_list: 重複要素を取り除きたいリスト
    @return: 重複が取り除かれたリスト(順番は保存されない)
    </comment-ja>
    <comment-en>
    delete overlap element in list

    @param target_list: list that has overlap element
    @return: list that delete overlap element (not keep original number)
    </comment-en>
    """
    return list(set(target_list))

def is_int(val):
    """<comment-ja>
    int型かどうか。
    @return: bool
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    try:
        ret = int(val)
        return True
    except (TypeError, ValueError):
        return False

def is_param(input, name, empty=False):
    """
    <comment-ja>
    リクエストデータ(self.input or web.input)に指定したパラメタが存在しているか。
    @param input: 
    @type input 
    @param
    @type
    @return: bool
    </comment-ja>
    <comment-en>
    TODO: English
    </comment-en>
    """
    try:
        if (name in input) is True:
            if empty is True:
                if is_empty(input[name]) is True:
                    return False
                else: # has (name)key and input[name] is not empty
                    return True
            else: # has (name)key and empty arg is False
                return True
        else: # does not have (name)key
            return False
    except:
        return False

def is_ascii(value):
    for x in range(len(value)):
        # Printable characters ASCII is between 0x20(SP) and 0x7e(~)
        if ord(value[x]) < 0x20 or 0x7e < ord(value[x]):
            return False
    return True

def str2datetime(src, format, whole_day=False):
    """<comment-ja>
    フォーマット(format)に一致した文字列(src)をdatetime型にキャストして
    M D Y のみのdatetimeを取得します。
    
    @param src: 変換文字列
    @type src: str
    @param format: 文字列フォーマット
    @type format: str
    @param whole_day: 一日の最終時刻まで
    @type whole_day: boolean
    @return: datetime型
    @rtype: datetime
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    _t = time.strptime(src, format)
    if whole_day is True:
        target = datetime.datetime(_t.tm_year, _t.tm_mon, _t.tm_mday, 23, 59)
    else:
        target = datetime.datetime(_t.tm_year, _t.tm_mon, _t.tm_mday)
    return target

def unixtime():
    """<comment-ja>
    UTCのエポックタイムを返却します。
    @rtype: float
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return time.time()

def unixtime_str():
    """<comment-ja>
    UTCのエポックタイムを文字列として返却します。
    @rtype: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return "%f" % unixtime()

def getfilesize(filepath):
    """<comment-ja>
    指定されたファイルのサイズを返却します。
    @rtype: long
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return os.stat(filepath)[stat.ST_SIZE]

def getfilesize_str(filepath):
    """<comment-ja>
    指定されたファイルのサイズを文字列で返却します。
    @rtype: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return "%ld" % getfilesize(filepath)

def get_filesize_MB(size):
    """
    <comment-ja>
    サイズ(str)をMBに変換する。
    @param size: サイズ
    @type size: str
    @return: MB
    @rtype: long
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    return int(math.ceil(float(size) / 1024 / 1024))

def replace_None(obj, replace_item):
    """<comment-ja>
    __dict__から要素がNone, あるいは空文字('')のものを指定の要素に置き換えます
    @param __dict__をもつオブジェクト
    @rtype: object
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    for k,v in obj.__dict__.items():
        if v == None or v == '':
            obj.__dict__[k] = replace_item
    return obj

def is_readable(path):
    """<comment-ja>
    指定されたパスが読み込み可能かどうか判定する
    @param path:ファイルパス
    @return: 可能ならTrue、不可能ならFalse
    @rtype: bool
    </comment-ja>
    <comment-en>
    test the readability of path
    </comment-en>
    """
    return os.access(path, os.R_OK)

def is_writable(path):
    """<comment-ja>
    指定されたパスが書き込み可能かどうか判定する
    @param path:ファイルパス
    @return: 可能ならTrue、不可能ならFalse
    @rtype: bool
    </comment-ja>
    <comment-en>
    test the readability of path
    </comment-en>
    """
    return os.access(path, os.W_OK)

def is_executable(path):
    """<comment-ja>
    指定されたパスが実行可能かどうか判定する
    @param path:ファイルパス
    @return: 可能ならTrue、不可能ならFalse
    @rtype: bool
    </comment-ja>
    <comment-en>
    test the readability of path
    </comment-en>
    """
    return os.access(path, os.X_OK)

def r_chown(path,owner):
    """<comment-ja>
    指定されたパス配下のディレクトリのオーナーを再帰的に変更する
    @param path:オーナーを変更したいパス
    @param owner:ユーザー名もしくがユーザーID、「:」で続けてグループを指定可能
    @return: 成功ならTrue、失敗ならFalse
    @rtype: bool
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    owner = str(owner)
    if not os.path.exists(path):
        return False

    if ':' in owner:
        user, group = owner.split(':')
    else:
        user, group = [owner,None ]

    if is_int(user) is not True:
        try:
            pw = pwd.getpwnam(user)
        except:
            return False
    else:
        try:
            pw = pwd.getpwuid(int(user))
        except:
            return False
    uid = pw[2]

    if group == None:
        statinfo = os.stat(path)
        gid = statinfo.st_gid
    else:
        if is_int(group) is not True:
            try:
                gr = grp.getgrnam(group)
            except:
                return False
        else:
            try:
                gr = grp.getgrgid(int(group))
            except:
                return False
        gid = gr[2]

    if os.path.isfile(path) or os.path.islink(path):
        try:
            os.chown(path,uid,gid)
        except:
            return False

    elif os.path.isdir(path):
        try:
            os.chown(path,uid,gid)
        except:
            return False

        for name in os.listdir(path):
            sub_path = os.path.join(path, name)
            r_chown(sub_path,owner)

    return True

def r_chgrp(path,group):
    """<comment-ja>
    指定されたパス配下のディレクトリのグループを再帰的に変更する
    @param path:グループを変更したいパス
    @param group:グループ名もしくがグループID
    @return: 成功ならTrue、失敗ならFalse
    @rtype: bool
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    group = str(group)
    if not os.path.exists(path):
        return False

    statinfo = os.stat(path)
    uid = statinfo.st_uid

    if is_int(group) is not True:
        try:
            gr = grp.getgrnam(group)
        except:
            return False
    else:
        try:
            gr = grp.getgrgid(int(group))
        except:
            return False
    gid = gr[2]

    if os.path.isfile(path) or os.path.islink(path):
        try:
            os.chown(path,uid,gid)
        except:
            return False

    elif os.path.isdir(path):
        try:
            os.chown(path,uid,gid)
        except:
            return False

        for name in os.listdir(path):
            sub_path = os.path.join(path, name)
            r_chgrp(sub_path,group)

    return True

def r_chmod(path,perm):
    """<comment-ja>
    指定されたパス配下のディレクトリのグループを再帰的に変更する
    @param path:グループを変更したいパス
    @param perm:パーミッション
    @return: 成功ならTrue、失敗ならFalse
    @rtype: bool
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """

    perm_regex = re.compile(r"""^(?P<user>[ugo]{0,3})(?P<action>[\+\-])(?P<value>[rwxst]{1,3})$""")

    user_table = {"u":"USR","g":"GRP","o":"OTH"}
    perm_table = {"r":"R","w":"W","x":"X"}

    if not os.path.exists(path):
        return False

    original_perm = perm
    if is_int(perm):
        if type(perm) == str:
            perm = oct2dec(perm)
        new_perm = perm
    else:
        s = os.lstat(path)
        new_perm = stat.S_IMODE(s.st_mode)

        m = perm_regex.match(perm)
        if m:
            user = m.group('user')
            action = m.group('action')
            value = m.group('value')
            if user == "":
                user = "ugo"

            mask_perm = 0
            for k,v in user_table.items():
                if k in user:
                    for k2,v2 in perm_table.items():
                        if k2 in value:
                            exec("bit = stat.S_I%s%s" % (v2,v,))
                            mask_perm = mask_perm | bit


            if "t" in value:
                bit = stat.S_ISVTX
                mask_perm = mask_perm | bit

            if "s" in value:
                if "u" in user:
                    bit = stat.S_ISUID
                    mask_perm = mask_perm | bit
                if "g" in user:
                    bit = stat.S_ISGID
                    mask_perm = mask_perm | bit

            #print "new_perm1:" + dec2oct(new_perm)
            #print "mask_perm:" + dec2oct(mask_perm)
            if action == "-":
                new_perm = new_perm & (~ mask_perm)
            elif action == "+":
                new_perm = new_perm | mask_perm
            #print "new_perm2:" + dec2oct(new_perm)

        else:
            return False

    if os.path.isfile(path) or os.path.islink(path):
        try:
            os.chmod(path,new_perm)
        except:
            return False

    elif os.path.isdir(path):
        try:
            os.chmod(path,new_perm)
        except:
            return False

        for name in os.listdir(path):
            sub_path = os.path.join(path, name)
            r_chmod(sub_path,original_perm)

    return True

def is_dict_value(value, dic):
    """<comment-ja>
    指定された値が辞書にあるか調べる
    @param value:調べたい値
    @param dic:辞書
    @return: 辞書にあればTrue、ないならFalse
    @rtype: bool
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    for key in list(dic.keys()):
        if value == dic[key]:
            return True
    return False

#def is_number(string):
#    """<comment-ja>
#    文字列が数字のみで構成されているか調べる
#    @param string:調べたい文字列
#    @return: 数字のみならTrue、そうでないならFalse
#    @rtype: bool
#    </comment-ja>
#    <comment-en>
#    TODO: English Comment
#    </comment-en>
#    """
#    pattern = re.compile('^[\d]+$')
#    if pattern.match(string):
#        return True
#    return False

def is_empty(string):
    """<comment-ja>
    文字列が空かどうか調べる
    @param string: 調べたい文字列
    @return: 文字列が空ならTrue、そうでないならFalse
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if string and 0 < len(string.strip()):
        return False
    else:
        return True

def uniq_filename():
    """<comment-ja>
    ユニークなファイル名を返却する。
    @param filename: 既存のファイル名
    @return: ユニークなファイル名
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return unixtime_str()

def get_model_name(model):
    """<comment-ja>
    モデル名を返却する。
    @param model: モデル
    @return: モデル名
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if hasattr(model, "__repr__"):
        return repr(model).split("<")[0]
    else:
        return None


def chk_create_disk(target, disk_size):
    """<comment-ja>
    指定されたフォルダ/ファイルが属するパーティションに、指定したサイズのファイルが作成できるか。
    比較単位はMB

    @param target: 調べるファイル/フォルダパス
    @type target: str 
    @param disk_size:
    @return: OK=True | NG=False
    @rtype: bool
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    partition = get_partition_info(target, header=False)
    available = int(partition[3][0])
    if 0 < (available * CHECK_DISK_QUOTA - float(disk_size)):
        return True
    else:
        return False

def get_partition_info(target, header=False):
    """<comment-ja>
    指定したファイル/フォルダパスのパーティション情報(dfコマンドの結果)を取得する。
     - return
       - 0: 'Filesystem' デバイス名
       - 1: '1048576-blocks' 最大サイズ
       - 2: 'Used' 使用サイズ
       - 3: 'Available' ディスク残量
       - 4: 'Capacity' 使用率
       - 5: 'Mounted' マウント先
    値はすべてMB

    @param target: 調べるファイル/フォルダパス
    @type target: str
    @param header: ヘッダ情報を表示するか
    @type header: bool
    @rtype: dict
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    if os.path.exists(target) is True:
        ret = {}
        if header is True:
            pipe = os.popen("LANG=C /bin/df -P -m " + target)
            try:
                data = []
                for line in pipe.readlines():
                    data.append(re.sub(r'[ \t]', ' ', line).split())
            finally:
                pipe.close()

            for i in range(0,6):
                ret[i] = (data[0][i], data[1][i])
        else:
            pipe = os.popen("LANG=C /bin/df -P -m %s | /bin/sed -n 2p" % target)
            try:
                line = pipe.read()
            finally:
                pipe.close()

            data = re.sub(r'[ \t]', ' ', line).split()

            for i in range(0,6):
                ret[i] = (data[i],)

        return ret
    else:
        return None

def uni_force(string, system="utf-8"):
    """
    <comment-ja>
    systemで指定された文字コードもしくは、["ascii", "utf-8", "euc-jp", "cp932", "shift-jis"]で強制的にunicodeへ変換します。

    @param string: 変換文字列
    @type string: str
    @param system: 文字コード
    @type system: str
    @return: Unicode文字列
    @rtype: str
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    if isinstance(string, str) is True:
        return string
    else:
        try:
            return str(string, system)
        except:
            encodings = ["ascii", "utf-8", "euc-jp", "cp932", "shift-jis"]
            for encode in encodings:
                try:
                    return str(string, encode)
                except:
                    pass
            raise KaresansuiLibException("Character code that can be converted to unicode.")

def get_ifconfig_info(name=None):
    """
    <comment-ja>
    ネットワークデバイス情報を取得する

    @param name: 取得したいデバイス名(省略時は全デバイス情報が指定されたとみなす) 「regex:^eth」のようにプレフィックスにregex:を付けると正規表現にマッチしたデバイス名の情報を全て取得できる。
    @return:    デバイス情報が格納されたdict配列
                配列の内容例
                {'eth0': {   'bcast': '172.16.0.255',
                             'device': 'eth0',
                             'hwaddr': '00:1D:09:D7:30:4B',
                             'ipaddr': '172.16.0.10',
                             'ipv6addr': 'fe80::21d:9ff:fed7:304b/64',
                             'link': 'Ethernet',
                             'mask': '255.255.255.0',
                             'metric': '1',
                             'mtu': '1500',
                             'running': True,
                             'scope': 'Link',
                             'up': True,
                             'use_bcast': 'BROADCAST',
                             'use_mcast': 'MULTICAST'}}

    </comment-ja>
    <comment-en>
    Get computer's network interface information

    @param name: network device name
    @return: a dict with: ipaddr, hwaddr, bcast, mask etc...
    @rtype: dict
    </comment-en>
    """
    info = {}

    _ifconfig = '/sbin/ifconfig'
    command_args = [_ifconfig,'-a']

    old_lang = os.environ['LANG']
    os.environ['LANG'] = 'C'
    (ret,res) = execute_command(command_args)
    os.environ['LANG'] = old_lang

    if ret != 0:
        return info

    device_regex = re.compile(r"""^(?P<device>[\S\:]+)\s+Link encap:(?P<link>(\S+ ?\S+))(\s+HWaddr (?P<hwaddr>[0-9a-fA-F:]+))?""")
    ipv4_regex = re.compile(r"""^\s+inet addr:\s*(?P<ipaddr>[0-9\.]+)(\s+Bcast:(?P<bcast>[0-9\.]+))?\s+Mask:(?P<mask>[0-9\.]+)""")
    ipv6_regex = re.compile(r"""^\s+inet6 addr:\s*(?P<ipv6addr>[0-9a-fA-F\:\/]+)\s+Scope:(?P<scope>\S+)""")
    status_regex = re.compile(r"""^\s+((?P<up>UP)\s+)?((?P<use_bcast>(BROADCAST|LOOPBACK))\s+)?((?P<running>RUNNING)\s+)?((?P<use_mcast>(MULTICAST|NOARP))\s+)?MTU:(?P<mtu>[0-9]+)\s+Metric:(?P<metric>[0-9]+)""")

    _info = {}
    for aline in res:
        if aline.strip() == "":

            cidr = None
            netlen = None

            if ipaddr is not None and mask is not None:
                netaddr = NetworkAddress("%s/%s" % (ipaddr,mask,))
                cidr = netaddr.get('cidr')
                netlen = netaddr.get('netlen')

            _info[device] = {
                           "device":device,
                           "link":link,
                           "hwaddr":hwaddr,
                           "ipaddr":ipaddr,
                           "bcast":bcast,
                           "mask":mask,
                           "ipv6addr":ipv6addr,
                           "scope":scope,
                           "up":up,
                           "running":running,
                           "use_bcast":use_bcast,
                           "use_mcast":use_mcast,
                           "mtu":mtu,
                           "metric":metric,
                           "cidr":cidr,
                           "netlen":netlen,
                           }
        m = device_regex.match(aline.decode('utf-8'))
        if m:
            device = m.group('device')
            link = m.group('link')
            hwaddr = m.group('hwaddr')
            ipaddr = None
            bcast = None
            mask = None
            ipv6addr = None
            scope = None
            up = False
            running = False
            use_bcast = None
            use_mcast = None
            mtu = None
            metric = None

        m = ipv4_regex.match(aline.decode('utf-8'))
        if m:
            ipaddr = m.group('ipaddr')
            bcast = m.group('bcast')
            mask = m.group('mask')

        m = ipv6_regex.match(aline.decode('utf-8'))
        if m:
            ipv6addr = m.group('ipv6addr')
            scope = m.group('scope')

        m = status_regex.match(aline.decode('utf-8'))
        if m:
            if m.group('up') == 'UP':
                up = True
            use_bcast = m.group('use_bcast')
            if m.group('running') == 'RUNNING':
                running = True
            use_mcast = m.group('use_mcast')
            mtu = m.group('mtu')
            metric = m.group('metric')

    all_info = dict_ksort(_info)
    #import pprint
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(all_info)

    if name == None:
        return all_info

    regex_regex = re.compile(r"""^regex:(?P<regex>.*)""")
    m = regex_regex.match(name)

    for dev,value in all_info.items():
        if m == None:
            if dev == name:
                info[dev] = value
                return info
        else:
            regex = m.group('regex')
            query_regex = re.compile(r""+regex+"")
            n = query_regex.search(dev)
            if n != None:
                info[dev] = value
    return info

def get_proc_meminfo(path="/proc/meminfo"):
    if os.path.isfile(path) is False:
        return None

    fp = open(path, "r")
    try:
        ret = {}
        for line in fp.readlines():
            val = line.split(":")
            key = re.sub(r'[\t\n]', '', val[0].strip())
            value = re.sub(r'[\t\n]', '', val[1]).strip()
            invalue = value.split(" ")
            if len(invalue) > 1:
                ret[key] = (invalue[0], invalue[1])
            else:
                ret[key] = (invalue[0])

        return ret
    except:
        return None

def get_proc_cpuinfo(path="/proc/cpuinfo"):
    if os.path.isfile(path) is False:
        return None

    fp = open(path, "r")
    try:
        ret = {}
        i = 0
        ret[i] = {}
        for line in fp.readlines():
            if len(line.strip()) <= 0:
                i += 1
                ret[i] = {}
            else:
                val = line.split(":")
                key = re.sub(r'[\t\n]', '', val[0].strip())
                value = re.sub(r'[\t\n]', '', val[1]).strip()
                ret[i][key] = value

        if len(ret[len(ret)-1]) <= 0:
            ret.pop(len(ret)-1)

        return ret
        
    except:
        return None

def get_process_id(command=None,regex=False):
    """
    <comment-ja>
    指定した文字列のプロセスIDを取得する

    @param command: コマンド文字列
    @type command: str
    @param regex: 正規表現による指定かどうか
    @type regex: boolean
    @return: プロセスIDのリスト
    @rtype: list
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>

    >>> from ps_match import get_process_id
    >>> get_process_id("libvirtd",regex=True)
    ['26859']
    >>> get_process_id("/usr/sbin/libvirtd --daemon --config /etc/libvirt/libvirtd.conf --listen --pid-file=/var/run/libvirtd.pid",regex=False)
    ['26859']
    """

    retval = []

    proc_dir = "/proc"
    cmdline_file_glob = "%s/[0-9]*/cmdline" % (proc_dir,)
    for _file in glob.glob(cmdline_file_glob):
        try:
            data = open(_file).read()
            data = re.sub("\0"," ",data)
            pid = os.path.basename(os.path.dirname(_file))
            if regex is False:
                if data.strip() == command:
                    retval.append(pid)
            else:
                if re.search(command,data):
                    retval.append(pid)
        except:
            pass
    return retval

def json_dumps(obj, **kw):
    """
    <comment-ja>
    PythonオブジェクトをJSONオブジェクトに変換する。

    @param obj: Pythonオブジェクト
    @type obj: str or dict or list or tuple or None or bool
    @param kw: 追加引数
    @type kw: str or dict or list or tuple or None or bool
    @return: JSONオブジェクト
    @rtype: str
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    import simplejson as json
    return json.dumps(obj, ensure_ascii=False, encoding="utf-8", **kw)

def is_path(target):
    """
    <comment-ja>
    指定された値が、パス名かどうか

    @param target: 調べるパス名
    @type target: str 
    @return: OK=True | NG=False
    @rtype: bool
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    _path, _file = os.path.split(target)
    if _path != "":
        return True
    else:
        return False

def get_keymaps(dir_path='/usr/share/xen/qemu/keymaps'):
    """<comment-ja>
    指定されたKeymapフォルダのファイル名からKeymapのリストを取得する。
    </comment-ja>
    <comment-en>
    English Comment
    </comment-en>
    """
    ret = []
    if os.path.isdir(dir_path) is True:
        for _file in os.listdir(dir_path):
            if len(_file)==2 or (len(_file)==5 and _file[2:3]=='-'):
                ret.append(_file)
    return sorted(ret)

def findFile(dir, pattern):
    fullPattern = os.path.join(dir,pattern)
    return glob.glob(fullPattern)

def findFileRecursive(topdir=None, pattern="*.*", nest=False, verbose=False):
    allFilenames = list()
    # current dir
    if verbose:
        print("*** %s" %topdir)
    if topdir is None: topdir = os.getcwd()
    filenames = findFile(topdir, pattern)
    if verbose:
        for filename in [os.path.basename(d) for d in filenames]:
            print("   %s" %filename)
    allFilenames.extend(filenames)
    # possible sub dirs
    names = [os.path.join(topdir, dir) for dir in os.listdir(topdir)]
    dirs = [n for n in names if os.path.isdir(n)]
    if verbose:
        print("--> %s" % [os.path.basename(d) for d in dirs])
    if len(dirs) > 0:
        for dir in dirs:
            filenames = findFileRecursive(dir, pattern, nest, verbose)
            if nest:
                allFilenames.append(filenames)
            else:
                allFilenames.extend(filenames)
    # final result
    return allFilenames

def available_kernel_modules():
    ret = []
    modules_dir = "/lib/modules/%s" % os.uname()[2]
    if os.path.isdir(modules_dir) is True:
        for k in findFileRecursive(modules_dir,"*.ko"):
            ret.append(os.path.basename(k)[0:-3])
        for k in findFileRecursive(modules_dir,"*.o"):
            ret.append(os.path.basename(k)[0:-2])
    ret = sorted(ret)
    ret = [p for p, q in zip(ret, ret[1:] + [None]) if p != q]
    return ret

def loaded_kernel_modules():
    proc_modules = "/proc/modules"
    if os.path.isfile(proc_modules) is False:
        return None

    ret = []
    fp = open(proc_modules, "r")
    try:
        for line in fp.readlines():
            if len(line.strip()) > 0:
                val = line.split(" ")
                ret.append(val[0])
        fp.close()
    except:
        return None

    return ret

def is_loaded_kernel_module(module=None):
    return module in loaded_kernel_modules()

def loaded_kernel_module_dependencies(module=None):
    if not module in loaded_kernel_modules():
        return None

    proc_modules = "/proc/modules"
    if os.path.isfile(proc_modules) is False:
        return None

    ret = []
    fp = open(proc_modules, "r")
    try:
        for line in fp.readlines():
            if len(line.strip()) > 0:
                val = line.split(" ")
                if val[0] == module and val[3] != "-":
                    ret = val[3].split(",")
                    ret.pop()
        fp.close()
    except:
        return None

    return ret

def load_kernel_module(module=None):
    if is_loaded_kernel_module(module):
        return False
    if module in available_kernel_modules():
        command_args = ["/sbin/modprobe",module]
        ret = execute_command(command_args)
        if is_loaded_kernel_module(module) is False:
            return False
    else:
        return False
    return True

def unload_kernel_module(module=None,force=False):
    if is_loaded_kernel_module(module) is False:
        return False
    else:
        if force is True:
            for k in loaded_kernel_module_dependencies(module):
                unload_kernel_module(k,force)
        command_args = ["/sbin/rmmod",module]
        ret = execute_command(command_args)
        if is_loaded_kernel_module(module):
            return False
    return True

def available_virt_mechs():
    """<comment-ja>
    </comment-ja>
    <comment-en>
    get list of usable virtualization mechanisms
    </comment-en>
    """
    ret = []
    if os.access("/proc/xen", os.R_OK):
        ret.append("XEN")
    if is_loaded_kernel_module("kvm"):
        ret.append("KVM")

    return sorted(ret)


def sh_config_read(filename):
    import re
    regex = re.compile("\s*=\s*")
    value_quote_regex = re.compile("\".*\"")

    ret = {}
    try:
        fp = open(filename,"r")
        fcntl.lockf(fp.fileno(), fcntl.LOCK_SH)
        for line in fp.readlines():
            line = line.strip()
            if len(line) <= 0 or line[0] == "#":
                continue
            key, value = regex.split(line,1)
            #ret[key] = value
            value = re.sub(r"^\"(.*)\"$", r"\1", value)
            value = re.sub(r"^'(.*)'$", r"\1", value)
            ret[key] = value
        fcntl.lockf(fp.fileno(), fcntl.LOCK_UN)
        fp.close()
    except:
        ret = False

    return ret

def sh_config_write(filename,opts):
    ret = True

    res = {}
    if type(opts) == dict:
        res = opts
    else:
        for k in dir(opts):
            res[k] = getattr(opts,k)

    try:
        fp = open(filename,"w")
        fcntl.lockf(fp.fileno(), fcntl.LOCK_EX)
        for k,v in res.items():
            if type(v) == str and k[0:2] != "__" and k[0:4] != "pass":
                fp.write("%s = %s\n" % (k, v,))
        fcntl.lockf(fp.fileno(), fcntl.LOCK_UN)
        fp.close()
    except:
        ret = False

    return ret

def available_virt_uris():
    """<comment-ja>
    </comment-ja>
    <comment-en>
    get list of libvirt's uri
    </comment-en>
    """
    from karesansui.lib.const import VIRT_LIBVIRTD_CONFIG_FILE, \
               VIRT_LIBVIRT_SOCKET_RW, VIRT_LIBVIRT_SOCKET_RO, \
               KVM_VIRT_URI_RW, KVM_VIRT_URI_RO, \
               XEN_VIRT_URI_RW, XEN_VIRT_URI_RO

    uris = {}
    mechs = available_virt_mechs()
    if len(mechs) == 0:
        mechs = ['KVM']

    for _mech in mechs:
        hostname = "127.0.0.1"
        if _mech == "XEN":
            uris[_mech] = XEN_VIRT_URI_RW
        if _mech == "KVM":
            if os.path.exists(VIRT_LIBVIRTD_CONFIG_FILE):
                opts = sh_config_read(VIRT_LIBVIRTD_CONFIG_FILE)
                uri_prefix = "qemu"
                uri_suffix = ""
                uri_args = ""

                try:
                    if opts["listen_tcp"] == "1":
                        uri_prefix = "qemu+tcp"
                        try:
                            opts["tcp_port"]
                            port_number = opts["tcp_port"]
                        except:
                            port_number = "16509"
                except:
                    pass

                try:
                    if opts["listen_tls"] == "1":
                        uri_prefix = "qemu+tls"
                        try:
                            opts["tls_port"]
                            port_number = opts["tls_port"]
                        except:
                            port_number = "16514"
                        uri_args += "?no_verify=1"
                        hostname = os.uname()[1]
                except:
                    pass

                try:
                    port_number
                    uri_suffix += ":%s/system%s" % (port_number, uri_args,)
                except:
                    uri_suffix += "/system%s" % (uri_args,)

                #print "%s://%s%s" % (uri_prefix,hostname,uri_suffix,)
                uris[_mech] = "%s://%s%s" % (uri_prefix,hostname,uri_suffix,)
            else:
                uris[_mech] = KVM_VIRT_URI_RW

    return uris

def file_type(file):
    command_args = [ "file", file, ]
    (rc,res) = execute_command(command_args)
    if rc != 0:
        return None
    else:
        return res[0].replace("%s: " % file, "")

def is_vmdk_format(file):
    try:
        f = open(file, "rb")
        return f.read(4) == "KDMV"
    except:
        return False

def is_iso9660_filesystem_format(file):

    retval = False

    magic  = "CD001"
    extra_magic = "EL TORITO SPECIFICATION" # bootable
    offset       = 32769
    label_offset = 32808
    extra_offset = 34823

    if not os.path.exists(file) or os.stat(file).st_size < offset+len(magic):
        return retval

    try:
        regex = re.compile(r"""\S""")
 
        f = open(file,"rb")
        f.seek(offset)
        header = f.read(len(magic))

        if header != magic:
            return retval

        label = ""
        step = 0
        for cnt in range(label_offset, label_offset + 100):
            f.seek(cnt)
            char = f.read(1)
            #print cnt,  
            #print "%x" % ord(char)
            if ord(char) == 0 or char == '\0':
                step = step + 1
                if step == 2:
                    break
            #elif regex.match(char):
            else:
                label += char

        label = label.strip()

        f.seek(extra_offset)
        data = f.read(len(extra_magic))
        if data == extra_magic:
            label += "(bootable)"

        f.close()

        retval = label
    except:
        pass

    return retval

def is_windows_bootable_iso(file):
    retval = False
    regexes = {
      "Windows XP Home"                  :"WXH(CCP|FPP|OEM|VOL|OCCP)_[A-Z]{2}",
      "Windows XP Professional"          :"WXP(CCP|FPP|OEM|VOL|OCCP)_[A-Z]{2}",
      "Windows XP Home (SP1)"            :"XRMH(CCP|FPP|OEM|VOL|OCCP)_[A-Z]{2}",
      "Windows XP Professional (SP1)"    :"XRMP(CCP|FPP|OEM|VOL|OCCP)_[A-Z]{2}",
      "Windows XP Home (SP1a)"           :"X1AH(CCP|FPP|OEM|VOL|OCCP)_[A-Z]{2}",
      "Windows XP Professional (SP1a)"   :"X1AP(CCP|FPP|OEM|VOL|OCCP)_[A-Z]{2}",
      "Windows XP Home (SP2)"            :"VRMH(CCP|FPP|OEM|VOL)_[A-Z]{2}",
      "Windows XP Professional (SP2)"    :"VRMP(CCP|FPP|OEM|VOL)_[A-Z]{2}",
      "Windows XP Home (SP2b)"           :"VX2H(CCP|FPP|OEM|VOL)_[A-Z]{2}",
      "Windows XP Professional (SP2b)"   :"VX2P(CCP|FPP|OEM|VOL)_[A-Z]{2}",
      "Windows XP Home (SP3)"            :"GRTMH(CCP|FPP|OEM|VOL)_[A-Z]{2}",
      "Windows XP Home K (SP3)"          :"GRTMHK(CCP|FPP|OEM|VOL)_[A-Z]{2}",
      "Windows XP Home KN (SP3)"         :"GRTMHKN(CCP|FPP|OEM|VOL)_[A-Z]{2}",
      "Windows XP Professional (SP3)"    :"GRTMP(CCP|FPP|OEM|VOL)_[A-Z]{2}",
      "Windows XP Professional K (SP3)"  :"GRTMPK(CCP|FPP|OEM|VOL)_[A-Z]{2}",
      "Windows XP Professional KN (SP3)" :"GRTMPKN(CCP|FPP|OEM|VOL)_[A-Z]{2}",
      "Windows XP from Dell"             :"XP2_(PER|PRO)_ENG",
      "Windows 7 Professional"           :"WIN_7_PROFESSIONAL",
      "Windows 7"                        :"WIN7",
     }
    label = is_iso9660_filesystem_format(file)
    if label is not False:
        for k,v in regexes.items():
            regex_str = "%s.*\(bootable\)" % v
            regex = re.compile(regex_str)
            if regex.search(label):
                retval = k
                break
    return retval

def is_linux_bootable_iso(file):
    retval = False
    regexes = {
      "Asianux"               :"Asianux",
      "MIRACLE LINUX \\1.\\2" :"MLSE([0-9])([0-9])",
      "Turbolinux"            :"Turbolinux",
      "Fedora Core \\1"       :"^FC/([0-9\.]*)",
      "Fedora \\1 \\2"        :"^Fedora ([0-9\.]+) (i386|x86_64)",
      "CentOS \\2"            :"CentOS( \-_)([0-9].[0-9])",
      "Red Hat Enterprise Linux \\2 \\3":"RHEL(/|\-)([0-9\.\-U]) (i386|x86_64)",
      "Red Hat Linux/\\1"     :"Red Hat Linux/(.+)",
      "openSUSE-\\1.\\2"      :"^SU(1[0-3])([0-9])0.00",
      "Debian \\1"            :"^Debian (.+)",
      "Buildix"               :"^Buildix",
      "Ubuntu \\1"            :"^Ubuntu ([0-9].+)",
      "Ubuntu Server \\1"     :"^Ubuntu-Server (.+)",
     }
    label = is_iso9660_filesystem_format(file)
    if label is not False:
        for k,v in regexes.items():
            regex_str = "%s.*\(bootable\)" % v
            regex = re.compile(regex_str)
            if regex.search(label):
                retval = re.sub(r"""%s\(bootable\)""" % v,k,label).strip()
                break
    return retval

def is_darwin_bootable_iso(file):
    retval = False
    regexes = {
      "DARWIN \\1" :"^DARWIN(.+)",
     }
    label = is_iso9660_filesystem_format(file)
    if label is not False:
        for k,v in regexes.items():
            regex_str = "%s.*\(bootable\)" % v
            regex = re.compile(regex_str)
            if regex.search(label):
                retval = re.sub(r"""%s\(bootable\)""" % v,k,label).strip()
                break
    return retval

def sizeunit_to_byte(string):
    import re
    import math

    unit_map = { "b" : 1024**0, "k" : 1024**1, "m" : 1024**2, "g" : 1024**3 }
    p = re.compile(r"""^(?P<bytes>[\d\.]+)(?P<unit>[gmkb]?)$""", re.IGNORECASE)
    m = p.match(string)
    if not m:
        return None
    size = float(m.group("bytes")) * unit_map.get(m.group("unit").lower(), 1)

    #return math.round(size)
    return int(math.floor(size))

def sizeunit_format(size,unit="b",digit=1):
    import re
    import math

    unit_map = { "b" : 1024**0, "k" : 1024**1, "m" : 1024**2, "g" : 1024**3 }
    string = float (size) / unit_map.get(unit, 1)

    return "%s%c" % (round(string,digit), unit.upper(),)

def get_disk_img_info(file):
    import re

    if not os.path.exists(file):
        return None

    command_args = [
          "qemu-img",
          "info",
          file,
          ]
    (rc,res) = execute_command(command_args)
    if rc != 0:
        ret = {}
        ftype = file_type(file)
        if ftype != None:
            if re.match(r'^QEMU Copy-On-Write disk image version 1', ftype):
                ret["file_format"] = "qcow"
            elif re.match(r'^QEMU Copy-On-Write disk image version 2', ftype):
                ret["file_format"] = "qcow2"
            elif re.match(r'^User-mode Linux COW file, version 2', ftype):
                ret["file_format"] = "cow"
            elif re.match(r'^data', ftype):
                if is_vmdk_format(file):
                    ret["file_format"] = "vmdk"
                else:
                    ret["file_format"] = "raw"
            else:
                ret["file_format"] = "unknown"
        ret["real_size"] = os.path.getsize(file)
        return ret

    else:
        regex = re.compile(":\s*")
        regex_bracket = re.compile(r"""^(?P<unitformat>.+) \((?P<bytes>[0-9\.]+) bytes\)""")
        ret = {}
        for line in res:
            try:
                key, value = regex.split(line,1)
                if key == "file format":
                    ret["file_format"] = value
                elif key == "virtual size":
                    m = regex_bracket.match(value)
                    ret["virtual_size"] = int(m.group("bytes"))
                elif key == "disk size":
                    ret["disk_size"] = sizeunit_to_byte(value)
                elif key == "cluster_size":
                    ret["cluster_size"] = int(value)
            except:
                pass 
        ret["real_size"] = os.path.getsize(file)
        return ret

def array_replace(array, pattern=None, replace=None, mode="og"):

    if type(array) != list:
        return array

    regex_mode = 0
    once_match_only = False
    search_cnt = 1

    cnt = 0
    while cnt < len(mode):
        if mode[cnt] == 'o':
            once_match_only = True
        if mode[cnt] == 'g':
            search_cnt = 0
        if mode[cnt] == 'i':
            regex_mode = re.IGNORECASE

        cnt += 1

    if type(pattern) is str and type(replace) is str:
        pattern = [pattern]
        replace = [replace]

    if type(pattern) is list and type(replace) is list and len(pattern) == len(replace):
        new_array = []
        for k in array:
            cnt = 0
            #print k,
            #print " => ",
            while cnt < len(pattern):
                p = re.compile("%s" % pattern[cnt],regex_mode)
                if p.search(k):
                    k = p.sub(replace[cnt], k, search_cnt) 
                    if once_match_only is True:
                        break
                cnt += 1
            #print k
            new_array.append(k)

        return new_array
    else:
        return array

def file_contents_replace(filename, new_filename, pattern=None, replace=None, mode="og"):

    lines = []
    try:
        fp = open(filename,"r")
        fcntl.lockf(fp.fileno(), fcntl.LOCK_SH)
        for line in fp.readlines():
            lines.append(line)
        fcntl.lockf(fp.fileno(), fcntl.LOCK_UN)
        fp.close()
    except:
        return False

    if len(lines) > 0:
        lines = array_replace(lines,pattern,replace,mode)
        try:
            fp = open(new_filename,"w")
            fcntl.lockf(fp.fileno(), fcntl.LOCK_EX)
            for line in lines:
                fp.write(line)
            fcntl.lockf(fp.fileno(), fcntl.LOCK_UN)
            fp.close()
        except:
            return False

    return True

def get_inspect_stack(prettyprint=False):
    import inspect

    stack_content = [
      'frame obj  ', 'file name  ', 'line num   ',
      'function   ', 'context    ', 'index      ',
    ]
    context, frame = 1, 2

    retval = dict(list(zip(stack_content, inspect.stack(context)[frame])))

    if prettyprint is True:
        preprint_r(retval)

    return retval

def get_dom_list():
    from karesansui.lib.const import VIRT_XML_CONFIG_DIR
    retval = []
    for _name in os.listdir(VIRT_XML_CONFIG_DIR):
        if _name[-4:] == ".xml":
            _path = os.path.join(VIRT_XML_CONFIG_DIR, _name)
            doc = get_xml_parse(_path)
            domain_name = get_xml_xpath(doc,'/domain/name/text()')
            retval.append(domain_name)
    return retval

def get_dom_type(domain):
    from karesansui.lib.const import VIRT_XML_CONFIG_DIR
    retval = None
    _path = os.path.join(VIRT_XML_CONFIG_DIR, domain+".xml")
    if os.path.exists(_path):
        doc = get_xml_parse(_path)
        retval = get_xml_xpath(doc,'/domain/@type')
    return retval

def base64_encode(string=""):
    import base64

    if type(string) == str:
        string = string.encode("utf-8")
    elif type(string) == str:
        pass
    else:
        raise

    return base64.b64encode(string)

def base64_decode(string=""):
    import base64

    if type(string) == str:
        pass
    else:
        raise

    return base64.b64decode(string)

def get_system_user_list():
    """<comment-ja>
    登録されているシステムユーザリストを/etc/passwd形式で取得します。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    info = []
    _getent = '/usr/bin/getent'
    command_args = [_getent,'passwd']

    old_lang = os.environ['LANG']
    os.environ['LANG'] = 'C'
    (ret,res) = execute_command(command_args)
    os.environ['LANG'] = old_lang

    if ret != 0:
        return info

    for user in res:
        info.append(user.decode().split(':'))
    return info

def get_system_group_list():
    """<comment-ja>
    登録されているシステムグループリストを/etc/group形式で取得します。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    info = []
    _getent = '/usr/bin/getent'
    command_args = [_getent,'group']

    old_lang = os.environ['LANG']
    os.environ['LANG'] = 'C'
    (ret,res) = execute_command(command_args)
    os.environ['LANG'] = old_lang

    if ret != 0:
        return {}

    for group in res:
        info.append(group.split(':'))
    return info

def str_repeat(string="",count=1):
    """<comment-ja>
    文字列を繰り返す
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    retval = ""
    for _cnt in range(0,count):
       retval = "%s%s" % (retval,string,)
    return retval

def _php_array_to_python_dict(string=""):
    """<comment-ja>
    PHPのvar_export形式の文字列をpythonの辞書文字列に変換する
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    lines = string.split("\n")

    array_depth = 0

    regex_array_s = " *array *\("
    regex_array_e = " *\)(?P<comma>,?)"
    regex_list    = " *[0-9]+ *=> *(?P<value>.+)"
    regex_dict    = " *(?P<key>'.+') *=> *"

    array_types = []
    _b_array = False
    new_lines = []
    for _aline in lines:
        indent = ""
        if array_depth > 0:
            indent = str_repeat("   ",array_depth-1)
        m_array_s = re.match(regex_array_s,_aline.rstrip())
        m_array_e = re.match(regex_array_e,_aline.rstrip())
        m_list    = re.match(regex_list   ,_aline)
        m_dict    = re.match(regex_dict   ,_aline)
        if m_array_s is not None:
            array_depth = array_depth + 1
            _b_array = True
            continue
        elif m_array_e is not None:
            array_depth = array_depth - 1
            array_type = array_types.pop()
            if array_type == "list":
                new_aline = "%s]%s" % (indent,m_array_e.group('comma'),)
            if array_type == "dict":
                new_aline = "%s}%s" % (indent,m_array_e.group('comma'),)
            _b_array = False
        elif m_list is not None:
            if _b_array is True:
                array_types.append("list")
                new_aline = "%s[" % indent
                new_lines.append(new_aline)
            value = m_list.group('value')
            new_aline = "%s%s" % (indent,re.sub("'","\'",value),)
            _b_array = False
        elif m_dict is not None:
            if _b_array is True:
                array_types.append("dict")
                new_aline = "%s{" % indent
                new_lines.append(new_aline)
            key = m_dict.group('key')
            value = re.sub(regex_dict,"%s:" % key, _aline)
            new_aline = "%s%s" % (indent,value,)
            _b_array = False
        else:
            new_aline = "%s%s" % (indent,_aline,)
            _b_array = False

        new_aline = re.sub("':false,","':False,", new_aline)
        new_aline = re.sub("':true," ,"':True," , new_aline)
        new_lines.append(new_aline)

    #print "\n".join(new_lines)
    return "\n".join(new_lines)
 
def python_dict_to_php_array(dictionary={},var_name=""):
    """<comment-ja>
    pythonの辞書配列をPHPの連想配列(できればvar_export形式)の文字列に変換する
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    import signal

    dict_str = preprint_r(dictionary,return_var=True)
    dict_str = dict_str.replace('{','array(')
    dict_str = dict_str.replace('\':','\' =>')
    dict_str = dict_str.replace('}',')')
    dict_str = dict_str.replace('=> [','=> array(')
    dict_str = dict_str.replace('])','))')
    dict_str = re.sub("\)$",')',dict_str)

    php_start = "<?php\n"
    php_end   = "?>\n"

    # Convert var_export format
    _php = "/usr/bin/php"
    if is_executable(_php):
        _script = "\"<?php var_export(%s); ?>\"" % (re.sub("[\r\n]"," ",dict_str),)
        signal.alarm(10)
        proc = subprocess.Popen(_php,
                   bufsize=1,
                   shell=True,
                   stdin=subprocess.PIPE,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE)

        proc.stdin.write(_script)
        output = proc.communicate()
        ret = proc.wait()
        signal.alarm(0)
        if ret == 0:
            dict_str = "".join(output)
            dict_str = re.sub("^\"","",dict_str)
            dict_str = re.sub("\"$","",dict_str)

    header = php_start;
    if var_name != "":
        header = "%s$%s = " % (header,var_name,)
    footer = php_end

    return "%s%s;\n%s" % (header,dict_str,footer,)

def php_array_to_python_dict(string=""):
    """<comment-ja>
    PHPの連想配列(var_export形式)の文字列をpythonの辞書配列に変換する
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    retval = False

    string = re.sub("^<[\?%](php)?"         ,'' ,string.lstrip())
    string = re.sub("[\?%]>$"               ,'' ,string.rstrip())
    string = re.sub("^\\$[a-zA-Z0-9_]+ *= *",'' ,string.lstrip())
    dict_str = string
    dict_str = dict_str.replace('array('    ,'{')
    dict_str = dict_str.replace('\' =>'     ,'\':')
    dict_str = dict_str.replace(')'         ,'}')
    dict_str = dict_str.replace('=> array(' ,'=> [')
    dict_str = dict_str.replace('))'        ,'])')
    dict_str = re.sub("{'(.*':.*)'}"         ,"['\\1']" ,dict_str)
    dict_str = re.sub("\);"                   ,')',dict_str)
    try:
        exec("retval = %s" % dict_str)
    except:
        try:
            # Read by var_export format
            exec("retval = %s" % _php_array_to_python_dict(string))
        except:
            raise

    return retval

def get_karesansui_version():
    import karesansui
    return karesansui.__version__ + '.' + karesansui.__release__

def get_blocks(d='/dev'):
    """<comment-ja>
    指定したフォルダに存在するブロックデバイス名一覧を取得します。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    ret = []
    for f in os.listdir(d):
        if stat.S_ISBLK(os.stat("%s/%s" % (d, f))[stat.ST_MODE]) is True:
            ret.append(f)

    return set(ret)

def get_hdd_list(_prefix='/dev'):
    """<comment-ja>
    OSで認識しているハードディスク名一覧を取得します。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    from karesansui.lib.const import HDD_TYPES_REGEX
    blocks = get_blocks(_prefix)
    ret = []
    for _type in HDD_TYPES_REGEX:
        _regex = re.compile(_type)
        for _b in blocks:
            if _regex.match(_b):
                ret.append(_b)
    return ret

def get_fs_info():
    """<comment-ja>
    OSで認識しているファイルシステムの情報(dfコマンドの結果)を取得します。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    ret = []
    tmp_dict = {}
    pipe = os.popen("LANG=C /bin/df -m -P")
    try:
        data = []
        for line in pipe.readlines():
            data.append(re.sub(r'[ \t]', ' ', line).split())
    finally:
        pipe.close()

    for i in range(1, len(data)):
        for j in range(0,6):
            tmp_dict[data[0][j]] = data[i][j]

        ret.append(tmp_dict)
        tmp_dict = {}

    return ret

def read_file(filepath):
    """<comment-ja>
    指定されたファイルの中身を取得します。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    ret = ""
    try:
        fp = open(filepath, "r")
        fcntl.lockf(fp.fileno(), fcntl.LOCK_SH)
        for line in fp.readlines():
            ret = ret + line
        fcntl.lockf(fp.fileno(), fcntl.LOCK_UN)
        fp.close()
    except:
        ret = False

    return ret

def create_epochsec(year, month, day, hour=0, minute=0, second=0):
    return str(int(time.mktime(datetime.datetime(year, month, day, hour, minute, second).timetuple())))

def get_hostname():
    import socket
#   return socket.gethostname()
    return socket.getfqdn()

def host2ip(host):
    import socket
    return socket.gethostbyname(host)

def uri_split(uri):
    """
       Basic URI Parser
    """
    import re
    regex = '^(([^:/?#]+):)?(//(([^:]+)(:(.+))?@)?([^/?#:]*)(:([0-9]+))?)?([^?#]*)(\?([^#]*))?(#(.*))?'

    p = re.match(regex, uri).groups()
    scheme, user, passwd, host, port, path, query, fragment = p[1], p[4], p[6], p[7], p[9], p[10], p[12], p[14]

    if not path: path = None
    return { "scheme"  :scheme,
             "user"    :user,
             "passwd"  :passwd,
             "host"    :host,
             "port"    :port,
             "path"    :path,
             "query"   :query,
             "fragment":fragment,
           }

def uri_join(segments,without_auth=False):
    """
       Reverse of uri_split()
    """
    result = ''

    try:
        result += segments["scheme"] + '://'
    except:
        pass

    if without_auth is False:
        try:
            result += segments["user"]
            try:
                result += ':' + segments["passwd"]
            except:
                pass
            result += '@'
        except:
            pass

    try:
        result += segments["host"]
    except:
        pass

    try:
        result += ':' + segments["port"]
    except:
        pass

    try:
        if segments["path"] is None or segments["path"] == "":
            segments["path"] = "/"
        if result != "":
            result += segments["path"]
    except:
        pass

    try:
        result += '?' + segments["query"]
    except:
        pass
    try:
        result += '#' + segments["fragment"]
    except:
        pass

    return result

def locale_dummy(str):
    return str

def symlink2real(symlink):
    """<comment-ja>
    シンボリック先の実体ファイルのファイル名を取得します。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    path = os.path.realpath(symlink)
    filename = os.path.basename(path)
    sfilename = filename.split(".")
    if len(sfilename) < 2:
        return (os.path.dirname(path), sfilename[0], "")
    else:
        name = ""
        for x in range(len(sfilename)-1):
            name = os.path.join(name, sfilename[x])
        return (os.path.dirname(path), name, sfilename[len(sfilename)-1])

def get_filelist(dir_path="/"):
    """<comment-ja>
    指定したディレクトリに存在するファイル名の一覧を取得します。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if os.path.isdir(dir_path):
        filelist = os.listdir(dir_path)
    else:
        filelist = []

    return filelist

def get_bonding_info(name=None):
    """
    <comment-ja>
    bondingデバイス情報を取得する

    @param name: 取得したいデバイス名(省略時は全デバイス情報が指定されたとみなす) 「regex:bond0」のようにプレフィックスにregex:を付けると正規表現にマッチしたデバイス名の情報を全て取得できる。
    @return:    デバイス情報が格納されたdict配列
                配列の内容例
                {'bond0': {  'mode'    : 'fault-tolerance (active-backup)',
                             'primary' : 'eth0',
                             'active'  : 'eth0',
                             'slave'   : ['eth0', 'eth1'],
                          }

    </comment-ja>
    <comment-en>
    Get computer's bonding interface information

    @param name: bonding device name
    @return: a dict with: mode, slave etc...
    @rtype: dict
    </comment-en>
    """
    info = {}
    _info = {}
    _proc_bonding_dir = '/proc/net/bonding'

    mode_regex = re.compile(r"""^Bonding Mode:\s*(?P<mode>.+)""")
    primary_regex = re.compile(r"""^Primary Slave:\s*(?P<primary>eth[0-9]+)""")
    active_regex = re.compile(r"""^Currently Active Slave:\s*(?P<active>eth[0-9]+)""")
    slave_regex = re.compile(r"""^Slave Interface:\s*(?P<slave>eth[0-9]+)""")

    for device in get_filelist(_proc_bonding_dir):
        _info[device] = {}
        _info[device]['slave'] = []
        for aline in read_file("%s/%s" % (_proc_bonding_dir, device)).split("\n"):
            if aline.strip() == "":
                continue

            m = mode_regex.match(aline)
            if m:
                _info[device]['mode'] = m.group('mode')

            m = primary_regex.match(aline)
            if m:
                _info[device]['primary'] = m.group('primary')

            m = active_regex.match(aline)
            if m:
                _info[device]['active'] = m.group('active')

            m = slave_regex.match(aline)
            if m:
                _info[device]['slave'].append(m.group('slave'))

    all_info = dict_ksort(_info)

    if name == None:
        return all_info

    regex_regex = re.compile(r"""^regex:(?P<regex>.*)""")
    m = regex_regex.match(name)

    for dev,value in all_info.items():
        if m == None:
            if dev == name:
                info[dev] = value
                return info
        else:
            regex = m.group('regex')
            query_regex = re.compile(r""+regex+"")
            n = query_regex.search(dev)
            if n != None:
                info[dev] = value
    return info

def get_bridge_info(name=None):
    """
    <comment-ja>
    Bridgeデバイス情報を取得する

    @param name: 取得したいデバイス名(省略時は全デバイス情報が指定されたとみなす)
    @return:    デバイス情報が格納されたdict配列
                配列の内容例
                {'eth0': ['peth0'] }

    </comment-ja>
    <comment-en>
    Get computer's bridge interface information

    @param name: bridge device name
    @return: a dict with: bridge name
    @rtype: dict
    </comment-en>
    """
    info = {}

    _sys_bridge_dir_tpl = '/sys/class/net/%s/bridge'
    _sys_brif_dir_tpl = '/sys/class/net/%s/brif'

    if_list = get_ifconfig_info()

    for dev in if_list:
        if os.path.exists(_sys_bridge_dir_tpl % (dev)):
            if os.path.exists(_sys_brif_dir_tpl % (dev)):
                info[dev] = get_filelist(_sys_brif_dir_tpl % (dev))

    if name is not None:
        if name in info:
            return info[name]

    return info


def get_pwd_info():
    """
    <comment-ja>
    全てのユーザ情報を取得する
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return pwd.getpwall()

def get_grp_info():
    """
    <comment-ja>
    全てのグループ情報を取得する
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    return grp.getgrall()

def get_filesystem_info():
    """
    <comment-ja>
    使用できるファイルシステムを取得する
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    ret = []
    _filesystem_path = "/etc/filesystems"
    nodev_regex = re.compile("^nodev")

    data = read_file(_filesystem_path)
    if data:
        for line in data.split("\n"):
            line = line.strip()
            if line == "":
                continue
            if nodev_regex.match(line):
                continue

            ret.append(line)

    return ret

def karesansui_database_exists():
    from karesansui.db import get_session
    from karesansui.db.model.user import User
    session = get_session()
    try:
        email = session.query(User).first().email
    except:
        return False
    return True

class ReverseFile(object):
    def __init__(self, fp):
        self.fp = fp
        if isinstance(self.fp ,gzip.GzipFile):
            self.fp.readlines()
            self.end = self.fp.size
            self.fp.seek(self.end)
        else:
            self.fp.seek(0, 2)
            self.end = self.fp.tell()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.fp.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.end == 0:
            raise StopIteration

        start = self.end - 2
        while start >= 0:
            self.fp.seek(start)
            if self.fp.read(1) == '\n':
                end = self.end
                self.end = start
                return self.fp.read(end - start)
            start -= 1

        end = self.end + 1
        self.end = 0
        self.fp.seek(0)
        return self.fp.read(end)

    def readline(self):
        return next(self)

    def fileno(self):
        return self.fp.fileno()

    def close(self):
        return self.fp.close()

reverse_file = ReverseFile

if __name__ == '__main__':
    pass
