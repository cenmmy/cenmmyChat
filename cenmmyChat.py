#!/usr/bin/env python3
# coding=UTF-8
'''
@Author: cenmmy
@LastEditors: cenmmy
@Description: chat app
@Date: 2019-04-13 10:49:32
@LastEditTime: 2019-05-11 10:40:10
'''

import curses
from cmychat import CmyChat
import time

# const variable
INVISIBLE = 0
NORMAL = 1
VERYVISIBLE = 2
    
'''
@description: entry function
@param {window} 
@return: void
'''
def main(stdscr):
    curses.curs_set(INVISIBLE)
    nlines, ncols = stdscr.getmaxyx()
    cc = CmyChat(stdscr, nlines, ncols, 0, 0)
    cc.draw()
    cc.refresh()
    cc.run()
if __name__ == "__main__":
    curses.wrapper(main)


