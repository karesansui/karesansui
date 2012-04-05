// This file is part of Karesansui Core.
//
// Copyright (C) 2009-2010 HDE, Inc.
//
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License, or (at your option) any later version.
//
// Authors:
//     Kei Funagayama <kei@karesansui-project.info>
//

/***
 * TRANSLATORS:
 * アイコン付きのアラートを表示する。
 * アイコンの種類は、statusで指定する。
 * statusは、SUCCEED(成功)、CAUTION(警告)、ERROR(エラー)が使用できる。
 * show_alert_msg関数を使用を推奨。
 */
function alert_on(id, status, msg){
    var alt_img = "";
    var alt_cls = "";
    var alt_title = "";

    if(id == '' || status == '' || msg == ''){
        return "";
    }
    
    if(status == 'SUCCEED'){
        alt_title = "${_('SUCCEED')}";
        alt_img = "succeed.gif";
        alt_cls = "succeed-alt";
    } else if(status == 'CAUTION') {
        alt_title = "${_('CAUTION')}";
        alt_img = "alert.gif";
        alt_cls = "caution-alt";
    } else if(status == 'ERROR') {
        alt_title = "${_('ERROR')}";
        alt_img = "alert.gif";
        alt_cls = "error-alt";
    }
    var lmsg = '<div class="alert-bg"><div class="' + alt_cls + '">';
    var msg = '<img src="${ctx.homepath}/static/images/' + alt_img + '" alt="${_("Alert")}" /><pre>' + status + ':  ' + msg + '</pre>';
    var rmsg = '</div><br style="clear:both" /></div>';

    $(id).html(lmsg + msg + rmsg);
    return true;
}

/***
 * TRANSLATORS:
 * アイコン付きのアラートを消す。
 */
function alert_off(_id){
    $(_id).html("");
    return true;
}

/***
 * TRANSLATORS:
 * 任意のメッセージでアラートを表示する。
 * グレーアウト画面があれば、そこにアラートを表示する。
 * グレーアウト画面がなければ、画面の右下にアラートを表示する。
 * msgを与えなければ、全てのアラートを消す。
 * アイコンの種類は、statusで指定する。
 * statusは、SUCCEED(成功)、CAUTION(警告)、ERROR(エラー)が使用できる。
 * statusを与えなければ、ERROR(エラー)が指定される。
 */
function show_alert_msg(msg, status){
    if (msg == "") {
        show_grayout_msg("")
        show_notifications_msg("")
        return true;
    } else {
        if(show_grayout_msg(msg, status) == true){
            return true;
        }
        if(show_notifications_msg(msg, status) == true){
            return true;
        }
        return false;
    }
}

/***
 * TRANSLATORS:
 * グレーアウト画面の上部に任意のメッセージでアイコン付きのアラートを表示する。
 * msgを与えなければ、アラートを消す。
 * アイコンの種類は、statusで指定する。
 * statusは、SUCCEED(成功)、CAUTION(警告)、ERROR(エラー)が使用できる。
 * statusを与えなければ、ERROR(エラー)が指定される。
 */
function show_grayout_msg(msg, status){
    if(typeof(status) == 'undefined') {
        status = "ERROR";
    }

    if($(".grayout-alert").size() == 0){
        return false;
    }

    if (msg == "") {
         alert_off(".grayout-alert");
    } else {
        alert_on(".grayout-alert", status, msg);
        $("#dialog_screen").animate({ scrollTop: 0 }, 'slow');
    }

    return true;
}

/***
 * TRANSLATORS:
 * 画面の右下に任意のメッセージで点滅するメッセージを表示する。
 * msgを与えなければ、アラートを消す。
 * statusがSUCCEED(成功)であれば、点滅するアラートが5秒後に消える。
 * それ以外のstatusであれば、クリックするまで消えない。
 */
function show_notifications_msg(msg, status){
    if(typeof(status) == 'undefined') {
        status = "ERROR";
    }

    if($("#_ajax1_lock").size() == 0){
        return false;
    }

    if (msg == "") {
        $("#_ajax1_lock").hide();
    } else {
        $("#_ajax1_lock .error-message").html('<span style="white-space:pre-wrap">' + msg + '</span>');
        $("#_ajax1_lock").show('pulsate',{times:2});

        if(status == 'SUCCEED'){
            setTimeout(function(){
                $("#_ajax1_lock").hide();
            }, 5000);
        }
    }

    return true;
}
