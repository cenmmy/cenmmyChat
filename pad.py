#!/usr/bin/env python3
# coding=UTF-8
'''
@Author: cenmmy
@LastEditors: cenmmy
@Description: 
@Date: 2019-04-13 11:08:09
@LastEditTime: 2019-04-21 20:17:27
'''

import curses
from curses.textpad import rectangle

# const variable
_up   = 0
_right = 1
_down = 2
_left = 3

#######################################################################

"""
classname: Pad
description: Abstracting pad objects
"""
class Pad(object):
    '''
    @description: Initialization function of Pad
    @param {stdscr: standard screen
            nlines: pad's height,
            ncoles: pas's width,
            sminrow: display area upper left y,
            smincol: dispaly area upper left x,
            smaxrow: display area lower right y,
            smaxcol: display area lower right x,
            fgcolor: foreground color,
            bgcolor: background color,
            color_pair: color_pair} 
    @return: void
    '''
    def __init__(self, stdscr, nlines, ncols, sminrow, smincol, smaxrow, smaxcol, fgcolor, bgcolor, color_pair):
        # Parameter initialization
        self.stdscr = stdscr
        self.nlines = nlines
        self.ncols  = ncols
        self.sminrow= sminrow
        self.smincol= smincol
        self.smaxrow= smaxrow
        self.smaxcol= smaxcol
        # Create pad objects
        self.pad = curses.newpad(self.nlines, self.ncols)
        # upper left corner of the pad region to be displayed 
        self.pminrow = 0
        self.pmincol = 0
        # color_pair
        self._fgcolor = fgcolor
        self._bgcolor = bgcolor
        self.color_pair = color_pair
        curses.init_pair(self.color_pair, self._fgcolor, self._bgcolor)

    '''
    @description: specify the part of the pad to be displayed and the location on the screen to be used for the display 
    @param {void} 
    @return: void
    '''
    def refresh(self):
        self.pad.refresh(self.pminrow, self.pmincol, self.sminrow, self.smincol, self.smaxrow, self.smaxcol)

    '''
    @description: Reset the size of pad
    @param {nlines: Nlines of the new pad,
            ncols: Ncols of the new pad} 
    @return: void
    '''
    def resize_pad(self, nlines, ncols):
        self.nlines = nlines
        self.ncols  = ncols
        self.pad    = curses.newpad(self.nlines, self.ncols)

    '''
    @description: Create pad borders
    @param {void} 
    @return: void
    '''
    def border(self):
        # Specifies the upper left and lower right corner of the border
        _uly = self.sminrow - 1
        _ulx = self.smincol - 1
        _lry = self.smaxrow + 1
        _lrx = self.smaxcol + 1
        # Create borders
        try:
            rectangle(self.stdscr, _uly, _ulx, _lry, _lrx)
        except curses.error:
            pass
        # Refresh stdscr
        self.stdscr.refresh()
    
    '''
    @description: draw content in the pad
    @param {void} 
    @return: void
    '''
    def content(self):
        pass

    '''
    @description: Display components on the screen
    @param {void} 
    @return: void
    '''
    def draw(self):
        self.border()
        self.content()
    
    def clear(self):
        self.pad.clear()

    @property
    def fgcolor(self):
        return self._fgcolor 
    
    @fgcolor.setter
    def fgcolor(self, value):
        self._fgcolor = value
        curses.init_pair(self.color_pair, self._fgcolor, self._bgcolor) 
    
    @property
    def bgcolor(self):
        return self._bgcolor
    
    @bgcolor.setter
    def bgcolor(self, value):
        self._bgcolor = value
        curses.init_pair(self.color_pair, self._fgcolor, self._bgcolor)


################################################################################

