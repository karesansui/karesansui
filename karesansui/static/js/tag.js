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

/**
 *
 * progress - the progress display in the carousel
 * 
 * @dependence jquery.js
 *
 */
function progress(id, size, pos){
    var max_width = $(id).width();
    var width = Math.floor((max_width - 1)/ size);
    var percent_width = Math.floor((width / max_width) * 100);
    var padding_percent_width = 100 - (percent_width * size);
    
    $(id).html("");
    for(var i = 0; i < size; i++){
        if(i == size - 1){
            percent_width += padding_percent_width;
        }

        if(pos == i){
            $(id).append("<div class='display' style='width:" + percent_width + "%;'></div>");
        } else {
            $(id).append("<div style='width:" + percent_width + "%;'></div>");
        }
    }
}

/**
 *
 * carousel - the carousel display
 * 
 * @dependence progress jquery.js jquery.jcarousel.js
 *
 */
function carousel(id, left_id, right_id, progress_id, visible){
    var _item = $("li", id).size();
    var _page = Math.floor(_item / visible);

    if(_item % visible){
        _page += 1;
    }

    _size = visible * _page;

    $(id).jcarousel({
        visible: visible,
        scroll: visible,
        size: _size,
        itemFirstInCallback: function(carousel, item, idx, state){
            if(idx == 1){
                $(left_id).unbind('click');
                $(left_id).addClass('off');
            } else {
                $(left_id).bind('click', function(){carousel.prev()});
                $(left_id).removeClass('off');
            }

            if(idx + carousel.options.scroll - 1 == carousel.options.size){
                $(right_id).unbind('click');
                $(right_id).addClass('off');
            } else {
                $(right_id).bind('click', function(){carousel.next()});
                $(right_id).removeClass('off');
            }

            var pos = Math.floor(idx / carousel.options.scroll);
            if(_page != 1){
                progress(progress_id, _page, pos) 
            }
        }
    });

    $(window).unbind("resize");
}

function refine_machine(tag_id, machine_id, detail_id){
    var target_ids = new Array();
    var classes;

    $(detail_id).html("<span id='detail_value'>--</span>")

    $(tag_id + " a.active").each(function(){
        classes = $(this).attr("class").split(" ");
        for(i=0; i < classes.length; i++){
            if(classes[i].match(/tag_machine\d+/)){
                target_ids.push(classes[i].replace("tag_machine", ""));
            }
        }
    });

    $(machine_id + ">div").removeClass("active").addClass("passive").hide()
    //alert(machine_id)

    if(target_ids.length){
        var machine_prefix

        if(machine_id == "#guests"){
            machine_prefix = "#guest_";
        } else if(machine_id == "#host"){
            machine_prefix = "#host_"
        }

        for(var i = 0; i < target_ids.length; i++){
            $(machine_prefix + target_ids[i]).show();
        }
    } else{
        $(machine_id + ">div").show();
    }
}

function tag_get_event(tag_id, machine_id, detail_id, url){
    $.ajax({
        url: url,
        async: false,
        success: function(data, status){
            $(tag_id + " #tag-main").html(data);
            carousel(
                tag_id + " #tag-main",
                tag_id + " .left",
                tag_id + " .right",
                tag_id + " #tag-progress",
                6
            );

            $(tag_id + " a").toggle(
                function(){
                    $(this).addClass("active");
                    refine_machine(tag_id, machine_id, detail_id)
                },
                function(){
                    $(this).removeClass("active");
                    refine_machine(tag_id, machine_id, detail_id)
                }
            );
        },
        error: function _error(xml_http_request, status, e){
            var prefix = "<div class='value'><ul><li><span class='text'>";
            var suffix = "</span></li></ul></div>";
            $(tag_id + " #tag-main").html(prefix + xml_http_request.responseText + suffix);
        }
    });
}

