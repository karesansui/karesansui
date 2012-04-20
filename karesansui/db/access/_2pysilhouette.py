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

import time
import logging

from pysilhouette.db.access import \
    jobgroup_findbyall, jobgroup_findbyall_limit, jobgroup_findbystatus, \
    jobgroup_findbyuniqkey, jobgroup_findbyid, jobgroup_update, \
    job_findbyjobgroup_id, job_update, job_result_action, job_result_rollback, \
    get_progress, up_progress, \
    save as jg_save, update as jg_update, delete as jg_delete

from pysilhouette.db.model import JOBGROUP_TYPE

from karesansui.db.model._2pysilhouette import Job, JobGroup, JOBGROUP_STATUS
from karesansui.db.access import dbsave, dbupdate, dbdelete
import karesansui.db.access.search
import karesansui.db.access.machine2jobgroup

logger = logging.getLogger('karesansui.db.access._2pysilhouette')

def jg_findbyall(session, jobgroup_ids=None, status=None, desc=False):

    query = session.query(JobGroup)

    if not jobgroup_ids is None:
        query = query.filter(JobGroup.id.in_(jobgroup_ids))

    if not status is None:
        query = query.filter(JobGroup.status == status)

    if desc is True:
        return query.order_by(JobGroup.id.desc()).all()
    else:
        return query.order_by(JobGroup.id.asc()).all()


def jg_findby1(session, jobgroup_id):
    return session.query(JobGroup).filter(JobGroup.id == jobgroup_id).first()

def jg_findbyalltype(session, _type,
                     jobgroup_ids=None, status=None,
                     desc=False):
    query = session.query(JobGroup)

    if not jobgroup_ids is None:
        query = query.filter(JobGroup.id.in_(jobgroup_ids))

    if not status is None:
        query = query.filter(JobGroup.status == status)

    if _type == JOBGROUP_TYPE["SERIAL"]:
        query = query.filter(JobGroup.type == JOBGROUP_TYPE["SERIAL"])
    elif _type == JOBGROUP_TYPE["PARALLEL"]:
        query = query.filter(JobGroup.type == JOBGROUP_TYPE["PARALLEL"])

    if desc is True:
        return query.order_by(JobGroup.id.desc()).all()
    else:
        return query.order_by(JobGroup.id.asc()).all()

def jg_findbylimit(session, limit, desc=False):
    if desc is True:
        return session.query(JobGroup).order_by(JobGroup.id.desc()).all()[:limit]
    else:
        return session.query(JobGroup).order_by(JobGroup.id.asc()).all()[:limit]

def jg_findbyserial_limit(session, limit, desc=False):
    if desc is True:
        return session.query(JobGroup).filter(
            JobGroup.type == JOBGROUP_TYPE["SERIAL"]).order_by(
            JobGroup.id.desc()).limit(limit).all()
    else:
        return session.query(JobGroup).filter(
            JobGroup.type == JOBGROUP_TYPE["SERIAL"]).order_by(
            JobGroup.id.asc()).limit(limit).all()

def jobgroup_findbyuniqkey_limit(session, uniq_key, limit, desc=False):
    if uniq_key:
        if desc is True:
            return session.query(JobGroup).filter(JobGroup.uniq_key == uniq_key).order_by(JobGroup.id.desc()).all()[:limit]
        else:
            return session.query(JobGroup).filter(JobGroup.uniq_key == uniq_key).order_by(JobGroup.id.asc()).all()[:limit]
    else:
        return None

def save_job_collaboration(karesansui_session,
                           pysilhouette_session,
                           machine2jobgroup,
                           jobgroup):
    """<comment-ja>
    ジョブの登録を行う。
      - Pysilhouette:JobgroupテーブルとKaresansui:machine2jobgroupテーブルに
      登録を行います。
    @param karesansui_session: Karesansui Database Session
    @type karesansui_session: Session
    @param pysilhouette_session: Pysilhouette Database Session
    @type pysilhouette_session: Session
    @param machine2jobgroup: Table Model(Karesansui)
    @type machine2jobgroup: karesansui.db.model.machine2jobgroup.Machine2Jobgroup
    @param jobgroup: Table Model(PySilhouette)
    @type jobgroup: pysilhouette.db.model.JobGroup
    @return 
    </comment-ja>
    <comment-en>
    TODO: English Comment
    </comment-en>
    """
    # JobGroup INSERT
    jg_save(pysilhouette_session, jobgroup)
    pysilhouette_session.commit()
    
    # Machine2JobGroup INSERT
    try:
        machine2jobgroup.jobgroup_id = jobgroup.id
        karesansui.db.access.machine2jobgroup.save(karesansui_session, machine2jobgroup)
        karesansui_session.commit()
    except:
        try:
            jg_delete(pysilhouette_session, jobgroup)
            pysilhouette_session.commit()
        except:
            # rollback(jobgroup)
            logger.critical('Failed to register the JobGroup. #6 - jobgroup id=%d' \
                              % jobgroup.id)
        raise # throw

def corp(karesansui_session,
          pysilhouette_session,
          machine2jobgroup,
          jobgroup,
          waittime=1,
          timeout=20):
    """<comment-ja>
    Pysilhouette経由で権限昇格によるコマンド実行を行います。
    </comment-ja>
    <comment-en>
    Can only reading (parallel)
    </comment-en>
    """
    save_job_collaboration(karesansui_session, pysilhouette_session, machine2jobgroup, jobgroup)

    timeout = int(timeout)
    waittime = int(waittime)

    start_time = time.time()
    res = False
    while True:
        if (int(time.time() - start_time)) <= timeout:
            pysilhouette_session.refresh(jobgroup)
            logger.debug('Reading JobGroup info - id=%d, status=%s' \
                         % (jobgroup.id, jobgroup.status))
            if jobgroup.status == JOBGROUP_STATUS['OK']:
                res = True
                break
        else:
            res = False # TimeOut
            logger.warn('Reading JobGroup - Result=Read Timeout, id=%d, status=%s' \
                                 % (jobgroup.id, jobgroup.status))
            break
        time.sleep(waittime)

    print 'Reading JobGroup - runtime=%d' % (int(time.time() - start_time))
    logger.fatal('Reading JobGroup - runtime=%d' % (int(time.time() - start_time)))
    return res


if __name__ == '__main__':
    pass
