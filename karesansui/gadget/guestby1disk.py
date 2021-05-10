# -*- coding: utf-8 -*-
#
# This file is part of Karesansui.
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

import pwd

import karesansui
from karesansui.lib.const import VIRT_COMMAND_ADD_DISK, DISK_MIN_SIZE, \
     STORAGE_VOLUME_PWD, DISK_USES, \
     VIRT_COMMAND_DELETE_STORAGE_VOLUME, VIRT_COMMAND_CREATE_STORAGE_VOLUME

from karesansui.lib.utils import uniq_filename, is_param, chk_create_disk
from karesansui.lib.checker import Checker, \
     CHECK_EMPTY, CHECK_VALID, CHECK_MIN, CHECK_MAX

from karesansui.db.access._2pysilhouette import save_job_collaboration
from karesansui.db.access.machine2jobgroup import new as m2j_new
from karesansui.db.model._2pysilhouette import JobGroup, Job

from pysilhouette.command import dict2command

# lib public
def validates_disk(obj):
    checker = Checker()
    check = True

    _ = obj._
    checker.errors = []

    """ TODO
    # sparse

    # disk
    if is_param(obj.input, 'disk_size'):
        check = checker.check_number(_('Disk Size (MB)'),
                                     obj.input.disk_size,
                                     CHECK_EMPTY | CHECK_VALID | CHECK_MIN,
                                     min = DISK_MIN_SIZE,
                                     ) and check

    else:
        check = False
        checker.add_error(_('"%s" is required.') % _('Disk Size (MB)'))

    """
    obj.view.alert = checker.errors

    return check

def create_storage_volume_dir(obj, guest, domname, volume_name, pool_name, format,
                            capacity, allocation, unit, order):
    """<comment-ja>
    dir形式のストレージボリュームを利用して、ディスク追加を行います。
    </comment-ja>
    <comment-en>
    TODO: To include comments in English
    </comment-en>
    """
    # create volume
    cmdname = "Create Storage Volume"
    cmd = VIRT_COMMAND_CREATE_STORAGE_VOLUME

    options = {}

    options['name'] = domname
    options['pool_name'] = pool_name
    options['format'] = format
    options['capacity'] = capacity
    options['allocation'] = allocation
    options['unit'] = unit
    options['permission_owner'] = pwd.getpwnam(STORAGE_VOLUME_PWD["OWNER"])[2]
    options['permission_group'] = pwd.getpwnam(STORAGE_VOLUME_PWD["GROUP"])[2]
    options['permission_mode'] = STORAGE_VOLUME_PWD["MODE"]
    options['use'] = DISK_USES["DISK"]
    options['volume'] = volume_name

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], cmd), options)

    rollback_options = {}
    rollback_options["name"] = domname
    rollback_options["pool_name"] = pool_name
    rollback_options["use"] = DISK_USES["IMAGES"]

    rollback_cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'],
                   VIRT_COMMAND_DELETE_STORAGE_VOLUME),
        rollback_options)

    _job = Job('%s command' % cmdname, order, _cmd)
    _job.rollback_command = rollback_cmd
    return _job

def create_disk_job(obj, guest, domain_name, pool, volume,
                    bus, format, type, target=None, order=0):
    """<comment-ja>
    ディスク追加ジョブを作成します。
    </comment-ja>
    <comment-en>
    TODO: To include comments in English
    </comment-en>
    """
    cmdname = "Add Disk"
    cmd = VIRT_COMMAND_ADD_DISK

    options = {}
    options['name'] = domain_name
    options['pool'] = pool
    options['volume'] = volume
    options['bus'] = bus
    options['type'] = type
    if target is not None:
        options['target'] = target

    if type != 'iscsi':
        options['format'] = format

    _cmd = dict2command(
        "%s/%s" % (karesansui.config['application.bin.dir'], cmd), options)

    job = Job('%s command' % cmdname, order, _cmd)
    return job

def exec_disk_job(obj,
                  guest,
                  disk_job,
                  volume_job=None,
                  order=0):
    """<comment-ja>
    ゲストOSにディスクを追加するジョブを登録します。
    </comment-ja>
    <comment-en>
    TODO: To include comments in English
    </comment-en>
    """
    cmdname = "Add Disk"
    _jobgroup = JobGroup(cmdname, karesansui.sheconf['env.uniqkey'])
    if volume_job is not None:
        _jobgroup.jobs.append(volume_job)

    _jobgroup.jobs.append(disk_job)

    _machine2jobgroup = m2j_new(machine=guest,
                                jobgroup_id=-1,
                                uniq_key=karesansui.sheconf['env.uniqkey'],
                                created_user=obj.me,
                                modified_user=obj.me,
                                )

    save_job_collaboration(obj.orm,
                           obj.pysilhouette.orm,
                           _machine2jobgroup,
                           _jobgroup,
                           )
    return True
