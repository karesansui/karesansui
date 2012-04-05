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

function goto_tab(uri,param) {
    $("#show").html('<div align="center"><img src="${ctx.homepath}/static/images/now-loading-main.gif" alt="Now Loading" /></div>');
    $("#cluetip").hide();
    _ajax_alert_off()
    g_now_main_url = uri;
    ajax_get('#show',uri, param, false);
    return void(0);
}
