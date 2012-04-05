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

function tool_reset(id){
    $(id).find(".tool-left").removeClass("tool-left-active").removeClass("tool-left-invalid");
    $(id).find(".tool-img").removeClass("tool-img-active").removeClass("tool-img-invalid");
    $(id).find(".tool-right").removeClass("tool-right-active").removeClass("tool-right-invalid");
    var _img = $(id).find("img").attr("src");
    _img = _img.replace("-invalid", "");
    $(id).find("img").attr("src", _img);
}

function tool_over(id){
    $(id).find(".tool-left").toggleClass("tool-left-over");
    $(id).find(".tool-img").toggleClass("tool-img-over");
    $(id).find(".tool-right").toggleClass("tool-right-over");
}

function tool_active(id){
    $(id).find(".tool-left").removeClass("tool-left-active").addClass("tool-left-active");
    $(id).find(".tool-img").removeClass("tool-img-active").addClass("tool-img-active");
    $(id).find(".tool-right").removeClass("tool-right-active").addClass("tool-right-active");
}

function tool_invalid(id){
    $(id).find(".tool-left").removeClass("tool-left-invalid").addClass("tool-left-invalid");
    $(id).find(".tool-img").removeClass("tool-img-invalid").addClass("tool-img-invalid");
    $(id).find(".tool-right").removeClass("tool-right-invalid").addClass("tool-right-invalid");
    var _img = $(id).find("img").attr("src");
    if(_img != null){
        if(_img.indexOf("-invalid.png") == -1){
            _img = _img.replace(".png", "") + "-invalid.png";
            $(id).find("img").attr("src", _img);
        }
    }
}
