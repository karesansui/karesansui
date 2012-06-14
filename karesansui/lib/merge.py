#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2012 HDE, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import karesansui

from karesansui.lib.const import MACHINE_ATTRIBUTE, MACHINE_HYPERVISOR
from karesansui.db.model.machine import Machine
from karesansui.db.model.user import User
from karesansui.db.model.notebook import Notebook

class MergeHost:
    """<comment-ja>
    Machine(s) Model と libvirt KaresansuiVirtGuest(s)をマージします。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
    def __init__(self, kvc, model, set_guests=True, if_deleted=2):
        """<comment-ja>
        @param model: Database Model
        @type model: karesansui.db.model.machine.Machine
        @param set_guests: 所属するゲストOS情報を含めるか。
        @type set_guests: bool
        @param is_deleted: 0: すべて, 1: 論理削除のみ, 2: 論理削除以外
        @param is_deleted: int

        注) 本クラスでは、libvirtへのコネクションをクローズしません。呼び出し元でcloseしてください。
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        self.info = {"model" : model,
                     "virt" : None,
                     }
        self.guests = []

        self.kvc = kvc
        self.set_guests = set_guests
        self.if_deleted = if_deleted

        if self.set_guests is True:

            if model.attribute == 2:
                #import pdb; pdb.set_trace()
                user  = User(u"unknown",
                             unicode("dummydummy"),
                             unicode("dummydummy"),
                             u"Unknown User",
                             u"",
                            )
                notebook = Notebook(u"", u"")

                for guest_name in kvc.list_active_guest() + kvc.list_inactive_guest():
                    _virt = kvc.search_kvg_guests(guest_name)
                    if len(_virt) > 0:
                        uuid = _virt[0].get_info()["uuid"]

                        #import pdb; pdb.set_trace()
                        guest = Machine(user,
                                        user,
                                        u"%s" % uuid,
                                        u"%s" % guest_name,
                                        MACHINE_ATTRIBUTE['GUEST'],
                                        MACHINE_HYPERVISOR['URI'],
                                        notebook,
                                        [],
                                        u"%s" % "",
                                        u'icon-guest3.png',
                                        False,
                                        None,
                                        )

                        self.guests.append(MergeGuest(guest, _virt[0]))

            else:
                for guest in model.children:
                    if self.if_deleted == 0:
                        _virt = kvc.search_kvg_guests(guest.uniq_key)
                        if len(_virt) > 0:
                            self.guests.append(MergeGuest(guest, _virt[0]))
                    elif self.if_deleted == 1:
                        if guest.is_deleted is True:
                            _virt = kvc.search_kvg_guests(guest.uniq_key)
                            if len(_virt) > 0:
                                self.guests.append(MergeGuest(guest, _virt[0]))
                    elif self.if_deleted == 2:
                        if guest.is_deleted is False:
                            _virt = kvc.search_kvg_guests(guest.uniq_key)
                            if len(_virt) > 0:
                                self.guests.append(MergeGuest(guest, _virt[0]))
                    else:
                        raise Karesansui.KaresansuiLibException("Flag is not expected. if_deleted=%d" % if_deleted)
                
    def get_json(self, languages):
        """<comment-ja>
        @return: {"model" : Host Model,
                  "virt" : Host Virt(karesansui.lib.virt.virt.KaresansuiVirtGuest),
                  "guests" : Guest list(MergeGuest.get_json()),
                  }
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        ret = {"model" : self.info["model"].get_json(languages),
               "virt" : self.info["virt"],
               }

        ret["guests"] = []
        for guest in self.guests:
            ret["guests"].append(guest.get_json(languages))
        return ret
        
class MergeGuest:
    """<comment-ja>
    Machine Model と libvirt KaresansuiVirtGuestをマージします。
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    
    def __init__(self, model, virt): 
        self.info = {"model" : model,
                     "virt" : virt,
                     }

    def get_json(self, languages):
        """<comment-ja>
        @return: {"model" : Guest Model,
                  "virt" : Guest Virt(karesansui.lib.virt.virt.KaresansuiVirtGuest),
                  }
        </comment-ja>
        <comment-en>
        TODO: English Comment
        </comment-en>
        """
        ret = {"model" : self.info["model"].get_json(languages),
               "virt" : self.info["virt"].get_json(),
               }
        return ret
        
if __name__ == '__main__':
    pass
    
