#!/usr/bin/env python3
# coding=UTF-8
'''
@Author: cenmmy
@LastEditors: cenmmy
@Description: 
@Date: 2019-04-16 21:27:45
@LastEditTime: 2019-05-01 15:01:54
'''

import curses
from pad import ScrollablePad

class Input(ScrollablePad):
    def __init__(self, stdscr, ncols, sminrow, smincol, smaxrow, smaxcol, text='', fgcolor=curses.COLOR_WHITE, bgcolor=curses.COLOR_BLACK, color_pair=3):
        ScrollablePad.__init__(self, stdscr, 1, ncols, sminrow, smincol, smaxrow, smaxcol, fgcolor, bgcolor, color_pair)
        self.prelude = '>'
        self.text = text
    
    def cal_input_nlines(self):
        lines = 0
        for _ in range(0, len(self.prelude + self.text), self.ncols):
            lines = lines + 1
        return lines

    def content(self):
        # If the size of pad changes, reset the size of pad
        nlines = self.cal_input_nlines()
        if self.nlines != nlines:
            self.resize_pad(nlines, self.ncols)
        
        lines = 0
        content = self.prelude + self.text
        for start in range(0, len(content), self.ncols):
            try:
                self.pad.addstr(lines, 0, content[start:start+self.ncols], curses.color_pair(self.color_pair))
                self.pad.chgat(lines, 0, -1, curses.color_pair(self.color_pair))
            except curses.error:
                pass
            lines = lines + 1
    
    def read(self, ch):
        self.text = self.text + chr(ch)
    
    def delete(self):
        self.text = self.text[0:len(self.text) - 1]
    
    def ondelete(self):
        self.current_row = self.nlines - 1
        self.modify_pminrow(True)

    def oninsert(self):
        self.current_row = self.nlines - 1
        self.modify_pminrow(True)
        