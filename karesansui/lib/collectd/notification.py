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
collectdからデータを受け取り、アクションを起こすかどうか判断する

アクションあり：メール送信用、シェル実行用のモジュールへデータを投げる
アクションなし：そのまま終了(リターンいらない)

Example: collectd.d/python.conf
----- snip ----- snip ----- snip -----
# "LoadPlugin python" だけだと、システムのpythonライブラリが使用できない
# 下記のように"<LoadPlugin python>" でGlobalsパラメータの設定が必要
<LoadPlugin python>
        Globals true
</LoadPlugin>

<Plugin python>
        ModulePath "/usr/lib/python2.6/site-packages/karesansui/lib/collectd"
        Encoding utf-8
        LogTraces true
        #Interactive true
        Import "notification"

        <Module "notification">
                CountupDBPath "/var/lib/karesansui/notify_count.db"
                LogFile "/var/log/collectd/notification.log"
                # 0 none, 1 errors, 2 informations, 4 debug, 7 all
                LogLevel 1
                Environ "KARESANSUI_CONF=/etc/karesansui/application.conf" "
FOOBAR=foo:bar" "LANG=ja_JP.utf-8"
        </Module>
</Plugin>
----- snip ----- snip ----- snip -----

Example: collectd.d/filter.conf
----- snip ----- snip ----- snip -----
# Messageオプションの値をdictの文字列にすることで、pythonスクリプト側で
# exec()の展開をすると各種データが取得できるようになる。
LoadPlugin match_regex
LoadPlugin match_value
LoadPlugin target_notification

PostCacheChain     PostTestChain
<Chain "PostTestChain">
    Target "write"
    <Rule "memory_cached_exceeded">
        <Target "notification">
            #Message            "Oops, the %{plugin} %{type_instance} memory_size is currently %{ds:value}!"
            Message            "{'host':'%{host}','plugin':'%{plugin}','plugin_instance':'%{plugin_instance}','type':'%{type}','type_instance':'%{type_instance}','ds_value':'%{ds:value}','msg':'shikiichi wo koemashita!!'}"
            Severity           "WARNING"
        </Target>
        <Match "regex">
            TypeInstance       "^cached$"
            Plugin             "^memory$"
        </Match>
        <Match "value">
            Satisfy            "Any"
            Min                47000000
        </Match>
    </Rule>
</Chain>
----- snip ----- snip ----- snip -----

Example: collectd.d/threshold.conf
----- snip ----- snip ----- snip -----
# 閾値を越えるとnotificationプラグインには、以下のメッセージが送られる。
# Host %{host}, plugin %{plugin} type %{type} (instance {%type_instance}):
# Data source "{%ds.name}" is currently {%ds.value}.
# 1. That is (below|above) the (failure|warning) threshold of ({%threshold_min}|{%thresold_max})%?.
# 2. That is within the (failure|warning) region of {%threshold_min}%? and {%threshold_max}%?.
<Threshold>
    <Plugin "df">
        <Type "df">
            DataSource "used"
            WarningMax 10
            FailureMax 20
            Percentage true
            Persist true
        </Type>
    </Plugin>
    <Plugin "load">
        <Type "load">
            DataSource "shortterm"
            WarningMax    0.01
            FailureMax    0.40
            Persist true
        </Type>
    </Plugin>
</Threshold>
----- snip ----- snip ----- snip -----
"""

import collectd
import os, sys, types, time, os.path, re, fcntl

search_paths = ["/usr/lib/python2.6","/usr/lib/python2.6/site-packages"]
for _path in search_paths:
    if os.path.exists(_path):
        sys.path.insert(0, os.path.join(_path))

from karesansui import __version__, __release__, __app__
from karesansui.lib.const            import COUNTUP_DATABASE_PATH, \
                                            KARESANSUI_SYSCONF_DIR
from karesansui.lib.collectd.countup import CountUp
from karesansui.lib.utils            import ucfirst

NOTIF_FAILURE = 1<<0
NOTIF_WARNING = 1<<1
NOTIF_OKAY    = 1<<2

CHECK_CONTINUATION = 1<<0
CHECK_HITCOUNT     = 1<<1
CHECK_SPAN         = 1<<2
CHECK_ALL          = CHECK_CONTINUATION | CHECK_HITCOUNT | CHECK_SPAN

ACTION_LOG    = 1<<0
ACTION_MAIL   = 1<<1
ACTION_SCRIPT = 1<<2
ACTION_ALL    = ACTION_LOG | ACTION_MAIL | ACTION_SCRIPT

AppName = "%s %s-%s" % (ucfirst(__app__),__version__,__release__,)
optional_data = {
                'AppName' : AppName,
                }

"""
notifyオブジェクト(printの結果)
インスタンス名はプラグインによっては無い場合がある

