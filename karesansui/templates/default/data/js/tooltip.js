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

function helptip(id, title, value){
    var a_id = id.replace(/^#/, "");
    title = title.replace(/\"/g, "&quot;");
    value = value.replace(/\"/g, "&quot;");
    var action = '<a id="' + a_id + '_a" class="helptip" href="#" title="' + title + '|' + value + '"><img src="${ctx.homepath}/static/images/help.png" alt="" /></a>';
    $(id).append(action);
    $(id+'_a').cluetip({splitTitle: '|',
			activation:'click',
			width: 300,
			cursor: 'pointer',
			cluezIndex: 199999
		       });
}

function detailtip(id, title, value){
    var a_id = id.replace(/^#/, "");
    title = title.replace(/\"/g, "&quot;");
    value = value.replace(/\"/g, "&quot;");
    var action = '<a id="' + a_id + '_a" class="helptip" href="#" title="' + title + '|' + value + '"><img src="${ctx.homepath}/static/images/view.png" alt="" /></a>';
    $(id).append(action);
    $(id+'_a').cluetip({splitTitle: '|',
        activation:'click',
        width: 300,
        cursor: 'pointer',
        cluezIndex: 199999
    });
}
