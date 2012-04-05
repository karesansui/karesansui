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

$.tablesorter.addWidget({
    id: "select",
    format: function(table) {
        $("tbody tr",table).click(function(){
            $("tbody tr",table).removeClass("active");
            $(this).addClass("active");
        });
    }
});

function selected_row(prefix){
    var target_id;
    $("tr[id*='"+prefix+"']").each(function(){
        if($(this).hasClass("active") == true){
            target_id = $(this).attr("id").replace(prefix, "");
        }
    });
    return target_id;
}

