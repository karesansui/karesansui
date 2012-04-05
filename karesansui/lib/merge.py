#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui Core.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#

import karesansui

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
    
