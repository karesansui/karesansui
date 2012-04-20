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
