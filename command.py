#!/usr/bin/env python3
# coding=UTF-8
'''
@Author: cenmmy
@LastEditors: cenmmy
@Description: 
@Date: 2019-04-19 15:17:32
@LastEditTime: 2019-05-01 14:59:19
'''

import curses
from pad import ScrollablePad

# const variable
COMMAND_IS_EMPTY     = -1
COMMAND_IS_NOT_EMPTY = 0

class Command(ScrollablePad):
    def __init__(self, stdscr, nlines, sminrow, smincol, smaxrow, smaxcol, command='', fgcolor=curses.COLOR_WHITE, bgcolor=curses.COLOR_BLACK, color_pair=4):
        self.prelude = ':'
        ScrollablePad.__init__(self, stdscr, nlines, len(self.prelude), sminrow, smincol, smaxrow, smaxcol, fgcolor, bgcolor, color_pair)
        self.command = command

    def content(self):
        content = self.prelude + self.command
        if self.ncols != len(content):
            self.resize_pad(self.nlines, len(content))
        try:
            self.pad.addstr(0, 0, content, curses.color_pair(self.color_pair))
        except curses.error:
            pass
    
    def read(self, ch):
        self.command = self.command + chr(ch)

    def delete(self):
        self.command = self.command[0: len(self.command) - 1]

    def reslove(self):
        temp = self.command.split(' ')
        length = len(temp)
        if length == 0:
            return {'status': COMMAND_IS_EMPTY, 'cmd': '', 'parms': []} 
        elif length == 1:
            return {'status': COMMAND_IS_NOT_EMPTY, 'cmd': temp[0], 'parms': []}
        else:
            return {'status': COMMAND_IS_NOT_EMPTY, 'cmd': temp[0], 'parms': temp[1:]}

    def ondelete(self):
        self.current_col = self.current_col - 1
        self.modify_pmincol(True)

    def oninsert(self):
        self.current_col = self.current_col + 1
        self.modify_pmincol(True)