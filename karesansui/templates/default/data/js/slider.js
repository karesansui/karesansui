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
function change_slider_okay_area() {
    var left = $("div.ui-slider-range").css("left");
    $("#value-slider-left").css("width", left);
}

function change_slider_type(type) {
    switch (type) {
    case "max":
        $("#threshold_setting").css("background-color", "#EC0000");
        $("#value-slider-left").css("background-color", "#99E000");
        $("#threshold_val1_label").text("${_('Warning Value')} ");
        $("#threshold_val2_label").text("${_('Failure Value')} ");
        $("#threshold_type").val("max");
        break;
    case "min":
        $("#threshold_setting").css("background-color", "#99E000");
        $("#value-slider-left").css("background-color", "#EC0000");
        $("#threshold_val1_label").text("${_('Failure Value')} ");
        $("#threshold_val2_label").text("${_('Warning Value')} ");
        $("#threshold_type").val("min");
        break;
    }
}

function set_slider(id, min, max, default_val1, default_val2, unit, type) {
    if (unit) {
        unit = " " + unit;
    }else {
        unit = "";
    }

    $(id).slider("destroy");
    $(id).slider({
        range: true,
        min: min,
        max: max,
        values: [default_val1, default_val2],
        slide: function(event, ui){
        	change_slider_okay_area();
            $("#threshold_val1").val(ui.values[0]);
            $("#threshold_val2").val(ui.values[1]);
        },
        change: function(event, ui){
        	change_slider_okay_area();
            $("#threshold_val1").val(ui.values[0]);
            $("#threshold_val2").val(ui.values[1]);
        }
    });
    change_slider_okay_area();
    $("#threshold_min").text(min + unit);
    $("#threshold_max").text(max + unit);
    $("#threshold_val1").val($(id).slider("values", 0));
    $("#threshold_val2").val($(id).slider("values", 1));
    $(id).css("width", 450);
    $("#threshold_max_unit").text(unit);
    $("#threshold_min_unit").text(unit);

    change_slider_type(type);
}

function set_simple_slider(slider_id, value_id, min_value, max_value, max_available_value, start_value, step_value){
    if(typeof(max_available_value) == 'undefined'){
        max_available_value = max_value;
    }

    if(typeof(start_value) == 'undefined'){
        start_value = min_value;
    }

    if(typeof(step_value) == 'undefined'){
        step_value = 1;
    }

    if(max_available_value < start_value){
        alert("${_('Start value is bigger than max available value!')}");
        return false;
    }

    var str_slider_id = slider_id.replace("#", "");
    var str_slider_left_id = str_slider_id + '_left';
    var slider_left_id = slider_id + '_left';

    $(slider_id).html('<div id="' + str_slider_left_id + '" data-corner="left 5px" class="slider-left"></div>');

    // set slider
    $(slider_id).slider('destroy');
    $(slider_id).slider({
        range: true,
        min: min_value,
        max: max_value,
        step: step_value,
        values: [start_value, max_available_value],
        startValue: start_value,
        slide: function(event, ui){
            var left_value = $("div.ui-slider-range", slider_id).css("left");
            $(slider_left_id).css("width", left_value);
            $(value_id).val(ui.values[0]);
            $(value_id).trigger('change');
        }
    });

    // corner
    $(slider_id).corner('round 5px');

    // set left area
    var left_value = $("div.ui-slider-range", slider_id).css("left");
    $(slider_left_id).css("width", left_value);

    // remove right handle
    $(slider_id).unbind();
    $(slider_id).bind('slidechange', function(event, ui){
        var left_value = $("div.ui-slider-range", slider_id).css("left");
        $(slider_left_id).css("width", left_value);
        if(max_available_value != ui.values[1]){
            $(this).slider("values", 1, max_available_value);
        }
    });
    if($("a", slider_id).size() > 1){
        $("a.:last-child", slider_id).hide();
    }

    // set value
    $(value_id).unbind();
    $(value_id).change(function(){
        $(slider_id).slider("values", 0, $(this).val());
    });
    $(value_id).val(start_value);
}


