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

function reset_main(){
    g_main_url = "${ctx.homepath}/host.part";
    return g_main_url;
}

function reset_extra(){
    g_extra_url = "${ctx.homepath}/tree.part";
    return g_extra_url;
}

function reset_msg(){
    g_msg_url = "${ctx.homepath}/msg.part";
    return g_msg_url;
}

function reset_all(){
    reset_main();
    reset_extra();
    reset_msg();
}

//set global valuable
reset_all();

function renew_main(async){
    if(g_main_url && g_now_main_url && g_main_url == g_now_main_url){
        var _async;

        if(async == true){
            _async = true;
        } else {
            _async = false;
        }
        $.ajax({
            url: g_main_url,
            async: _async,
            success: function(data, status){
                $("#show").html(data);
            }
        });
    }
    reset_main();
}

function renew_extra(async){
    if(g_extra_url){
        var _async;

        if(async == true){
            _async = true;
        } else {
            _async = false;
        }
        $.ajax({
            url: g_extra_url,
            async: _async,
            success: function(data, status){
                $("#tree_display").html(data);
            }
        });
    }
    reset_extra();
}

function renew_msg(async){
    if(g_msg_url){
        var _async;

        if(g_msg_url == null){
            return false;
        }

        if(async == true){
            _async = true;
        } else {
            _async = false;
        }
        $.ajax({
            url: g_msg_url,
            async: _async,
            success: function(data, status){
                $("#msg_display").html(data);
            }
        });
    }
    reset_msg();
}

function renew_all(async){
    renew_main(async);
    renew_extra(async);
    renew_msg(async);
}

function renew_main_event(id, url){
    $(id).mousedown(function(){
        $(this).attr("src", "${ctx.homepath}/static/images/reload-on_click.gif");
    }).mouseup(function(){
        $(this).attr("src", "${ctx.homepath}/static/images/reload.gif");
    }).mouseout(function(){
        $(this).attr("src", "${ctx.homepath}/static/images/reload.gif");
    });

    $(id).one("click", function(){
        g_main_url = url;
        renew_main();
    });
}