type=%s
type_instance=%s
plugin=%s
plugin_instance=%s
host=%s
message=%s
severity=%i
time=%lu
"""

countup_db_path = COUNTUP_DATABASE_PATH
logfile         = "/dev/null"
loglevel        = 1
interval        = 10
environ         = {"KARESANSUI_CONF":"/etc/karesansui/application.conf"}
uniq_id         = None

mail_server     = "localhost"
mail_port       = 25

def config(cfg):
    global countup_db_path
    global logfile
    global loglevel
    global interval
    global environ

    for child in cfg.children:
        if child.key == "CountupDBPath":
            collectd.debug( "[config] config arg set key %s: %s" % ( child.key, child.values[0] ) )
            countup_db_path = child.values[0]

        if child.key == "LogFile":
            collectd.debug( "[config] config arg set key %s: %s" % ( child.key, child.values[0] ) )
            logfile = child.values[0]

        if child.key == "LogLevel":
            collectd.debug( "[config] config arg set key %s: %s" % ( child.key, child.values[0] ) )
            loglevel = int(child.values[0])

        if child.key == "Environ":
            for _value in child.values:
                collectd.debug( "[config] config arg set key %s: %s" % ( child.key, _value ) )
                pieces = _value.split("=",1)
                environ[pieces[0]] = pieces[1]

def init():
    global countup_db_path
    global logfile
    global interval
    global environ

    """
    if not os.path.exists(countup_db_path):
        collectd.error( "Can't find CountupDBPath at %s, disabling plugin" % (countup_db_path))
    """

    try:
        from karesansui.lib.conf import read_conf
        modules = ["collectd"]
        dop = read_conf(modules)
        interval = int(dop.cdp_get("collectd",["Interval"]))
    except:
        pass

def append_log(string,level=1):
    global logfile
    global loglevel
    global uniq_id

    try:
        string = "[%f] %s" % (uniq_id,str(string),)
    except:
        string = "[%f] %s" % (uniq_id,string,)

    from karesansui.lib.collectd.utils import append_line
    if loglevel & level:
        append_line(logfile,string)

def notification(notify=None, data=None):
    global countup_db_path
    global logfile
    global loglevel
    global interval
    global environ
    global uniq_id

    ########################################################
    # 拡張環境変数をセット
    ########################################################
    for _k,_v in environ.iteritems():
        os.environ[_k] = _v

    # 関数読み込み
    from karesansui.lib.collectd.utils import query_watch_data

    ########################################################
    # データを展開
    ########################################################
    if data is types.DictType:
        for _k,_v in data.iteritems():
            if _v is types.StringType:
                exec("%s = '%s'" % (_k,_v,))
            else:
                exec("%s = %s" % (_k,_v,))
    try:
        loglevel
    except:
        pass

    ########################################################
    # システムのログ
    ########################################################
    # logging
    uniq_id = time.time()

    append_log("###################################################",7)
    append_log("countup_db_path: %s" % (countup_db_path,) ,4)
    append_log("logfile        : %s" % (logfile,)         ,4)
    append_log("interval       : %d" % (interval,)        ,4)
    append_log("environ        : %s" % (environ,)         ,4)
    append_log("data           : %s" % (data,)            ,4)
    append_log("",4)


    ########################################################
    # notifyデータから各種値を取得
    ########################################################
    plugin           = notify.plugin
    plugin_instance  = notify.plugin_instance
    type             = notify.type
    type_instance    = notify.type_instance
    host             = notify.host
    severity         = notify.severity
    message          = notify.message
    now              = notify.time
    now_str = time.strftime("%c",time.localtime(now))

    # logging
    append_log("plugin         : %s" % (plugin,)           ,7)
    append_log("plugin_instance: %s" % (plugin_instance,)  ,7)
    append_log("type           : %s" % (type,)             ,7)
    append_log("type_instance  : %s" % (type_instance,)    ,7)
    append_log("host           : %s" % (host,)             ,7)
    append_log("severity       : %s" % (severity,)         ,7)
    append_log("message        : %s" % (message,)          ,7)
    append_log("now            : %s" % (now_str,)          ,4)
    append_log("",4)
    append_log("notify         : %s" % (str(dir(notify)),) ,4)
    """ comment
    append_log("collectd       : %s" % (str(dir(collectd)),)              ,4)
    append_log("collectd.Config: %s" % (str(dir(collectd.Config)),)       ,4)
    append_log("collectd.Notifi: %s" % (str(dir(collectd.Notification)),) ,4)
    append_log("collectd.Values: %s" % (str(dir(collectd.Values)),)       ,4)
    append_log("",4)
    """

    ########################################################
    # messageを展開、ds.xxxxをdata_valueとして取り出す
    ########################################################
    percentage = False

    # messageを展開、ds.xxxxをds_xxxとして取り出す
    # Filterの時はdict文字列をexec展開して抽出
    if message[0:2] == "{'":
        try:
            exec("ds_value = %s['ds_value']" % message)
            exec("msg      = %s['msg']"      % message)
            exec("extras   = %s['dict']"     % message)
        except:
            pass

        # dictの設定があれば extra_<key> = <value> で変数展開
        try:
            extras
            for _k,_v in extras.iteritems():
                exec("extra_%s = %s" % (_k,_v,))
        except:
            pass

    # messageを展開、ログからds_valueに取り出す
    # Thresholdの時はログの文字列から正規表現でデータを抽出
    else:
        msg = message
        regex  = "^Host (?P<host>.+), plugin (?P<plugin>.+)( \(instance (?P<plugin_instance>.+)\))? type (?P<type>.+)( \(instance (?P<type_instance>.+)\))?: "
        regex += "Data source \"(?P<ds_name>.+)\" is currently (?P<ds_value>.+)\. "
        regex += "That is (below|above) the (failure|warning) threshold of (?P<ts_value>[\-0-9\.]+)(?P<percent_flag>%?)\."

        m = re.match(regex,message)
        if m:
            ds_name  = m.group('ds_name')
            ds_value = m.group('ds_value')
            ts_value = m.group('ts_value')
            if m.group('percent_flag') == "%":
                percentage = True

        # メッセージの(msg 以下のdict文字列をparamsに展開する
        regex = ". \(msg (?P<msg_dict>{.+})"
        m = re.search(regex,message)
        if m:
            exec("params = %s" % m.group('msg_dict'))
            try:
                ds_name = params["ds"]
            except:
                pass

    # ds_valueが浮動小数点形式の文字列なら数値に変換
    try:
        from karesansui.lib.utils import float_from_string
        _ret = float_from_string(ds_value)
        if _ret is not False:
            ds_value = float(_ret)
        else:
            ds_value = float(ds_value)
    except:
        ds_value = None

    try:
        msg
    except:
        msg  = "Host %s, plugin %s type %s (instance %s)\): " % (host,plugin,type,type_instance,)
        msg += "Data source is currently %s\." % (ds_value)

    # logging
    append_log("msg            : %s" % (msg,)        ,4)
    try:
        append_log("ds_name        : %s" % (ds_name,),4)
        append_log("ds_value       : %f" % (ds_value,)   ,4)
        append_log("ts_value       : %f" % (ts_value,)   ,4)
    except:
        pass
    append_log("percentage     : %s" % (percentage,) ,4)
    append_log("",4)

    ########################################################
    # watchデータベースからマッチしたデータを取得
    ########################################################
    ########################################################
    # watchデータベースからマッチしたアクション条件を取得
    ########################################################

    """
    # !! テストデータ !!
    # 1分間に5回以上、または、連続５回ヒットしたらアクションを起こす例
    # かつ、1.5分間は同じアクションは起こさない
    checks = CHECK_ALL
    check_hitcount     = 5
    check_seconds      = 1   * 60
    check_continuation = 5
    check_span         = 1.5 * 60
    """

    checks = CHECK_CONTINUATION | CHECK_SPAN
    #check_hitcount     = 5
    #check_seconds      = 1   * 60
    check_continuation = 60
    check_span         = 60 * 60 * 6

    watch_data = query_watch_data(plugin,plugin_instance,type,type_instance,ds_name,host=host)
    append_log("watch_data     : %s" % (str(watch_data),) ,4)

    watch_column = [ 'name',
                     'check_continuation',
                     'check_span',
                     'warning_value',
                     'warning_script',
                     'warning_mail_body',
                     'is_warning_percentage',
                     'is_warning_script',
                     'is_warning_mail',
                     'failure_value',
                     'failure_script',
                     'failure_mail_body',
                     'is_failure_percentage',
                     'is_failure_script',
                     'is_failure_mail',
                     'okay_script',
                     'okay_mail_body',
                     'is_okay_script',
                     'is_okay_mail',
                     'notify_mail_from',
                     'notify_mail_to']
    try:
        for column_name in watch_column:
            exec("%s = watch_data[0]['%s']" % (column_name,column_name,))
            exec("_var = %s" % (column_name,))
            append_log("%s: %s"  % (column_name,_var)   ,4)
    except:
        append_log("Error: cannot get watch data." ,1)
        return
        #sys.exit(0)

    if severity == NOTIF_OKAY:
        watch_script    = okay_script
        watch_mail_body = okay_mail_body
        watch_is_script = is_okay_script
        watch_is_mail   = is_okay_mail
        severity_str    = "okay"
    elif severity == NOTIF_WARNING:
        watch_script    = warning_script
        watch_mail_body = warning_mail_body
        watch_is_script = is_warning_script
        watch_is_mail   = is_warning_mail
        severity_str    = "warning"
    elif severity == NOTIF_FAILURE:
        watch_script    = failure_script
        watch_mail_body = failure_mail_body
        watch_is_script = is_failure_script
        watch_is_mail   = is_failure_mail
        severity_str    = "failure"

    # logging
    append_log("watch_script    :%s" % (watch_script,)    ,4)
    append_log("watch_mail_body :%s" % (watch_mail_body,) ,4)
    append_log("watch_is_script :%s" % (watch_is_script,) ,4)
    append_log("watch_is_mail   :%s" % (watch_is_mail,)   ,4)
    append_log("",4)


    ########################################################
    # 前回のヒット時刻を取得(連続しているか判断するため)
    ########################################################
    gategory_key = "%s:%s:%s:%s@%s" % (plugin,plugin_instance,type,type_instance,host)
    countup = CountUp(countup_db_path)
    old_mtime = countup.get(gategory_key,attr="mtime")
    try:
        old_mtime_str = time.strftime("%c",time.localtime(float(old_mtime)))

        # logging
        append_log("old_mtime      : %s" % (old_mtime_str)  ,4)
        append_log("",4)
    except:
        old_mtime = 0
        pass

    ########################################################
    # カウントDBに記録
    ########################################################
    if severity != NOTIF_OKAY:
        countup.up(gategory_key)

        # 何回連続しているか調べる
        # 連続していれば、continuationをインクリメント 
        # いなければ、continuationをリセット
        try:
            old_mtime = int(old_mtime)
            # (インターバル+2)未満のヒットであればインクリメント
            if now < (old_mtime + interval + 2):
                countup.up(gategory_key,attr="continuation")
            else:
                countup.reset(gategory_key,attr="continuation")
        except:
            pass

        (total,hitcount,continuation,since,start,mtime,action) = countup.get(gategory_key)
        since_str = time.strftime("%c",time.localtime(since))
        start_str = time.strftime("%c",time.localtime(start))

        append_log("total          : %d" % (total,)        ,4)
        append_log("hitcount       : %d" % (hitcount,)     ,4)
        append_log("continuation   : %d" % (continuation,) ,4)
        append_log("",4)
        append_log("since          : %s" % (since_str,)    ,4)
        append_log(" sec from since: %d" % (now - since)   ,4)
        append_log("start          : %s" % (start_str,)    ,4)
        append_log(" sec from start: %d" % (now - start)   ,4)
        try:
            append_log("start + seconds: %d" % (start + check_seconds) ,4)
            append_log(" sec to now    : %d" % ((start + check_seconds) - now) ,4)
        except:
            pass
        append_log("since + span   : %d" % (since + check_span)         ,4)
        append_log(" sec to now    : %d" % ((since + check_span) - now) ,4)
        append_log("",4)
        append_log("action         : %d" % (action,) ,4)
        append_log("",4)

        ########################################################
        # アクションを起こすかどうかのチェック
        ########################################################
        do_action = False

        # 連続している回数が許容範囲内であるかチェック
        if checks & CHECK_CONTINUATION:
            if continuation >= check_continuation:
                do_action = True

        # 一定期間(seconds)内のヒット回数制限を超過していないかチェック
        if checks & CHECK_HITCOUNT:
            # 現在から遡って調べる秒数(seconds)の間に既にヒットしている場合
            if now <= (start + check_seconds):
                # ヒット回数と同じ場合 アクションを起こす
                if hitcount == check_hitcount:
                    do_action = True
                    countup.reset(gategory_key,attr="hitcount",value=0)

        # 再アクション禁止期間(span)内に既にアクションを起こしているかチェック
        # 再アクション禁止期間(span)内の場合
        if now <= (since + check_span):
            if do_action is True:
                # 既にアクションを起こしている場合はアクションを起こさない
                if action > 0:
                    do_action = False
        # 過ぎている場合は、totalをリセット
        else:
            countup.reset(gategory_key,attr="action",value=0)
            countup.reset(gategory_key,attr="total",value=0)

    # 正常値に戻ったとき(NOTIF_OKAY)は常にアクションを起こす
    else:
        (total,hitcount,continuation,since,start,mtime,action) = countup.get(gategory_key)
        # 既にアクションを起こしている場合だけアクションを起こす
        if action > 0:
            do_action = True

        # 正常値に戻ったときはhitcountとcontinuationもリセット
        countup.reset(gategory_key,attr="hitcount",value=0)
        countup.reset(gategory_key,attr="continuation")

    # アクションを起こす場合は、totalをリセット
    if do_action is True:
        countup.up(gategory_key,attr="action")
        countup.reset(gategory_key,attr="total")


    # カウントDB書き込み終わり
    countup.finish()

    append_log("do_action      : %s" % (do_action,)   ,4)
    append_log("",4)


    # アクションを起こさない場合は、ここで抜ける
    if do_action is not True:
        append_log("Notice: Action will be not executed. Aborted.",1)
        return
        #sys.exit(0)

    ########################################################
    # アクション呼出開始
    ########################################################

    actions = ACTION_LOG
    try:
        if watch_is_script is True and watch_script != "":
            actions |= ACTION_SCRIPT
    except:
        pass
    try:
        if watch_is_mail is True and watch_mail_body != "":
            actions |= ACTION_MAIL
    except:
        pass

    # 仮りに全てのアクションを例とする
    #actions = ACTION_ALL

    # メッセージを作成
    if severity == NOTIF_OKAY:
        alert_msg = "The value of %s is within normal range again." % (name,)
    elif severity == NOTIF_WARNING:
        alert_msg = "The value of %s (%f) is within the warning region." % (name,ds_value,)
    elif severity == NOTIF_FAILURE:
        alert_msg = "The value of %s (%f) is within the failure region." % (name,ds_value,)

    try:
        ts_value
        if percentage is True:
            alert_msg += " (threshold:%f%%)" % (float(ts_value),)
        else:
            alert_msg += " (threshold:%f)"   % (float(ts_value),)
    except:
        pass

    # ログ書き込み
    if actions & ACTION_LOG:
        from karesansui.lib.collectd.action.log import write_log

        if severity == NOTIF_OKAY:
            priority = "OKAY"
        elif severity == NOTIF_WARNING:
            priority = "WARNING"
        elif severity == NOTIF_FAILURE:
            priority = "FAILURE"

        write_log(alert_msg,priority=priority)
        write_log(msg      ,priority="INFO")
        pass

    # スクリプト実行
    if actions & ACTION_SCRIPT:
        from karesansui.lib.collectd.action.script import exec_script

        script = watch_script
        user   = "root"

        script_retval = False
        try:
            script_retval = exec_script(script=script,user=user,msg=alert_msg,watch_name=name,logfile=logfile)
        except:
            pass

    # メール送信
    if actions & ACTION_MAIL:
        from karesansui.lib.collectd.action.mail import send_mail
        from karesansui.lib.collectd.utils import get_karesansui_config

        try:
            karesansui_config = get_karesansui_config()
            smtp_server = karesansui_config['application.mail.server']
            smtp_port   = int(karesansui_config['application.mail.port'])
        except:
            smtp_server = mail_server
            smtp_port   = mail_port

        recipient   = notify_mail_to
        sender      = notify_mail_from

        try:
            lang = os.environ['LANG'].split('.',1)[0]
            lang = lang.split('_',1)[0]
        except:
            lang = "en"

        if watch_mail_body == "":
            NOTIF_MAIL_TMPL_DIR = KARESANSUI_SYSCONF_DIR + "/template"
            mail_template_file = "%s/%s/collectd_%s_%s.eml" % (NOTIF_MAIL_TMPL_DIR,lang,severity_str,plugin,)
            append_log("mail_template_file: %s" % mail_template_file,1)
            if os.path.exists(mail_template_file):
                watch_mail_body = open(mail_template_file).read()
        append_log("watch_mail_body: %s" % watch_mail_body,1)

        try:
            watch_mail_body = watch_mail_body.encode("UTF-8")
        except:
            pass

        script_result_message = ""
        CRLF = "\r\n"
        if actions & ACTION_SCRIPT:
            script_result_message += CRLF
            script_result_message += CRLF
            if script_retval is False:
                script_result_message += "Error: failed to execute the following script."
                script_result_message += CRLF
                script_result_message += script
                script_result_message += CRLF
            else:
                script_result_message += "Notice: The action script was executed."
                script_result_message += CRLF
                script_result_message += "script return value:%s" % script_retval[0]
                script_result_message += CRLF
                if len(script_retval[1]) > 0:
                    script_result_message += "[Script Output]"
                    script_result_message += CRLF
                    script_result_message += "%s" % CRLF.join(script_retval[1])
                    script_result_message += CRLF

        macros = {}
        macros['app_name']        = AppName
        macros['plugin']          = plugin
        macros['plugin_instance'] = plugin_instance
        macros['type']            = type
        macros['type_instance']   = type_instance
        macros['host']            = host
        macros['severity']        = severity_str
        macros['message']         = message
        macros['time']            = now_str
        macros['script_result_message'] = script_result_message
        try:
            macros['ds']              = ds_name
            macros['current_value']   = ds_value
            macros['threshold_value'] = ts_value
        except:
            pass
        try:
            params
            for _k,_v in params.iteritems():
                exec("macros['%s'] = '%s'" % (_k,str(_v),))
        except:
            pass

        from karesansui.lib.collectd.utils import evaluate_macro
        watch_mail_body = evaluate_macro(watch_mail_body,macros)

        send_mail(recipient=recipient,sender=sender,server=smtp_server,port=smtp_port,message=watch_mail_body,extra_message=script_result_message,watch_name=name,logfile=logfile)
        pass

    """ comment
    collectd.Values(type='cpu',type_instance='steal',
                    plugin='cpu',plugin_instance='0',
                    host='host.example.com',
                    message='Oops, the cpu steal cpu is currently 0!',
                    time=%lu,interval=%i)
    """

collectd.register_config(config)
collectd.register_init(init)
collectd.register_notification(notification,data=optional_data)
