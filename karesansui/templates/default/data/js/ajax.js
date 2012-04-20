// This file is part of Karesansui Core.
//
// Copyright (C) 2009-2012 HDE, Inc.
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

if(typeof(jQuery) == "undefined"){
    document.write('<script type="text/javascript" src="${ctx.homepath}/static/lib/jquery.js"><\/script>');
}

// define
$.ajaxSetup({
    timeout: 0,
    beforeSend: _ajax_beforeSend,
    complete: _ajax_complete,
    error: _error,
    cache: true,
    async: false
});

// private
function _ajax_notifications(msg){
    show_notifications_msg(msg);
}

function _ajax_alert_on(status, msg){
    show_alert_msg(msg, status);
}

function _ajax_alert_off(){
    show_alert_msg("");
}

function _ajax_beforeSend(XMLHttpRequest){
    $("#traffic").attr('src', "${ctx.homepath}/static/images/access.gif");
}

function _ajax_complete(XMLHttpRequest, textStatus){
    $("#traffic").attr('src', "${ctx.homepath}/static/images/access-off.gif");

    if(XMLHttpRequest.status == "202"){
        _ajax_alert_on("SUCCEED", "${_('Accepted')}" + " [" + XMLHttpRequest.status + "]");
    } else if(XMLHttpRequest.status == "204"){
        _ajax_alert_on("ERROR", "${_('No Content')}" + " [" + XMLHttpRequest.status + "]");
    }
}

function _error(xml_http_request, status, e){
    if(xml_http_request.status == "400") {
        _ajax_alert_on("ERROR", "${_('Bad Request')}" + " [" + xml_http_request.status + "]\n" + xml_http_request.responseText);
    } else if (xml_http_request.status == "404"){
        _ajax_alert_on("ERROR", "${_('Not Found')}" + " [" + xml_http_request.status + "]\n" + xml_http_request.responseText);
    } else if (xml_http_request.status == "405"){
        _ajax_alert_on("ERROR", "${_('Method Not Allowed')}" + " [" + xml_http_request.status + "]");
    } else if (xml_http_request.status == "409"){
        _ajax_alert_on("ERROR", "${_('Conflict')}" + " [" + xml_http_request.status + "]\n" + xml_http_request.responseText);
    } else {
        _ajax_alert_on("ERROR", "${_('Illegal Error')}" + "\n" + xml_http_request.responseText);
    }
}

function _ajax_beforSend_grayout(id, url, params_form, validator, async_flag, ajax_event){
    var check = validator();
    if(!check){
        $(id + " span").removeClass("onclick");
        ajax_event(id, url, params_form, validator, async_flag);
    }
    return check;
}

function _ajax_success_grayout(){
    show_alert_msg("${_('Update success.')}", "SUCCEED");
    $(".grayout-contents :input").attr("disabled", "disabled");
    $(".grayout-footer span.button-right").html("${_('Close')}");

    // for ajax_post(put)_grayout function
    $(".grayout-footer a").unbind("click");
    
    $("#cluetip").hide();
    $('span[id$="_help"]').each(function(){
        $(this).remove();
    });

    $(".grayout-footer a").attr("id", "grayout_close_button");
    $("#grayout_close_button span").removeClass("onclick");
    grayout_submit_effect("#grayout_close_button");
    $("#grayout_close_button").one("click", function(){
        $('#dialog_screen').dialog('close');
    });
}

function _ajax_complete_grayout(XMLHttpRequest, textStatus){
    _ajax_complete(XMLHttpRequest, textStatus);
}

function _ajax_error_grayout(xml_http_request, status, e,
                             id, url, params_form, validator, async_flag, ajax_event){
    _error(xml_http_request, null, e);
    $(id + " span").removeClass("onclick");
    ajax_event(id, url, params_form, validator, async_flag);
}

function _check_file_upload(response){
    var ret = true;
    res_arr = response.split(/\n/);
    for(var i = 0; i < res_arr.length; i++){
        var data_arr = res_arr[i].split(/:/);
        if(data_arr[0] == "400" || data_arr[0] == "409" || data_arr[0] == "500"){
            ret = false;
            break;
        }
    }
    return ret;
}

