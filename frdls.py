#!/usr/bin/env python3
# coding=UTF-8
'''
@Author: cenmmy
@LastEditors: cenmmy
@Description: friend list
@Date: 2019-04-14 11:24:24
@LastEditTime: 2019-04-19 16:02:05
'''

import curses
from pad import ScrollablePad

"""
classname: FrdLs
description: friend list
"""
class FrdLs(ScrollablePad):
    '''
    @description: Initialization function of the FrdLs
    @param {stdscr: standard screen,
            ncols:  list's width,
            sminrow: display area upper left y,
            smincol: dispaly area upper left x,
            smaxrow: display area lower right y,
            smaxcol: display area lower right x,
            friends: friends,
            fgcolor: foreground color,
            bgcolor: background color} 
    @return: void 
    '''
    def  __init__(self, stdscr, ncols, sminrow, smincol, smaxrow, smaxcol, friends, fgcolor=curses.COLOR_WHITE, bgcolor=curses.COLOR_BLACK, color_pair=1):
        ScrollablePad.__init__(self, stdscr, len(friends) + 1, ncols, sminrow, smincol, smaxrow, smaxcol, fgcolor, bgcolor, color_pair)
        self.title = ['FRIEND LIST']
        self._friends = friends

    '''
    @description: draw content in the pad
    @param {void} 
    @return: void
    '''
    def content(self):
        content = self.title + self.friends
        # If the size of pad changes, reset the size of pad
        if self.nlines != len(content):
            self.resize_pad(len(content), self.ncols)
        # draw friend list
        try:
            for index, item in enumerate(content):
                self.pad.addstr(index, 0, item)
                self.pad.chgat(index, 0, -1, curses.color_pair(self.color_pair))
        except curses.error:
            pass

    @property
    def friends(self):
        return self._friends
    
    @friends.setter
    def friends(self, value):
        self._friends = value