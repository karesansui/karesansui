#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime

def create_epochsec(year, month, day, hour, minute, second):
    return str(int(time.mktime(datetime.datetime(year, month, day, hour, minute, second).timetuple())))

_start_year = 2010
_start_month = 4
_start_day = 1
_start_hour = 0
_start_minute = 0
_start_second = 0

_end_year = 2010
_end_month = 5
_end_day = 1
_end_hour = 0
_end_minute = 0
_end_second = 0

RRD_DIR = "/var/lib/collectd/foo.example.com/"

RRD_DIR_VIRT = "/var/lib/collectd/virt.example.com/"

START_TIME = create_epochsec(_start_year, _start_month, _start_day, _start_hour, _start_minute, _start_second)
END_TIME = create_epochsec(_end_year, _end_month, _end_day, _end_hour, _end_minute, _end_second)

INTERFACE = "br0"

