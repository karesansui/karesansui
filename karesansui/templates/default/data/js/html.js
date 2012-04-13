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

function make_tr(name, value, is_plane){
    var name_tag = "<th>" + name + "</th>";
    var image_tag = "<td class='detail-separator'><img src='${ctx.homepath}/static/images/table-space.gif' alt='' /></td>";
    if(typeof(is_plane) == "undefined"){
        is_plane = false;
    } 

    if(is_plane == true){
        var value_tag = "<td>" + value + "</td>";
    } else {
        var value_tag = "<td><pre>" + jQuery("<span>" + value + "</span>").text() + "</pre></td>";
    }

    return "<tr>" + name_tag + image_tag + value_tag + "</tr>";
}

function make_toggle_tr(toggle_button_id, toggle_value_id, desc_data, detail_data, is_plane){
    var detail_data_tag = '';

    for(i=0; i<detail_data.length; i++){
        var detail_name_tag = detail_data[i]['name'];
        var detail_value_tag = detail_data[i]['value'];
        if(is_plane == false){
            detail_value_tag = '<pre>' + detail_value_tag + '</pre>';
        }

        if(detail_name_tag == ''){
            detail_data_tag += '\
                            <tr>\
                                <td class="info_detail_value" colspan="2">\
                                    ' + detail_value_tag + '\
                                </td>\
                            </tr>\
            ';
        } else {
            detail_data_tag += '\
                            <tr>\
                                <td class="info_detail_name">\
                                    ' + detail_name_tag + '\
                                </td>\
                                <td class="info_detail_value">\
                                    ' + detail_value_tag + '\
                                </td>\
                            </tr>\
            ';
        }
    }

    var tag = '\
<tr>\
    <td>\
        <div class="info_desc">\
            <div id="' + toggle_button_id + '" class="info_desc_name">\
                ' + desc_data['name'] + '\
            </div>\
            <div class="info_desc_value">\
                ' + desc_data['value'] + '\
            </div>\
        </div>\
        <div style="clear:both"></div>\
            <div id="' + toggle_value_id + '" class="info_detail">\
                <table>\
                    <tbody>\
                        ' + detail_data_tag + '\
                    </tbody>\
                </table>\
            </div>\
        </div>\
    <tr>\
<td>\
';

    return tag;
}


function make_status_bar(name, total, free){
    var used = Math.round(total - free);
    var used_percent = Math.round(100 - ((free / total) * 100));
    var _status;

    total = Math.round(total);
    free = Math.round(free);

    _status_bar = '<table cellspacing="2" cellpadding="0" class="detail-sub-contents detail-status-contents" >'
                    + '<td><span class="status-bar-active" title="'
                    + '${_("Used")}: '
                    + used + 'MB"><em title="'
                    + '${_("Free")}: '
                    + free + 'MB" class="status-bar-back" style="left: '
                    + used_percent + '%;">'
                    + used_percent + '%</em></span></td><td>'
                    + used + ' / '
                    + total + ' MB</td></table>';
    return make_tr(name, _status_bar, true);
}

function make_space(){
    return "<tr><td colspan='3'><div class='detail-space'/></td></tr>";
}

function format_cputime(num){
    num = num.toString();
    var int_part = num.split(".")[0];
    var dec_part = num.split(".")[1];

    var ret = "";
    if(dec_part == undefined){
        ret = int_part + ".00";
    } else {
        ret = int_part + "." + dec_part.slice(0, 2);
    }

    return ret;
}

function show_detail_event(){
    $("#show_detail_switch").click(function(){
        if($("#detail_value").html() != "--"){
            var src_val = "${ctx.homepath}/static/images/tree-close.gif";
            
            $("#detail_value").toggle(500);
            if($(this).attr("src").indexOf("tree-open.gif") == -1){
                src_val = "${ctx.homepath}/static/images/tree-open.gif";
            }
            $(this).attr("src", src_val);
        }
    });
}

function join_comma(value){
    var ret = "";

    for(var i = 0; i < value.length; i++){
        ret += value[i] + ", ";
    }

    ret = ret.slice(0, ret.length - 2);

    return ret;
}

function str_status(status){
    if(status == VIR_DOMAIN_NOSTATE){
        return 'NOSTATE';
    } else if(status == VIR_DOMAIN_CRASHED){
        return 'CRASHED';
    } else if(status == VIR_DOMAIN_SHUTOFF){
        return 'SHUTOFF';
    } else if(status == VIR_DOMAIN_SHUTDOWN){
        return 'SHUTDOWN';
    } else if(status == VIR_DOMAIN_PAUSED){
        return 'PAUSED';
    } else if(status == VIR_DOMAIN_BLOCKED){
        return 'BLOCKED';
    } else if(status == VIR_DOMAIN_RUNNING){
        return 'RUNNING';
    } else{
        return null;
    }
}

