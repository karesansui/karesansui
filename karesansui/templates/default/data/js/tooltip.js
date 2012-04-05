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
