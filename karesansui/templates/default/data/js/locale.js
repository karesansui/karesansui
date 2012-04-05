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

<%
from karesansui.lib.const import MACHINE_HYPERVISOR
import simplejson as json 
from karesansui.lib.utils import json_dumps

json_hypervisor = json_dumps(MACHINE_HYPERVISOR.keys())

%>
function locale_hypervisor(hypervisor){
    hypervisors = ${json_hypervisor}
    try{
        return ${_('hypervisors')}
    } catch(e) {
        return "${_('Undefined')}"
    }
}