function _ajax_file_delete(form_id, upload_button_id, cancel_button_id,
                           name_input_id, value_input_id, url, validates, async_flag){
    $(upload_button_id).hide();
    $(cancel_button_id).show();

    $(upload_button_id).unbind("click");

    $(cancel_button_id).one("click", function(){
        $.ajax({
            url: url + "/" + $(name_input_id).val(),
            data: null,
            dataType: "html",
            type: "DELETE",
            async: async_flag,
            
            beforeSubmit: function(){
                validates();
            },
            success: function(data, status){
                $(value_input_id).attr("disabled", "");
                $(name_input_id).attr("value", "");

                _ajax_alert_on("CAUTION", "${_('Succeeded to remove the file.')}");
                _ajax_file_upload(
                    form_id, 
                    upload_button_id, 
                    cancel_button_id, 
                    name_input_id, 
                    value_input_id, 
                    url, 
                    validates,
                    async_flag
                );
            },
            error: function(xml_http_request, status, e){
                _error(xml_http_request, status, e);
                _ajax_file_delete(
                    form_id,
                    upload_button_id,
                    cancel_button_id,
                    name_input_id,
                    value_input_id,
                    url,
                    validates,
                    async_flag
                );
            },
            complete: function(xml_http_request, text_status){
                _ajax_complete(xml_http_request, text_status);
            }
        });
    });
}

function _ajax_file_upload(form_id, upload_button_id, cancel_button_id,
                           name_input_id, value_input_id, url, validates, async_flag){
    var options = {
        beforeSubmit: function(){
            validates();
        },
        url: url,
        async: async_flag,

        success: function(data, status){
            if(_check_file_upload(data) == true){
                // success
                var real_filename = data;
                $(value_input_id).attr("disabled", "disabled");
                $(name_input_id).attr("value", data);

                _ajax_alert_on("CAUTION", "${_('Succeeded to update the file.')}" + "\n" + "${_('To complete the set, please click on the button below the screen.')}");

                _ajax_file_delete(
                    form_id, 
                    upload_button_id, 
                    cancel_button_id, 
                    name_input_id, 
                    value_input_id, 
                    url, 
                    validates,
                    async_flag
                );
            } else {
                // error
                _ajax_alert_on("ERROR", "${_('Failed to create icon file')}");
                $(upload_button_id).one("click", function(){
                    $(form_id).submit();
                });
            }
        },
        error: function(xml_http_request, status, e){
            _error(xml_http_request, status, e);
            $(upload_button_id).one("click", function(){
                $(form_id).submit();
            });
        },
        complete: function(xml_http_request, text_status){
            _ajax_complete(xml_http_request, text_status);
        }
    };
    $(form_id).ajaxForm(options); 

    $(upload_button_id).show();
    $(cancel_button_id).hide();

    $(upload_button_id).one("click", function(){
        $(form_id).submit();
    });
    $(cancel_button_id).unbind("click");
}

// lib
function ajax_request(url, data, callback, type, method, async_flag){
    if($.isFunction(data)) {
        callback = data;
        data = {};
    }
    async_flag = set_async_flag(async_flag);

    return $.ajax({
        url: url,
        data: data,
        dataType: type,
        type: method,
        async: async_flag,
        
        success: callback
    });
}

$.extend({
    put: function(url, data, callback, type, async_flag) {
        return ajax_request(url, data, callback, type, 'PUT', async_flag);
    },
    remove: function(url, data, callback, type, async_flag) {
        return ajax_request(url, data, callback, type, 'DELETE', async_flag);
    }
});

// public 
function ajax_get(id, url, params, async_flag){
    async_flag = set_async_flag(async_flag);

    $.ajax({
        url: url,
        data: params,
        type: "GET",
        async: async_flag,

        success: function(data, status) {
            if(data != ""){
                $(id).html(data);
            }
        }
    });
}

function ajax_delete(id, url, params, async_flag){
    async_flag = set_async_flag(async_flag);

    $.ajax({
        url: url,
        data: params,
        type: "DELETE",
        async: async_flag,

        success: function(data, status) {
            if(data != ""){
                $(id).html(data);
            }
        }
    });
}

function ajax_json(url, params, fn, async_flag){
    async_flag = set_async_flag(async_flag);

    $.ajax({
        url: url,
        data: params,
        dataType: "json",
        type: "GET",
        async: async_flag,
        success: fn
    });
    return false;
}

