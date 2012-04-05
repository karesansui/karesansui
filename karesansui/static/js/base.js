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

function button_effect(id){
    $(id).mousedown(function(){
        $(id + " span").addClass("onclick");
    }).mouseup(function(){
        $(id + " span").removeClass("onclick");
    }).mouseout(function(){
        $(id + " span").removeClass("onclick");
    });
}

function grayout_submit_effect(id){
    $(id).mousedown(function(){
        $(id + " span").addClass("onclick");
    }).mouseout(function(){
        $(id + " span").removeClass("onclick");
    }).click(function(){
        $(id).unbind("mouseout");
    });
}