function toggle_button_event(button_id, value_id, default_status, style, speed){
    if(typeof(default_status) == "undefined"){
        var default_status = "open";
    }

    if(typeof(style) == "undefined"){
        var style = "default";
    }

    if(typeof(speed) == "undefined"){
        var speed = 500;
    }

    if($(button_id).hasClass("tree-toggle") == true){
        return true;
    }

    $(button_id).addClass("tree-toggle");

    var str_button_id = button_id.replace("#", "");

    var open_img = "${ctx.homepath}/static/images/tree-open.gif"
    var close_img = "${ctx.homepath}/static/images/tree-close.gif";
    if(style == "black"){
        open_img = "${ctx.homepath}/static/images/tree-open-bk.png"
        close_img = "${ctx.homepath}/static/images/tree-close-bk.png";
    }

    $(button_id+'_img').css('cursor', 'pointer');

    if(default_status == "open"){
        $(button_id).prepend('<img id="' + str_button_id + '_img" src="' + open_img + '" alt="" class="tree-toggle-button"/></span>');
        $(button_id+'_img').attr("src", open_img);
        $(value_id).show();
    } else {
        $(button_id).prepend('<img id="' + str_button_id + '_img" src="' + close_img + '" alt="" class="tree-toggle-button"/></span>');
        $(button_id+'_img').attr("src", close_img);
        $(value_id).hide();
    }

    var click_event_func = function(){
        if($(this).attr("src") == open_img){
            $(this).attr("src", close_img);
            $(value_id).hide(speed);
        } else {
            $(this).attr("src", open_img);
            $(value_id).show(speed);
        }
    }

    /* 
     * Click event may not be effective.
     * Toggle event avoided.
     */
    $(button_id+"_img").toggle(
        click_event_func,
        click_event_func
    );

    return true;
}

function autounit(t, unit){
    var _t = parseFloat(t);
    var now = 0;
    var _u = 1;
    while(true){
        var ret = Math.floor(_t / _u);
        if(0 == ret || now == unit.length){
            break;
        }
        _u *= 1024;
        now += 1;
    }

    if(0 < now){
       _u /= 1024;
       now -= 1;
    }

    if(unit.length < now){
        return [_t, unit[0]];
    }
    return [_t / _u, unit[now]];
}

function view_autounit(t, unit, decimal_point, print_unit){
    if(typeof(unit) == 'undefined' || unit == null){
        unit = ['B','KB','MB','GB','TB', 'PB', 'EB'];
    }

    if(typeof(print_unit) == 'undefined' || print_unit == null){
        print_unit = false;
    }

    if(typeof(decimal_point) == 'undefined' || decimal_point == null){
        decimal_point = 0;
    }

    var ret = autounit(t, unit);

    var view_number = ret[0].toFixed(decimal_point);
    var view_unit = ret[1];

    if(print_unit == true){
        return view_number + view_unit;
    } else {
        return view_number;
    }
}

function megaunit(t, now_unit){
    var UNIT = ['B','KB','MB','GB','TB', 'PB', 'EB'];
    var MEGA_POS = 2;

    var _t = parseFloat(t);
    var _u = 1;

    var now_pos = 0;
    for(var i=0; i<UNIT.length; i++){
        if(now_unit == UNIT[i]){
            now_pos = i;
            break;
        }
    }

    if(MEGA_POS <= now_pos){
        var unit_reach = now_pos - MEGA_POS;
        for(var i=0; i<unit_reach; i++){
            _u *= 1024;
        }
        return _t * _u;
    } else {
        var unit_reach = MEGA_POS - now_pos;
        for(var i=0; i<unit_reach; i++){
            _u *= 1024;
        }
        return _t / _u;
    }
}

function view_megaunit(t, now_unit, decimal_point, print_unit){
    if(typeof(print_unit) == 'undefined' || print_unit == null){
        print_unit = false;
    }

    if(typeof(decimal_point) == 'undefined' || decimal_point == null){
        decimal_point = 0;
    }

    var ret = megaunit(t, now_unit);

    var view_number = ret.toFixed(decimal_point);

    if(print_unit == true){
        return view_number + 'MB';
    } else {
        return view_number;
    }
}