function ajax_put(url, params, fn, async_flag, renew_url){
    async_flag = set_async_flag(async_flag);

    $.ajax({
        url: url,
        data: params,
        type: "PUT",
        async: async_flag,        
        success: function(data, status){
            fn(data, status);
            if (renew_url){
                timer = setTimeout(function(){
                    g_main_url = renew_url;
                    renew_all(false);
                }, 5000);
            }
        }
    });
}

function ajax_post_event(id, url, params_form, validator, async_flag){
    async_flag = set_async_flag(async_flag);
    
    grayout_submit_effect(id);
    $(id).one("click", function() {
        $.ajax({
            url: url,
            data: $(params_form).serialize(),
            dataType: "html",
            type: "POST",
            async: async_flag,
            
            beforeSend: function(){
                return _ajax_beforSend_grayout(id, url, params_form, validator, async_flag, ajax_post_event);
            },
            success: _ajax_success_grayout,
            complete: _ajax_complete_grayout,
            error: function(xml_http_request, status, e){
                _ajax_error_grayout(xml_http_request, status, e,
                                        id, url, params_form, validator, async_flag, ajax_post_event);
            }
        });
    });
}

function ajax_put_event(id, url, params_form, validator, async_flag){
    async_flag = set_async_flag(async_flag);

    /*
        Problem:
        IE8 throw PUT request and receive seeother, that has location current URI,
        IE8 continue  throw PUT request endlessly.

        Solution:
        use overload POST method or redirect other URI.
    */
    /* overload POST */
    method_type = "PUT";
    if(jQuery.browser.msie){
        $("#_method").val("PUT");
        method_type = "POST";
    }

    grayout_submit_effect(id);
    $(id).one("click", function() {
        $.ajax({
            url: url,
            data: $(params_form).serialize(),
            dataType: "html",
            type: method_type,
            async: async_flag,
            
            beforeSend: function(){
                 return _ajax_beforSend_grayout(id, url, params_form, validator, async_flag, ajax_put_event);
            },
            success: _ajax_success_grayout,
            complete: _ajax_complete_grayout,
            error: function(xml_http_request, status, e){
                _ajax_error_grayout(xml_http_request, status, e,
                                    id, url, params_form, validator, async_flag, ajax_put_event);
            }
        });
    });
}

function set_async_flag(async_flag){
    if(async_flag != true){
        async_flag = false;
    }
    return async_flag;
}

// *.input multi section
function get_section(ifval, ifs){
    var section = $(ifval).val();
    var _i = 0;
    for(i=0;i<ifs.length;i++){
        if(section == ifs[i]){_i = i;}
    }
    return _i;
}

function _ajax_beforSend_grayout_if(id, ifval, ifs, urls, params_forms, validators, async_flag, ajax_event){
    i = get_section(ifval, ifs);
    var check = validators[i]();
    if(!check){
        $(id + " span").removeClass("onclick");
        ajax_event(id, ifval, ifs, urls, params_forms, validators, async_flag);
    }
    return check;
}

function _ajax_error_grayout_if(xml_http_request, status, e,
                             id, ifval, ifs, urls, params_forms, validators, async_flag, ajax_event){
    _error(xml_http_request, null, e);
    $(id + " span").removeClass("onclick");
    ajax_event(id, ifval, ifs, urls, params_forms, validators, async_flag);
}

function ajax_post_event_if(id, ifval, ifs, urls, params_forms, validators, async_flag){
    async_flag = set_async_flag(async_flag);
    
    grayout_submit_effect(id);

    _i = get_section(ifval, ifs);
    $(id).one("click", function(){
        $.ajax({
            url: urls[_i],
            data: $(params_forms[_i]).serialize(),
            dataType: "html",
            type: "POST",
            async: async_flag,
            beforeSend: function(){
	        return _ajax_beforSend_grayout_if(id, ifval, ifs, urls, params_forms, validators, async_flag, ajax_post_event_if);
            },
            success: _ajax_success_grayout,
            complete: _ajax_complete_grayout,
            error: function(xml_http_request, status, e){
                _ajax_error_grayout_if(xml_http_request, status, e, id, ifval, ifs, urls, params_forms, validators, async_flag, ajax_post_event_if);
            }
        });
    });
}
