#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#
# This file is part of Karesansui.
#
# Copyright (C) 2009-2010 HDE, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#

import sys
import os
import curses
import time

import __cmd__

from karesansui.lib.virt.virt import KaresansuiVirtConnection

# initialize curses
stdscr = curses.initscr()
curses.noecho()
curses.cbreak()
stdscr.keypad(1)

#curses.start_color()
#curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)

# timeout getch after 1s
stdscr.timeout(1000)

(maxy, maxx) = stdscr.getmaxyx()

vtop_start = time.time()
first_run = True

conn = KaresansuiVirtConnection()
shares = {}
while True:
    guests = conn.search_guests()
    idx = 1
    cpusum=0
    if first_run:
        for guest in guests:
            id = guest.ID()
            if id > -1:
                name = guest.name()
                info = guest.info()
                shares[name] = info[4]
        first_run = False
    else:
        stdscr.addstr(idx, 1, "Domain\t\tID\tVCPU\t%CPU\t%CPUSUM   ", curses.A_REVERSE)
        idx += 1
        for guest in guests:
            id = guest.ID()
            if id > -1:
                name = guest.name()
                info = guest.info()
                now = time.time()
                share = info[4] - shares[name]
                p = (share*100)/((now - vtop_start) * 10**9)
                cpusum+=p
                stdscr.addstr(idx, 1, "%s\t%d\t%d\t%.2f\t%.2f" % (name, id, info[3], p, cpusum))
                idx += 1
        idx += 1
        stdscr.addstr(idx, 1, "Press 'q' for quit.")
        idx += 1
    c = stdscr.getch()
    if c == ord('q'):
        curses.nocbreak()
        stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        break
    stdscr.erase()
    stdscr.refresh()

    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
curses.endwin()
conn.close()

