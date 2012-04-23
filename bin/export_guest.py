#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
#
# Copyright (C) 2012 HDE, Inc.
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

import os
import os.path
import sys
import re
import signal
import logging
from optparse import OptionParser

from ksscommand import KssCommand, KssCommandException, KssCommandOptException

import __cmd__

try:
    import karesansui
    from karesansui import __version__
    from karesansui.lib.virt.virt import KaresansuiVirtConnection, KaresansuiVirtException
    from karesansui.lib.utils import load_locale, preprint_r, base64_decode
    from karesansui.db.access.machine import findby1uniquekey
    from karesansui.lib.utils import string_from_uuid     as StrFromUUID
    from karesansui.lib.utils import generate_uuid        as GenUUID
    from karesansui.lib.virt.snapshot import KaresansuiVirtSnapshot
    from karesansui.db.access.snapshot import findbyname_guestby1 as s_findbyname_guestby1
except ImportError:
    print >>sys.stderr, "[Error] karesansui package was not found."
    sys.exit(1)

_ = load_locale()

usage = '%prog [options]'

def getopts():
    optp = OptionParser(usage=usage, version=__version__)
    optp.add_option('-n', '--name', dest='name', help=_('Domain Name'))
    optp.add_option('-p', '--pool', dest='pool', help=_('Storage pool name'))
    #optp.add_option('-d', '--dir',  dest='dir',  help=_('Directory name'))
    optp.add_option('-t', '--title',dest='title',default='', help=_('Export title'))
    optp.add_option('-q', '--quiet',dest='verbose', action="store_false", default=True, help=_("don't print status messages"))
    return optp.parse_args()

def chkopts(opts):
    reg = re.compile("[^a-zA-Z0-9\./_:-]")

    if opts.name:
        if reg.search(opts.name):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-n or --name', opts.name))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-n or --name')

    if opts.pool:
        if reg.search(opts.pool):
            raise KssCommandOptException('ERROR: Illigal option value. option=%s value=%s' % ('-p or --pool', opts.pool))
    else:
        raise KssCommandOptException('ERROR: %s option is required.' % '-p or --pool')

    #if not opts.pool and not opts.dir:
    #    raise KssCommandOptException('ERROR: -p/--pool or -d/--dir options are required.')

class ExportGuest(KssCommand):

    def __grab_stdout(self, flag):
        if flag:
                self.stdout = sys.stdout
                sys.stdout = os.fdopen(sys.stdout.fileno(), "w", 0)
                logf = open("/dev/null", "a")
                os.dup2(logf.fileno(), 1)
                logf.close()
        else:
                os.dup2(sys.stdout.fileno(), 1)
                sys.stdout = self.stdout
                del self.stdout

    def process(self):
        (opts, args) = getopts()
        chkopts(opts)
        self.up_progress(10)

        conn = KaresansuiVirtConnection(readonly=False)
        try:
            try:
                src_pool = conn.get_storage_pool_name_bydomain(opts.name, "os")
                if not src_pool:
                    raise KssCommandException("Source storage pool not found. domain=%s" % (opts.name))
                if conn.get_storage_pool_type(src_pool) == 'dir':
                    raise KssCommandException("Storage pool type 'dir' is not. domain=%s" % (opts.name))

                src_path = conn.get_storage_pool_targetpath(src_pool[0])
                self.domain_dir  = "%s/%s" % (src_path, opts.name,)

                if os.path.isdir(self.domain_dir) is False:
                    raise KssCommandException(
                        'domain directory is not found or not directory. - %s' % (self.domain_dir))

                # Model
                virt_uuid = conn.domname_to_uuid(opts.name)
                model = findby1uniquekey(self.kss_session, virt_uuid)
                if not model:
                    raise KssCommandException("Export data does not exist in the database.")

                database = {}
                database['attribute'] = model.attribute
                database['hypervisor'] = model.hypervisor
                database['icon'] = model.icon
                database['name'] = model.name
                database['notebook'] = {"title" : model.notebook.title,
                                        "value" : model.notebook.value,
                                        }
                tags = []
                for _tag in model.tags:
                    tags.append(_tag.name)

                database['tags'] = ",".join(tags)
                database['uniq_key'] = model.uniq_key

                # Snapshot
                snapshots = []
                kvs = KaresansuiVirtSnapshot(readonly=False)
                try:
                    guest_id = model.id
                    snapshot_list = kvs.listNames(opts.name)[opts.name]
                    if len(snapshot_list) > 0:
                        for snapshot in snapshot_list:
                            s_model = s_findbyname_guestby1(self.kss_session, snapshot, guest_id)
                            if s_model is not None:
                                name  = s_model.name
                                title = s_model.notebook.title
                                value = s_model.notebook.value
                                snapshots.append({"name":name, "title":title, "value":value,})
                except:
                    raise KssCommandException("Cannot fetch the information of snapshots correctly.")
                kvs.finish()

                # Pool
                target_dir = ""
                if opts.pool:
                    inactive_storage_pools = conn.list_inactive_storage_pool()
                    active_storage_pools = conn.list_active_storage_pool()
                    if not (opts.pool in active_storage_pools or opts.pool in inactive_storage_pools):
                        raise KssCommandException('Target storage pool does not exist. - pool=%s' % (opts.pool))

                    pool = conn.search_kvn_storage_pools(opts.pool)
                    storage_info = pool[0].get_info()
                    if storage_info["type"] == "dir" and storage_info["target"]["path"] != "":
                        target_dir = storage_info["target"]["path"]
                    else:
                        raise KssCommandException("Target storage pool type is not 'dir'. pool=%s" % (opts.pool))
                elif opts.dir:
                    target_dir = opts.dir

                self.up_progress(10)
                progresscb = None
                if opts.verbose:
                    try:
                        from karesansui.lib.progress import ProgressMeter
                        progresscb = ProgressMeter(command_object=self)
                    except:
                        pass
                else:
                    try:
                        from karesansui.lib.progress import ProgressMeter
                        progresscb = ProgressMeter(command_object=self,quiet=True)
                    except:
                        pass

                if opts.title[0:4] == "b64:":
                    title = base64_decode(opts.title[4:])
                else:
                    title = opts.title

                uuid = StrFromUUID(GenUUID())
                conn.export_guest(uuid=uuid,
                                  name=opts.name,
                                  directory=target_dir,
                                  database=database,
                                  realicon=model.realicon(),
                                  title=title,
                                  snapshots=snapshots,
                                  progresscb=progresscb)

                self.up_progress(40)
                self.logger.info('Export guest completed. - pool=%s, uuid=%s' % (opts.pool, uuid))
                print >>sys.stdout, _('Export guest completed. - pool=%s, uuid=%s' % (opts.pool, uuid))
                return True

            except KaresansuiVirtException, e:
                raise KssCommandException('Failed to export guest. - %s to %s [%s]' \
                                          % (opts.name,target_dir, ''.join(e.args)))

            except KssCommandException:
                raise

            except:
                raise KssCommandException('Failed to export guest. - %s to %s' \
                                          % (opts.name,target_dir))
        finally:
            conn.close()

if __name__ == "__main__":
    target = ExportGuest()
    sys.exit(target.run())