"""
classname: ScrollablePad
description: inherits from Pad class and realizes the function of scrolling.
"""
class ScrollablePad(Pad):
    '''
    @description: Initialization function of ScrollablePad
    @param {
            stdscr: standard screen
            nlines: pad's height,
            ncoles: pas's width,
            sminrow: display area upper left y,
            smincol: dispaly area upper left x,
            smaxrow: display area lower right y,
            smaxcol: display area lower right x
            fgcolor: foreground color,
            bgcolor: background color,
            color_pair: color_pair} 
    @return: void
    '''
    def __init__(self, stdscr, nlines, ncols, sminrow, smincol, smaxrow, smaxcol, fgcolor, bgcolor, color_pair):
        Pad.__init__(self, stdscr, nlines, ncols, sminrow, smincol, smaxrow, smaxcol, fgcolor, bgcolor, color_pair)
        self._direction = _up
        self._current_row = 0
        self._current_col = 0
            
    '''
    @description: Modify the direction of the scroll
    @param {direction: Scrolling direction} 
    @return: void
    '''
    def modify_direction(self, direction): 
        self._direction = direction

    '''
    @description: Invoked when the up key is pressed
    @param {lines: Number of rows scrolling up} 
    @return: void
    '''
    def onkeyup(self, lines=1):
        self.modify_direction(_up)
        self.current_row = self.current_row - lines 
        self.modify_pminrow()

    '''
    @description: Invoked when the right key is pressed
    @param {lines: Number of cols scrolling up} 
    @return: void
    '''
    def onkeyright(self, cols=1):
        self.modify_direction(_right)
        self.current_col = self.current_col + cols
        self.modify_pmincol()
    '''
    @description: Invoked when the down key is pressed
    @param {lines: Number of rows scrolling down} 
    @return: void
    '''
    def onkeydown(self, lines=1):
        self.modify_direction(_down)
        self.current_row = self.current_row + lines 
        self.modify_pminrow()
    
    '''
    @description: Invoked when the left key is pressed
    @param {lines: Number of cols scrolling up} 
    @return: void
    '''
    def onkeyleft(self, cols=1):
        self.modify_direction(_left)
        self.current_col = self.current_col - cols
        self.modify_pmincol()

    '''
    @description: modify the pminrow
    @param {type} 
    @return: 
    '''
    def modify_pminrow(self, delete=False):
        if delete:
            if self.current_row > self.smaxrow - self.sminrow:
                self.pminrow = self.current_row - self.smaxrow + self.sminrow
            else:
                self.pminrow = 0
        else:
            if self.current_row > self.pminrow + self.smaxrow - self.sminrow and self._direction == _down:
                self.pminrow = self.current_row - self.smaxrow + self.sminrow
            elif self.current_row < self.pminrow and self._direction == _up:
                self.pminrow = self.current_row

    '''
    @description: modify the pminrow
    @param {type} 
    @return: 
    '''
    def modify_pmincol(self, delete=False):
        if delete:
            if self.current_col > self.smaxcol - self.smincol:
                self.pmincol = self.current_col - self.smaxcol + self.smincol
            else:
                self.pmincol = 0
        else:
            if self.current_col > self.pmincol + self.smaxcol - self.smincol and self._direction == _right:
                self.pmincol = self.current_col - self.smaxcol + self.smincol
            elif self.current_col < self.pmincol and self._direction == _left:
                self.pmincol = self.current_col

    '''
    @description: set style of current row
    @param {style: the style of current row} 
    @return: void
    '''
    def current_row_style(self, style):
        self.pad.chgat(self.current_row, 0, -1, style)
    
    '''
    @description: Scroll to the bottom of the list
    @param {void} 
    @return: void
    '''
    def move2bottom(self):
        self.current_row = self.nlines - 1
        self.modify_direction(_down)
        self.modify_pminrow()

    '''
    @description: Scroll to the top of the list
    @param {void} 
    @return: void
    '''
    def move2top(self):
        self.current_row = 0
        self.modify_direction(_up)
        self.modify_pminrow()
    
    def move2left(self):
        self.current_col = 0
        self.modify_direction(_left)
        self.modify_pmincol()

    def move2right(self):
        self.current_col = self.ncols - 1
        self.modify_direction(_right)
        self.modify_pmincol()
    
    @property
    def current_row(self):
        return self._current_row

    @current_row.setter
    def current_row(self, value):
        if not (value < 0 or value >= self.nlines):
            self._current_row = value
    
    @property
    def current_col(self):
        return self._current_col
    
    @current_col.setter
    def current_col(self, value):
        if not (value < 0 or value >= self.ncols):
            self._current_col = value