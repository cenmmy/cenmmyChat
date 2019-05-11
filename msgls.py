#!/usr/bin/env python3
# coding=UTF-8
'''
@Author: cenmmy
@LastEditors: cenmmy
@Description: 
@Date: 2019-04-16 21:27:55
@LastEditTime: 2019-05-01 14:05:36
'''

import curses
from pad import ScrollablePad

# const varialbe
TITLE = "MESSAGE LIST"

class Msg(object):
    def __init__(self, sender, receiver, content, date):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.date = date

class MsgLs(ScrollablePad):
    '''
    @description: Initialization function of the MsgLs
    @param {stdscr: standard screen,
            ncols:  list's width,
            sminrow: display area upper left y,
            smincol: dispaly area upper left x,
            smaxrow: display area lower right y,
            smaxcol: display area lower right x,
            msgs: msgs,
            fgcolor: foreground color,
            bgcolor: background color} 
    @return: void 
    '''
    def __init__(self, stdscr, ncols, sminrow, smincol, smaxrow, smaxcol, msgs, receiver="no receiver", fgcolor=curses.COLOR_WHITE, bgcolor=curses.COLOR_BLACK, color_pair=2):
        nlines = self.cal_msgs_nlines(ncols, msgs)
        ScrollablePad.__init__(self, stdscr, nlines, ncols, sminrow, smincol, smaxrow, smaxcol, fgcolor, bgcolor, color_pair)
        self.msgs = msgs
        self.receiver = receiver

    '''
    @description: calculate msgs nlines
    @param {ncols: list's width,
            msgs: messages} 
    @return: lines of the messages
    '''
    def cal_msgs_nlines(self, ncols, msgs):
        # title and dividing line
        lines = 2
        for msg in msgs:
            lines = lines + self.cal_msg_nlines(ncols, msg)
        return lines

    '''
    @description: Calculate the number of rows of messages
    @param {void} 
    @return: void
    '''
    def cal_msg_nlines(self, ncols, msg):
        # sender and time
        lines = 1
        # content
        for _ in range(0, len(msg.content), ncols):
            lines = lines + 1
        # Dividing line
        lines = lines + 1
        return lines
        
    '''
    @description: Write content to memory
    @param {void} 
    @return: void
    '''
    def content(self):
        # If the size of pad changes, reset the size of pad
        nlines = self.cal_msgs_nlines(self.ncols, self.msgs)
        if self.nlines != nlines:
            self.resize_pad(nlines, self.ncols)
        # title
        try:
            self.pad.addstr(0, int((self.ncols-len(self.receiver))/2), self.receiver)
            self.pad.chgat(0, 0, -1, curses.color_pair(self.color_pair))
            self.pad.addstr(1, 0, ''.join(['-' for _ in range(self.ncols)]), curses.color_pair(self.color_pair))
            self.pad.chgat(1, 0, -1, curses.color_pair(self.color_pair))
        except curses.error:
            pass
        line = 2
        # msgs
        for msg in self.msgs:
            try:
                self.pad.addstr(line, 0, '[' + msg.date + ']' + msg.sender)
                self.pad.chgat(line, 0, -1, curses.color_pair(self.color_pair))
            except curses.error:
                pass
            for start in range(0, len(msg.content), self.ncols):
                line = line + 1
                try:
                    self.pad.addstr(line, 0, msg.content[start:start + self.ncols])
                    self.pad.chgat(line, 0, -1, curses.color_pair(self.color_pair))
                except curses.error:
                    pass
            line = line + 1
            try:
                self.pad.addstr(line, 0, ''.join(['-' for _ in range(self.ncols)]))
                self.pad.chgat(line, 0, -1, curses.color_pair(self.color_pair))
            except curses.error:
                pass
            line = line + 1

    '''
    @description: Adding messages to the message list
    @param {msg: message} 
    @return: void
    '''
    def add_msg(self, msg):
        self.msgs.append(msg)
    
