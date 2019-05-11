#!/usr/bin/env python3
# coding=UTF-8
'''
@Author: cenmmy
@LastEditors: cenmmy
@Description: 
@Date: 2019-04-19 15:19:01
@LastEditTime: 2019-05-01 15:05:07
'''

import curses
from frdls import FrdLs
from msgls import Msg, MsgLs
from input import Input
from command import Command
from statusbar import StatusBar
import time
import socketio
import locale
import os
import threading
from config import Config

# const variable
MODE_NORMAL  = 0b000
MODE_FRDLS   = 0b001
MODE_MSGLS   = 0b010
MODE_INPUT   = 0b011
MODE_COMMAND = 0b100
COMMAND_IS_EMPTY     = -1
COMMAND_IS_NOT_EMPTY = 0
URL = 'http://localhost:1234'


class WinInfo(object):
    def __init__(self, sminrow, smincol, smaxrow, smaxcol):
        self.sminrow = sminrow
        self.smincol = smincol
        self.smaxrow = smaxrow
        self.smaxcol = smaxcol
        
class CmyChat(object):
    def __init__(self, stdscr, nlines, ncols, begin_y, begin_x):
        self.stdscr = stdscr
        self.nlines = nlines
        self.ncols = ncols
        self.begin_y = begin_y
        self.begin_x = begin_x
        
        self.init_variable()
        self.init_pair()
        self.cal_wininfo()
        self.set_win_color(self._frdls_info, 1)
        self.set_win_color(self._msgls_info, 2)
        self.set_win_color(self._input_info, 3)
        self.set_win_color(self._command_info, 4)
        self.create_win()
        # send file path
        self.filepath = ''
        self.file_sender = ''
        self.file_receiver = ''

        self.sio = socketio.Client()

    def init_variable(self):
        self.friends = []
        self.text = ''
        self.command = ''
        self.mode = MODE_NORMAL
        self.user = {'username':''}
        self.current_receiver = 'no_receiver'
        self.msgls_set = {}
        self.logged_in = False

    def init_pair(self):
        frdls_color = Config['color']['frdls']
        msgls_color = Config['color']['msgls']
        input_color = Config['color']['input']
        command_color = Config['color']['command']
        curses.init_pair(1, frdls_color['fgcolor'], frdls_color['bgcolor'])
        curses.init_pair(2, msgls_color['fgcolor'], msgls_color['bgcolor'])
        curses.init_pair(3, input_color['fgcolor'], input_color['bgcolor'])
        curses.init_pair(4, command_color['fgcolor'], command_color['bgcolor'])

    def cal_wininfo(self): 
        self._frdls_info   = WinInfo(self.begin_y + 1, self.begin_x + 1, (self.begin_y + 1) + (self.nlines - 2 - 4 - 1), (self.begin_x + 1) + (int((self.ncols - 4) * 0.25) - 1))
        self._msgls_info   = WinInfo(self.begin_y + 1, self._frdls_info.smaxcol + 1 + 1 + 1, (self.begin_y + 1) + (int((self.nlines - 2 - 2 - 4) * 0.7) - 1), (self.begin_x + self.ncols - 1 - 1))
        self._input_info   = WinInfo(self._msgls_info.smaxrow + 1 + 1 + 1, self._frdls_info.smaxcol + 1 + 1 + 1, self.begin_y + self.nlines - 1 - 4 - 1, self.begin_x + self.ncols - 1 - 1)
        self._command_info = WinInfo(self.begin_y + self.nlines - 1 - 1 - 1, self.begin_x + 1, self.begin_y + self.nlines - 1 - 1 - 1, self.begin_x + self.ncols -1 -1)
        self._statusbar_info = WinInfo(self.begin_y + self.nlines - 1, self.begin_x, self.begin_y + self.nlines - 1, self.begin_x + self.ncols - 1)

    def set_win_color(self, wininfo, colorpair):
        line = wininfo.sminrow
        while line <= wininfo.smaxrow:
            self.stdscr.chgat(line, wininfo.smincol, wininfo.smaxcol - wininfo.smincol + 1, curses.color_pair(colorpair))
            line = line + 1

    def create_win(self):
        self.frdls = FrdLs(self.stdscr, self._frdls_info.smaxcol - self._frdls_info.smincol + 1, self._frdls_info.sminrow, self._frdls_info.smincol, self._frdls_info.smaxrow, self._frdls_info.smaxcol, self.friends, Config['color']['frdls']['fgcolor'], Config['color']['frdls']['bgcolor'])
        self.msgls_set[self.current_receiver] = MsgLs(self.stdscr, self._msgls_info.smaxcol - self._msgls_info.smincol + 1, self._msgls_info.sminrow, self._msgls_info.smincol, self._msgls_info.smaxrow, self._msgls_info.smaxcol, [], fgcolor=Config['color']['msgls']['fgcolor'], bgcolor=Config['color']['msgls']['bgcolor'])
        self.input = Input(self.stdscr, self._input_info.smaxcol - self._input_info.smincol + 1, self._input_info.sminrow, self._input_info.smincol, self._input_info.smaxrow, self._input_info.smaxcol, self.text, Config['color']['input']['fgcolor'], Config['color']['input']['bgcolor'])
        self.command = Command(self.stdscr, self._command_info.smaxrow - self._command_info.sminrow + 1, self._command_info.sminrow, self._command_info.smincol, self._command_info.smaxrow, self._command_info.smaxcol, self.command, Config['color']['command']['fgcolor'], Config['color']['command']['bgcolor'])
        self.statusbar = StatusBar(self.stdscr, 1, self._statusbar_info.smaxcol - self._statusbar_info.smincol + 1, self._statusbar_info.sminrow, self._statusbar_info.smincol, self._statusbar_info.smaxrow, self._statusbar_info.smaxcol, "NORMAL", "xxxxxx", fgcolor=curses.COLOR_BLACK, bgcolor=curses.COLOR_WHITE)

    def resize(self, nlines, ncols, begin_y=0, begin_x=0):
        self.nlines  = nlines
        self.ncols   = ncols
        self.begin_y = begin_y
        self.begin_x = begin_x

    def draw(self):
        self.frdls.draw()
        self.msgls_set[self.current_receiver].draw()
        self.input.draw()
        self.command.draw()
        self.statusbar.draw()
    
    def refresh(self):
        self.stdscr.refresh()
        self.frdls.refresh()
        self.msgls_set[self.current_receiver].refresh()
        self.input.refresh()
        self.command.refresh()
        self.statusbar.refresh()
    
    def clear(self):
        self.stdscr.clear()
        self.frdls.clear()
        self.msgls_set[self.current_receiver].clear()
        self.input.clear()
        self.command.clear()
        self.statusbar.clear()

    def run(self):
        self.connect(URL)
        self.event_listenning()
        while True:
            ch = self.stdscr.getch()
            if ch == curses.KEY_RESIZE:
                self.on_key_resize()
            elif ch == 27:
                self.on_key_esc()
            elif self.mode == MODE_NORMAL:
                if ch == ord('q'):
                    if self.logged_in:
                        self.sio.emit('logout', {}, callback=lambda res: self.sio.disconnect())
                    else:
                        self.sio.emit('quit', {}, callback=lambda: self.sio.disconnect())
                    break
                else:
                    self.on_normal(ch)
            elif self.mode == MODE_FRDLS:
                self.on_frdls(ch)
            elif self.mode == MODE_MSGLS:
                self.on_msgls(ch)
            elif self.mode == MODE_INPUT:
                self.on_input(ch)
            elif self.mode == MODE_COMMAND:
                self.on_command(ch)

    def on_key_resize(self):
        nlines, ncols = self.stdscr.getmaxyx()
        if nlines >= 25 and ncols >= 55:
            self.clear()
            self.friends = self.frdls.friends
            self.msgs = self.msgls_set[self.current_receiver].msgs
            self.text = self.input.text
            self.command = self.command.command
            self.resize(nlines, ncols)
            self.cal_wininfo()
            self.set_win_color(self._frdls_info, 1)
            self.set_win_color(self._msgls_info, 2)
            self.set_win_color(self._input_info, 3)
            self.set_win_color(self._command_info, 4)
            self.create_win()
            self.draw()
            self.refresh()
        else:
            self.stdscr.clear()
            try:
                curses.init_pair(6, curses.COLOR_RED, curses.COLOR_BLACK)
                self.stdscr.addstr(int(nlines / 2), int((ncols - len("TOO SMALL")) / 2), "TOO SMALL", curses.color_pair(6))
            except curses.error:
                pass
            self.stdscr.refresh()
        
    def on_key_esc(self):
        self.mode = MODE_NORMAL
        self.statusbar.mode = "NORMAL"
        self.statusbar.content()
        self.statusbar.refresh()
    
    def on_normal(self, ch):
        if ch == ord('f'):
            self.mode = MODE_FRDLS
            self.statusbar.mode = "FRDLS"
            self.statusbar.content()
            self.statusbar.refresh()
        elif ch == ord('m'):
            self.mode = MODE_MSGLS
            self.statusbar.mode = "MSGLS"
            self.statusbar.content()
            self.statusbar.refresh()
        elif ch == ord('i'):
            self.mode = MODE_INPUT
            self.statusbar.mode = "INPUT"
            self.statusbar.content()
            self.statusbar.refresh()
        elif ch == ord('c'):
            self.mode = MODE_COMMAND
            self.statusbar.mode = "COMMAND"
            self.statusbar.content()
            self.statusbar.refresh()
        elif ch == ord('r'):
            # reconnect
            self.connect(URL)
    
    def on_frdls(self, ch):
        if ch == curses.KEY_UP:
            self.frdls.current_row_style(curses.color_pair(self.frdls.color_pair))
            self.frdls.onkeyup()
            self.frdls.current_row_style(curses.A_REVERSE)
            self.refresh()
        elif ch == curses.KEY_DOWN:
            self.frdls.current_row_style(curses.color_pair(self.frdls.color_pair))
            self.frdls.onkeydown()
            self.frdls.current_row_style(curses.A_REVERSE)
            self.refresh()
        elif ch == ord('\n'):
            receiver = self.frdls.friends[self.frdls.current_row - 1]
            if receiver != self.user['username']:
                self.msgls_set[self.current_receiver].clear()
                self.msgls_set[self.current_receiver].refresh()
                self.current_receiver = receiver
                self.msgls_set[self.current_receiver].content()
                self.msgls_set[self.current_receiver].refresh()
                
                self.mode = MODE_INPUT
                self.statusbar.mode = "INPUT"
                self.statusbar.content()
                self.statusbar.refresh()

    def on_msgls(self, ch):
        if ch == curses.KEY_UP:
            self.msgls_set[self.current_receiver].current_row_style(self.msgls_set[self.current_receiver].color_pair)
            self.msgls_set[self.current_receiver].onkeyup()
            self.msgls_set[self.current_receiver].current_row_style(curses.A_REVERSE)
            self.msgls_set[self.current_receiver].refresh()
        elif ch == curses.KEY_DOWN:
            self.msgls_set[self.current_receiver].current_row_style(self.msgls_set[self.current_receiver].color_pair)
            self.msgls_set[self.current_receiver].onkeydown()
            self.msgls_set[self.current_receiver].current_row_style(curses.A_REVERSE)
            self.msgls_set[self.current_receiver].refresh()

    def on_input(self, ch):
        if ch == curses.KEY_BACKSPACE:
            self.input.delete()
            self.input.clear()
            self.input.refresh()
            self.input.content()
            self.input.ondelete()
            self.set_win_color(self._input_info, 3)
            self.stdscr.refresh()
            self.input.refresh()
        elif ch == curses.KEY_UP:
            self.input.onkeyup()
            self.input.refresh()
        elif ch == curses.KEY_DOWN:
            self.input.onkeydown()
            self.input.refresh()
        elif ch == ord('\n'):
            msg = Msg(self.user['username'], self.current_receiver, self.input.text, time.strftime('%H:%M:%S', time.localtime(time.time()))) 
            self.sio.emit('message', {'receiver': self.current_receiver, 'message': self.input.text}, callback=lambda res: self.onmessage(res, msg))
            self.input.text = ''
            self.input.clear()
            self.input.refresh()
            self.input.content()
            self.set_win_color(self._input_info, 3)
            self.stdscr.refresh()
            self.input.refresh()
        else:
            self.input.read(ch)
            self.input.content()
            self.input.oninsert()
            self.input.refresh()
    
    def on_command(self, ch):
        if ch == curses.KEY_LEFT:
            self.command.onkeyleft()
            self.command.refresh()
        elif ch == curses.KEY_RIGHT:
            self.command.onkeyright()
            self.command.refresh()
        elif ch == curses.KEY_BACKSPACE:
            self.command.delete()
            self.command.clear()
            self.command.refresh()
            self.command.content()
            self.command.ondelete()
            self.set_win_color(self._command_info, 4)
            self.stdscr.refresh()
            self.command.refresh()
        elif ch == ord('\n'):
            res = self.command.reslove()
            self.exec_cmd(res)
            self.command.command = ''
            self.command.clear()
            self.command.refresh()
            self.command.content()
            self.set_win_color(self._command_info, 4)
            self.stdscr.refresh()
            self.command.refresh()
        else:
            self.command.read(ch)
            self.command.content()
            self.command.oninsert()
            self.command.refresh()
    
    def exec_cmd(self, cmd):
        if cmd['status'] == COMMAND_IS_EMPTY:
            self.prompt('command is empty')
        else:
            if cmd['cmd'] == 'login':
                self.login(cmd['parms'])
            elif cmd['cmd'] == 'register':
                self.register(cmd['parms'])
            elif cmd['cmd'] == 'logout':
                self.logout(cmd['parms'])
            elif cmd['cmd'] == 'sendfile':
                self.sendfile(cmd['parms'])
            else:
                self.prompt('command undefined')    

    def connect(self, url):
        try:
            self.sio.connect(url)
        except socketio.exceptions.ConnectionError as e:
            self.prompt(str(e))
        except ValueError as e:
            self.prompt(str(e))
        else:
            self.prompt('successful connection')        

    def login(self, parms):
        if len(parms) != 2:
            self.prompt('parms error')
        else:
            username = parms[0]
            password = parms[1]
            try:
                self.sio.emit('login', {'username': username, 'password': password}, callback=lambda res: self.onlogin(username, res))
            except socketio.exceptions.ConnectionError as e:
                self.prompt(str(e))

    def register(self, parms):
        if len(parms) != 2:
            self.prompt('parms error')
        else:
            username = parms[0]
            password = parms[1]
            try:
                self.sio.emit('register', {'username': username, 'password': password}, callback=lambda res: self.onregister(res))
            except socketio.exceptions.ConnectionError as e:
                self.prompt(str(e))

    def logout(self, parms):
        if len(parms) != 0:
            self.prompt('parms error')
        else:
            self.sio.emit('logout', '', callback=lambda res: self.onlogout(res))
        
    def sendfile(self, parms):
        if len(parms) != 1:
            self.prompt('parms error')
        else:
            filepath = parms[0]
            if (not os.path.exists(filepath)) or (not os.path.isfile(filepath)):
                self.prompt('can not found file {}'.format(filepath))
            else:
                self.filepath = filepath
                self.file_receiver = self.current_receiver
                try:
                    self.sio.emit('fconnect', {'name': self.user['username'], 'filename': os.path.split(filepath)[0], 'filesize': os.path.getsize(filepath)})
                except socketio.exceptions.ConnectionError as e:
                    self.prompt(str(e))

    
    def prompt(self, prompt):
        self.statusbar.other = prompt
        self.statusbar.clear()
        self.statusbar.refresh()
        self.statusbar.content()
        self.statusbar.refresh()

    def event_listenning(self):
        @self.sio.on('connect')
        def connect():
            pass

        @self.sio.on('disconnect')
        def disconnect():
            pass

        @self.sio.on('friend_login')
        def friend_login(friend):
            self.frdls.friends.append(friend)
            self.frdls.content()
            self.frdls.refresh()
            self.msgls_set[friend] =  MsgLs(self.stdscr, self._msgls_info.smaxcol - self._msgls_info.smincol + 1, self._msgls_info.sminrow, self._msgls_info.smincol, self._msgls_info.smaxrow, self._msgls_info.smaxcol, [], receiver=friend)

        @self.sio.on('friend_logout')
        def friend_logout(friend):
            self.frdls.clear()
            self.frdls.refresh()
            self.frdls.friends.remove(friend)
            self.frdls.content()
            self.frdls.refresh()
            self.msgls_set.pop(friend)
        
        @self.sio.on('user_online')
        def user_online(users):
            for friend in users['users']:
                self.frdls.friends.append(friend)
                self.msgls_set[friend] =  MsgLs(self.stdscr, self._msgls_info.smaxcol - self._msgls_info.smincol + 1, self._msgls_info.sminrow, self._msgls_info.smincol, self._msgls_info.smaxrow, self._msgls_info.smaxcol, [], receiver=friend)
            self.frdls.content()
            self.frdls.refresh()
        
        @self.sio.on('message')
        def message(msg):
            sender = msg['sender']
            message = msg['message']
            msg = Msg(sender, self.user['username'], message, time.strftime('%H:%M:%S', time.localtime()))
            self.msgls_set[sender].add_msg(msg)
            if sender == self.current_receiver:
                self.msgls_set[self.current_receiver].content()
                self.msgls_set[self.current_receiver].move2bottom()
                self.msgls_set[self.current_receiver].refresh()
            self.prompt("Receive messages from " + sender)
        
        @self.sio.on('connect_ok')
        def connect_ok(data):
            th = threading.Thread(target=self._sendfile)
            th.start()
            th.join()
            self.prompt('file has sended')
        
        @self.sio.on('fconnect')
        def fconnect(data):
            self.file_sender = data['name']
            self.sio.emit('connect_ok', {'name': self.file_sender})
            th = threading.Thread(target=self._recvfile, args=(data['filename'], data['filesize']))
            th.start()
            th.join()
            self.prompt('file has recved')


        
    def onlogin(self, username, res):
        if res['code'] == 0 or res['code'] == 1:
            self.logged_in = True
            self.user['username'] = username
        self.prompt(res['text'])
    
    def onmessage(self, res, msg):
        if res['code'] == 1:
            self.prompt(res['text'])
            self.msgls_set[self.current_receiver].add_msg(msg)
            self.msgls_set[self.current_receiver].content()
            self.msgls_set[self.current_receiver].move2bottom()
            self.msgls_set[self.current_receiver].refresh()
        else:
            self.prompt(res['text'])
    
    def onlogout(self, res):
        if res['code'] == 1:
            self.logged_in = False
            self.init_variable()
            self.create_win()
            self.draw()
            self.refresh()
        self.prompt(res['text'])
    
    def onregister(self, res):
        self.prompt(res['text'])
    
    def _sendfile(self):
        fsio = socketio.Client()
        fsio.connect('http://localhost:1234')

        @fsio.on('end')
        def end(data):
            fsio.disconnect()

        @fsio.on('recv_ok')
        def recv_ok(data):
            self.prompt(str(data['has']))

        with open(self.filepath, 'rb') as f:
            buffer = f.read(10)
            block = 1
            while buffer:
                fsio.emit('send_file', {'block': block, 'data': buffer})
                buffer = f.read(10)
                block = block + 1
        fsio.wait()

    def _recvfile(self, filename, filesize):
        fsio = socketio.Client()
        fsio.connect('http://localhost:1234')

        file = {
            'recv_bytes': 0,
            'file_buffer': []
        }

        @fsio.on('end')
        def end(data):
            fsio.disconnect()

        @fsio.on('recv_file')
        def recv_file(data):
            file['recv_bytes'] = file['recv_bytes'] + len(data['data'])
            file['file_buffer'].append((data['block'], data['data']))
            fsio.emit('recv_ok', {'has': '[{:.2f}%]'.format((file['recv_bytes'] / filesize) * 100)})
            self.prompt('[{:.2f}%]'.format((file['recv_bytes'] / filesize) * 100))
            if file['recv_bytes'] == filesize:
                file['file_buffer'].sort(key=lambda data: data[0])
                with open('xxx.txt', 'ab+') as f:
                    for block in file['file_buffer']:
                        f.write(block[1])
                fsio.emit('end', {})
        fsio.wait()