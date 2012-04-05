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

function machine_post_event(id, url, params_form, validator, async_flag){
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
                return _ajax_beforSend_grayout(id, url, params_form, validator, async_flag, machine_post_event);
            },
            success: function(){
                if(typeof($("#icon_upload_submit").val()) != "undefined"){
                    if($("#icon_upload_submit").attr("style").indexOf("inline") != -1){
                        $("#multi_icon").val("");
                    }
                    $("#icon_upload_submit").hide();
                    $("#icon_cancel_submit").hide();
                }
                $(".ui-slider").hide();
                _ajax_success_grayout();
            },
            complete: _ajax_complete_grayout,
            error: function(xml_http_request, status, e){
                _ajax_error_grayout(xml_http_request, status, e,
                                        id, url, params_form, validator, async_flag, machine_post_event);
            }
        });
    });
}

function machine_put_event(id, url, params_form, validator, async_flag){
    async_flag = set_async_flag(async_flag);

    grayout_submit_effect(id);
    $(id).one("click", function() {
        $.ajax({
            url: url,
            data: $(params_form).serialize(),
            dataType: "html",
            type: "PUT",
            async: async_flag,

            beforeSend: function(){
                _ajax_beforSend_grayout(id, url, params_form, validator, async_flag, machine_put_event);
            },
            success: function(){
                if(typeof($("#icon_upload_submit").val()) != "undefined"){
                    if($("#icon_upload_submit").attr("style").indexOf("inline") != -1){
                        $("#multi_icon").val("");
                    }
                    $("#icon_upload_submit").hide();
                    $("#icon_cancel_submit").hide();
                }
                $(".ui-slider").hide();
                _ajax_success_grayout();
            },
            complete: _ajax_complete_grayout,
            error: function(xml_http_request, status, e){
                _ajax_error_grayout(xml_http_request, status, e,
                                        id, url, params_form, validator, async_flag, machine_put_event);
            }
        });
    });
}

function icon_post_event(form_id, url, validator, async_flag){
    var upload_button_id = form_id + " #icon_upload_submit";
    var cancel_button_id = form_id + " #icon_cancel_submit";
    var name_input_id = form_id + " #icon_filename";
    var value_input_id = form_id + " #multi_icon";

    async_flag = set_async_flag(async_flag);

    button_effect(upload_button_id);
    button_effect(cancel_button_id);
    $(upload_button_id).hide();
    $(cancel_button_id).hide();

    $(value_input_id).one("change", function(){
        _ajax_file_upload(
            form_id,
            upload_button_id,
            cancel_button_id,
            name_input_id,
            value_input_id,
            url,
            validator,
            async_flag
        );
    });
}

