#!/usr/bin/env python3
# coding=UTF-8
'''
@Author: cenmmy
@LastEditors: cenmmy
@Description: 
@Date: 2019-04-19 11:34:56
@LastEditTime: 2019-04-21 20:46:25
'''

import curses
from pad import Pad

class StatusBar(Pad):
    def __init__(self, stdscr, nlines, ncols, sminrow, smincol, smaxrow, smaxcol, mode="NORMAL", other="", fgcolor=curses.COLOR_WHITE, bgcolor=curses.COLOR_BLACK, color_pair=5):
        Pad.__init__(self, stdscr, nlines, ncols, sminrow, smincol, smaxrow, smaxcol, fgcolor, bgcolor, color_pair)
        self.mode = mode
        self.other = other
        self.smile = '☺'

    def content(self):
        try:
            self.pad.addstr(0, 0, self.mode + ''.join([' ' for _ in range(self.ncols - len(self.mode) - len(self.other) - len(self.smile) - 1)]) + self.other + ' ' + self.smile, curses.color_pair(self.color_pair))
            self.pad.chgat(0, 0, -1, curses.color_pair(self.color_pair))
        except curses.error:
            pass
    
    def draw(self):
        self.content()