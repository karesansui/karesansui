#! /usr/bin/env python
# -*- coding: utf-8 -*-`
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

from karesansui import KaresansuiTemplateException
from karesansui.lib.utils import get_system_user_list, get_system_group_list

def view(text, _):
    """<comment-ja>
    mako#render時にUNDEFINEDが発生する可能性がある場合に利用してください。
    UNDEFINEDが発生した場合は、国際化された_('Undefined')が返却されます。
    @param text: 表示する文字列
    @type text: str
    @param _: translationオブジェクト
    @type _:gettext.GNUTranslations
    @rtype: str
    @return: 表示する文字列
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    from mako.runtime import UNDEFINED

    if text is UNDEFINED:
        return ""
    elif not text:
        return _('Undefined')
    else:
        return text

def img_status(status, prefix='', extra=''):
    """<comment-ja>
    ゲストOSのステータスを元に指定された形式で出力します。
    @param status: libvirt status
    @type status: int
    @param prefix: 固定画像名の先頭につけるプレフィックスファイル名　example) prefix='bar-' result 'bar-nostate.png'
    @type prefix: str
    @param extra: imgタグに別途追記する属性
    @type extra: str
    @return: form#img
    @rtype: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    import web
    from karesansui.lib.virt.virt import VIR_DOMAIN_NOSTATE, \
         VIR_DOMAIN_RUNNING, \
         VIR_DOMAIN_BLOCKED, \
         VIR_DOMAIN_PAUSED, \
         VIR_DOMAIN_SHUTDOWN, \
         VIR_DOMAIN_SHUTOFF, \
         VIR_DOMAIN_CRASHED

    _img_tpl = '<img src="' + web.ctx.homepath + '/static/images/%s" alt=""' + extra + ' />'

    if status == VIR_DOMAIN_NOSTATE:
        return _img_tpl % (prefix+'nostate.png')
    elif status == VIR_DOMAIN_CRASHED:
        return _img_tpl % (prefix+'crashed.png')
    elif status == VIR_DOMAIN_SHUTOFF:
        return _img_tpl % (prefix+'shutoff.png')
    elif status == VIR_DOMAIN_SHUTDOWN:
        return _img_tpl % (prefix+'shutdown.png')
    elif status == VIR_DOMAIN_PAUSED:
        return _img_tpl % (prefix+'paused.png')
    elif status == VIR_DOMAIN_BLOCKED:
        return _img_tpl % (prefix+'blocked.png')
    elif status == VIR_DOMAIN_RUNNING:
        return _img_tpl % (prefix+'running.png')
    else:
        raise KaresansuiTemplateException("Not specify the status.")

def str_status(status, _):
    """<comment-ja>
    ゲストOSステータスの名称を出力します。
    @param status: libvirt status
    @type status: int
    @param _: translationオブジェクト
    @type _:gettext.GNUTranslations
    @return: 名称
    @rtype: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    import web
    from karesansui.lib.virt.virt import VIR_DOMAIN_NOSTATE, \
         VIR_DOMAIN_RUNNING, \
         VIR_DOMAIN_BLOCKED, \
         VIR_DOMAIN_PAUSED, \
         VIR_DOMAIN_SHUTDOWN, \
         VIR_DOMAIN_SHUTOFF, \
         VIR_DOMAIN_CRASHED

    if status == VIR_DOMAIN_NOSTATE:
        return _('NOSTATE')
    elif status == VIR_DOMAIN_CRASHED:
        return _('CRASHED')
    elif status == VIR_DOMAIN_SHUTOFF:
        return _('SHUTOFF')
    elif status == VIR_DOMAIN_SHUTDOWN:
        return _('SHUTDOWN')
    elif status == VIR_DOMAIN_PAUSED:
        return _('PAUSED')
    elif status == VIR_DOMAIN_BLOCKED:
        return _('BLOCKED')
    elif status == VIR_DOMAIN_RUNNING:
        return _('RUNNING')
    else:
        raise KaresansuiTemplateException("Not specify the status.")

def str_attribute(attribute):
    """<comment-ja>
    マシン属性の名称を出力します。
    @param attribute: マシン属性値
    @type attribute: int
    @return: 名称
    @rtype: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    from karesansui.lib.const import MACHINE_ATTRIBUTE

    for key, value in list(MACHINE_ATTRIBUTE.items()):
        if attribute == value:
            return key
    else:
        raise KaresansuiTemplateException("Not specify the attribute.")

