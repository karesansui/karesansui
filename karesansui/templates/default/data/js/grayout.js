// This file is part of Karesansui Core.
//
// Copyright (C) 2012 HDE, Inc.
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.
//
// Authors:
//     Kei Funagayama <kei@karesansui-project.info>
//

function grayout_view(type, url, title, reflush, async_flag){

    var async_flag = set_async_flag(async_flag);

    if($("div[class*='ui-dialog']").size() != 0){
        $("div[class*='ui-dialog']").remove();
    }

    var dialog_screen_html = ' \
<div id="dialog_screen"> \
    <div id="dialog_loading" align="center"> \
        <div style="padding-top:150px;">&nbsp;</div><img src="${ctx.homepath}/static/images/now-loading.gif" alt="Now Loading" /> \
    </div> \
</div>  \
'

    $('#screen').html(dialog_screen_html);

    var timer = setTimeout(function(){
        $('#dialog_screen').dialog({
            width: 800,
            height:520,
            modal: true,
            resizable: false,
            title: title,
            buttons:{
                'close':function() {$(this).dialog('close');}
            },
            beforeclose: function() {
                renew_all(false);
                $("#cluetip").hide();
            },
            open: function() {
                $("div[class*='ui-dialog-titlebar']").corner("top");
                $("div[class*='ui-dialog-buttonpane']").corner("bottom");
                $("div[class*='ui-dialog-buttonpane'] > button").hide();
                $.ajax({
                    type: type,
                    url: url,
                    async: async_flag,
                    success: function(data) {
                        $('#dialog_screen').append('<div class="grayout-alert">');
                        $('#dialog_screen').append(data);
                        $('#dialog_loading').hide();
                        $("div[class*='ui-dialog-buttonpane']").prepend($("div.grayout-footer"));
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown) {
                        _error(XMLHttpRequest, textStatus, errorThrown);
                        $('#dialog_screen').dialog('close');
                    }
                });
            }
        });
    }, 500);

    g_main_url = reflush;
    return timer;
}

function delete_dialog(id, url, param, reflush, button, message){
    if($("div[class*='ui-dialog']").size() != 0){
        $("div[class*='ui-dialog']").remove();
        $('#screen').append('<div id="' + id.slice(1) + '"></div>');
    }

    if (message) {
        $(id).text(message);        
    } else {
        $(id).text("${_('Do you really want to remove the target?')}");
    }

    var _click_flag = false;

    var dialog_delete_button_html = '\
            <a href="#" name="dialog_delete_button" id="dialog_delete_button" class="button dialog_button">\
                <span class="button-left">&nbsp;</span><span class="button-right">${_('Delete')}</span>\
            </a>';
    var dialog_cancel_button_html = '\
            <a href="#" name="dialog_cancel_button" id="dialog_cancel_button" class="button dialog_button">\
                <span class="button-left">&nbsp;</span><span class="button-right">${_('Cancel')}</span>\
            </a>';

    $(id).dialog({
        width: 400,
        modal: true,
        resizable: false,
        title: "${_('Confirm')}",
        open: function() {
            $("div[class*='ui-dialog-titlebar']").corner("top");
            $("div[class*='ui-dialog-buttonpane']").corner("bottom");

            $("div[class*='ui-dialog-buttonpane'] button").hide();
            $("div[class*='ui-dialog-buttonpane']").append(dialog_delete_button_html);
            $("div[class*='ui-dialog-buttonpane']").append(dialog_cancel_button_html);
        },
        close: function(event, ui){
            if(_click_flag == false){
                _click_flag = true;
                $(".ui-dialog-buttonpane button").attr("disabled","disabled");
                if(button){
                    tool_reset(button);
                }
                $(this).dialog("close");
            }
        },
        buttons:{
            ${'dummy'} : function() {
            }
        }
    });

    $('#dialog_delete_button').click(function(){
        if(_click_flag == false){
            _click_flag = true;
            $.remove(url,
                param,
                function(data, status){
                    if (status == "success") {
                        g_main_url = reflush;
                        renew_all(false);
                        show_alert_msg("${_('Was removed.')}", "SUCCEED");
                    }
                }
            );
            $(id).dialog("close");
        }
    });

    $('#dialog_cancel_button').click(function(){
        if(_click_flag == false){
            _click_flag = true;
            if(button){
                tool_reset(button);
            }
            $(id).dialog("close");
        }
    });

    button_effect("#dialog_delete_button");
    button_effect("#dialog_cancel_button");

    
}

function apply_dialog(id, url, param, reflush, button, message, method_type){
    if(typeof(method_type) == 'undefined'){
        method_type = 'PUT';
    }

    if(method_type == 'PUT'){
        ajax_func = $.put;
    } else {
        ajax_func = $.post;
    }

    if($("div[class*='ui-dialog']").size() != 0){
        $("div[class*='ui-dialog']").remove();
        $('#screen').append('<div id="' + id.slice(1) + '"></div>');
    }

    if (message) {
        $(id).text(message);        
    } else {
        $(id).text("${_('OK to apply changes?')}");
    }

    var _click_flag = false;

    var dialog_apply_button_html = '\
            <a href="#" name="dialog_apply_button" id="dialog_apply_button" class="button dialog_button">\
                <span class="button-left">&nbsp;</span><span class="button-right">${_('Apply')}</span>\
            </a>';
    var dialog_cancel_button_html = '\
            <a href="#" name="dialog_cancel_button" id="dialog_cancel_button" class="button dialog_button">\
                <span class="button-left">&nbsp;</span><span class="button-right">${_('Cancel')}</span>\
            </a>';
    

    $(id).dialog({
        width: 400,
        modal: true,
        resizable: false,
        title: "${_('Confirm')}",
        open: function() {
            $("div[class*='ui-dialog-titlebar']").corner("top");
            $("div[class*='ui-dialog-buttonpane']").corner("bottom");

            $("div[class*='ui-dialog-buttonpane'] button").hide();
            $("div[class*='ui-dialog-buttonpane']").append(dialog_apply_button_html);
            $("div[class*='ui-dialog-buttonpane']").append(dialog_cancel_button_html);
        },
        close: function(event, ui){
            if(_click_flag == false){
                _click_flag = true;
                $(".ui-dialog-buttonpane button").attr("disabled", "disabled");
                if(button){
                    tool_reset(button);
                }
                $(this).dialog("close");
            }
        },
        buttons:{
            ${'dummy'}:function() {
            }
        }
    });

    $('#dialog_apply_button').click(function(){
        if(_click_flag == false){
            _click_flag = true;
            ajax_func(url,
                param,
                function(data, status){
                    if (status == "success") {
                        g_main_url = reflush;
                        renew_all(false);
                        show_alert_msg("${_('Was applied.')}", "SUCCEED");
                    }
                }
            );
            $(id).dialog("close");
        }
    });

    $('#dialog_cancel_button').click(function(){
        if(_click_flag == false){
            _click_flag = true;
            if(button){
                tool_reset(button);
            }
            $(id).dialog("close");
        }
    });

    button_effect("#dialog_apply_button");
    button_effect("#dialog_cancel_button");

}