def locale_hypervisor(hypervisor, _):
    """<comment-ja>
    Japanese Comment
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    from karesansui.lib.const import MACHINE_HYPERVISOR
    if (hypervisor in list(MACHINE_HYPERVISOR.values())) is True:
        for x in list(MACHINE_HYPERVISOR.items()):
            if hypervisor == x[1]:
                return _(x[0])

        raise KaresansuiTemplateException("Hypervisor is not defined.")
    else:
        raise KaresansuiTemplateException("Hypervisor is not defined.")

def locale_bool(bool, _):
    """<comment-ja>
    Bool型を国際化された名称で出力します。
    @param bool: True/False
    @type bool: bool
    @param _: translationオブジェクト
    @type _:gettext.GNUTranslations
    @return: 名称
    @rtype: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    import web

    if bool is True:
        return _('Enabled')
    elif bool is False:
        return _('Disabled')
    else:
        raise KaresansuiTemplateException("Bool not specified.")

def lnewline(text):
    from mako.runtime import UNDEFINED
    if text is UNDEFINED:
        return ""
    ret = ""
    for t in text:
        ret += t + '\n'
    return ret

def clipping(text, num):
    """<comment-ja>
    テキストが任意の文字数を超えていたら、
    省略したテキストに … を加えたものをを返却する。
    そうでないなら、テキストをそのまま返却する。
    半角は1文字、全角は2文字としてカウントする。

    @param text: 省略するテキスト
    @type text: str
    @param num: 省略する文字数
    @type num: int
    @return: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    from mako.runtime import UNDEFINED
    if text is UNDEFINED:
        return ""

    ret = text

    count = 0
    for i in range(len(text)):
        if ord(text[i]) <= 255:
            count += 1;
        else:
            count += 2;

        if num < count:
            ret = text[0:i] + "…"
            break

    return ret

def replace_empty(value, replace_value):
    """<comment-ja>
    値がNone、または、空文字('')のものを指定の値に置き換えます
    @param value: 置き換え元の要素
    @type value: str
    @param replace_value: 置き換え先の要素
    @type replace_value: str
    @return: 存在するマシン名
    @rtype: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if value == None or value == "":
        return replace_value
    else:
        return value

def get_exist_machine_name(machines, _):
    """<comment-ja>
    存在するマシン名を返却します。
    マシン名が複数あるときはカンマ区切りで返却します。
    マシン名が存在しない、または、マシンが削除されているときは、「Unregistered」を返却します。
    @param machines: マシンの配列
    @type machines: list
    @param _: translationオブジェクト
    @type _:gettext.GNUTranslations
    @return: 存在するマシン名
    @rtype: str
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    if machines is None:
        return _('N/A')

    _names = []
    for machine in machines:
        if machine.is_deleted is False:
            _names.append(machine.name)
    
    if len(_names) > 0:
        return  ",".join(_names)
    else:
        return  _('N/A')

def userid2realname(userid):
    users = get_system_user_list()
    for user in users:
        if userid == user[2]:
            return user[0]
    return userid

def groupid2realname(groupid):
    groups = get_system_group_list()
    for group in groups:
        if groupid == group[2]:
            return group[0]
    return groupid

def autounit(t, unit):
    _t = float(t)
    now = 0
    _u = 1
    while True:
        ret = int(_t / _u)
        if 0 == ret or now == len(unit):
            break
        _u *= 1024
        now += 1

    if 0 < now:
       _u /= 1024 
       now -= 1

    if len(unit) < now:
        return (_t, unit[0])
    return (_t/_u, unit[now])

def view_autounit(_b, unit=('B','KB','MB','GB','TB', 'PB', 'EB'), decimal_point=0, print_unit=False):
    ret = autounit(_b, unit)
    formmat = "%." + str(decimal_point) + "f"
    view_number = formmat % ret[0]
    view_unit = ret[1]

    if print_unit is True:
        return "%s%s" % (view_number, view_unit)
    else:
        return "%s" % (view_number)

def megaunit(t, now_unit):
    UNIT = ('B','KB','MB','GB','TB', 'PB', 'EB')
    MEGA_POS = 2

    _t = float(t)
    _u = 1

    now_pos = 0
    for i in range(len(UNIT)):
        if now_unit == UNIT[i]:
            now_pos = i
            break

    if MEGA_POS <= now_pos:
        for i in range(now_pos - MEGA_POS):
            _u *= 1024
        return _t * _u
    else:
        for i in range(MEGA_POS - now_pos):
            _u *= 1024
        return _t / _u

def view_megaunit(_b, now_unit, decimal_point=0, print_unit=False):
    ret = megaunit(_b, now_unit)
    formmat = "%." + str(decimal_point) + "f"

    view_number = formmat % ret

    if print_unit is True:
        return "%sMB" % (view_number)
    else:
        return "%s" % (view_number)

def total_progress(jobs):
    complete_progress = len(jobs) * 100

    sum_progress = 0
    for job in jobs:
        sum_progress += job.progress

    return int(float(sum_progress) / float(complete_progress) * 100)

def newline2br(text):
    import re
    return re.compile(r"[\r\n]+").sub('<br/>', text)
