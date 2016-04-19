#!/usr/bin/python
# -*- coding: utf-8 -*-
import msvcrt
from lib.termui import *

class loginScreen(screen):
	def __init__(self, height, width):
		screen.__init__(self, height, width, hasTab = False)
		self.TitleWindow = window("0", "title", 3, 100)
		self.loginWindow = self.newWindow("1", "Login", 27, 100)
		self.RegisterWindow = self.newWindow("2","Register", 27, 100)
		self.TitleWindow.forcus = lambda : False
		self.initTitle()
		self.initLogin()
		self.initRegister()
		self.chWindow(self.loginWindow)
		self.addHandler(handler.LEFT, lambda a,b : 1 == 1)# Cannot Shift Window
		self.addHandler(handler.RIGHT, lambda a,b : 1 == 1)
		self.addHandler(handler.ESC, lambda a,b : self.close())
		
	def initTitle(self):
		self.TitleWindow.holeArea = self.TitleWindow.newArea(0, "Hole", 1, 97, 1, 1, focusable = False)
		self.TitleWindow.holeArea.goto(40, 0); self.TitleWindow.holeArea.putLine("欢迎来到XXX！")
	
	def initLogin(self):
		self.loginWindow.holeArea = self.loginWindow.newArea(0, "Hole", 25, 97, 1, 1, focusable = False)
		self.loginWindow.holeArea.goto(40, 6); self.loginWindow.holeArea.putLine("登        录")
		self.loginWindow.holeArea.goto(30, 9); self.loginWindow.holeArea.putLine("用户名：")
		self.loginWindow.holeArea.goto(30, 14); self.loginWindow.holeArea.putLine("密  码：")
		self.loginWindow.nameEditor = input(1, "username", 1, 20)
		self.loginWindow.addArea(self.loginWindow.nameEditor, 40, 10)
		self.loginWindow.passwordEditor = password(2, "password", 1, 20, maxLen=8)
		self.loginWindow.addArea(self.loginWindow.passwordEditor, 40, 15)
		self.loginWindow.registerBtn = button(3, "去注册", 1, 10)
		self.loginWindow.addArea(self.loginWindow.registerBtn, 35, 18)
		self.loginWindow.registerBtn.onClick = lambda:self.chWindow(self.RegisterWindow)
		self.loginWindow.submitBtn = button(4, "确定", 1, 10)
		self.loginWindow.addArea(self.loginWindow.submitBtn, 50, 18)
		self.loginWindow.submitBtn.onClick = lambda:self.login()
		self.loginWindow.chArea(self.loginWindow.nameEditor)
	
	def initRegister(self):
		self.RegisterWindow.holeArea = self.RegisterWindow.newArea(0, "Hole", 25, 97, 1, 1, focusable = False)
		self.RegisterWindow.holeArea.goto(40, 4); self.RegisterWindow.holeArea.putLine("注        册")
		self.RegisterWindow.holeArea.goto(30, 7); self.RegisterWindow.holeArea.putLine("用 户 名：")
		self.RegisterWindow.holeArea.goto(30, 12); self.RegisterWindow.holeArea.putLine("密    码：")
		self.RegisterWindow.holeArea.goto(30, 17); self.RegisterWindow.holeArea.putLine("重复密码：")
		self.RegisterWindow.nameEditor = input(1, "username", 1, 20)
		self.RegisterWindow.addArea(self.RegisterWindow.nameEditor, 40, 8)
		self.RegisterWindow.passwordEditor = password(2, "password", 1, 20, maxLen=8)
		self.RegisterWindow.addArea(self.RegisterWindow.passwordEditor, 40, 13)
		self.RegisterWindow.repasswordEditor = password(3, "repassword", 1, 20, maxLen=8)
		self.RegisterWindow.addArea(self.RegisterWindow.repasswordEditor, 40, 18)
		self.RegisterWindow.loginBtn = button(4, "去登录", 1, 10)
		self.RegisterWindow.addArea(self.RegisterWindow.loginBtn, 35, 21)
		self.RegisterWindow.loginBtn.onClick = lambda:self.chWindow(self.loginWindow)
		self.RegisterWindow.submitBtn = button(5, "确定", 1, 10)
		self.RegisterWindow.addArea(self.RegisterWindow.submitBtn, 50, 21)
		self.RegisterWindow.submitBtn.onClick = lambda:self.register()
		self.RegisterWindow.chArea(self.RegisterWindow.nameEditor)
	
	def login(self):
		name = self.loginWindow.nameEditor.getText()
		password = self.loginWindow.passwordEditor.getText()
		if name == '' or password == '':
			return
		self.do_login(name, password)
	def do_login(self, name, password):
		loginSuccess()
		pass
	
	def register(self):
		name = self.RegisterWindow.nameEditor.getText()
		password = self.RegisterWindow.passwordEditor.getText()
		repassword = self.RegisterWindow.repasswordEditor.getText()
		if name == '' or password == '' or repassword == '':
			return 
		if password != repassword:
			return
		#raise Exception("name:" + name + "\npassword:" + password + "\nrepassword:" + repassword)
		self.do_register(name, password, repassword)
	def do_rigister(self, name, password, repassword):
		pass
	
	def close(self):
		self.doConfirm("确认关闭聊天室？", Quit, None)
	
	def refresh(self):
		os.system('cls')
		self.TitleWindow.refresh()
		self.curWindow.refresh()

class chatScreen(screen):
	def __init__(self, height, width):
		screen.__init__(self, height, width, hasTab = True)
		self.hall = Hall(height - 3, width)			#New Hall
		self.addWindow(self.hall)
		self.addHandler(handler.HOME, lambda a,b : self.chWindow(self.hall))
		self.addHandler(handler.CTRLN, lambda a,b : self.doPrompt("请输入房间名称：", self.createRoom, None))
	
	def newChat(self, object):
		if self.windows.has_key(object.id):
			self.chChat(self.windows[object.id])
			return
		if isinstance(object, user):
			_chat = userChat(object, 27, 100)
		elif isinstance(object, room):
			_chat = roomChat(object, 27, 100)
		else:
			return
		self.addWindow(_chat)
		self.chChat(_chat)
	def openChat(self, object):
		self.do_open_chat(object)
		pass
	def createRoom(self, name):
		self.do_create_room(name)
	def enterRoom(self, room):
		self.do_enter_room(room)
	def leaveRoom(self, room):
		if self.windows.has_key(room.id):
			self.do_leave_room(room.id)
		pass
	
	def chChat(self, _chat):
		if _chat.focus():
			self.curWindow = _chat
			return True
		else:
			return False
	
	def do_logout(self):
		pass
	def do_create_room(self, name):
		pass
	def do_enter_room(self, room):
		pass	
	def do_leave_room(self, id):
		pass
	def do_send_msg(self, target, content):
		pass
	def do_open_chat(self, object):
		self.newChat(object)
		pass
	
	def closeChat(self, _chat):
		self.closeWindow(_chat)
		
class chat(window):
	def __init__(self, object, height, width):
		window.__init__(self, object.id, object.name, height, width)
		self.object = object
		
		self.talkArea = self.newArea(1, 'talk', 17, 70, 2, 1)		
		self.inputArea = editor(4, "inputArea", 6, 70)
		self.addArea(self.inputArea, 2, 20)
		
		self.inputArea.keyEnter = self.sendMsg
		
	def addMsg(self, who = '', when = '', what = ''):
		if(who.strip() == '' or when.strip ()== '' or what.strip() == ''):
			return 
		self.talkArea.putStr("[" + who.strip() + "] Say (@" + when.strip() + "):")
		self.talkArea.putStr("  " + what)
		self.talkArea.drawLine(' ')
	
	def sendMsg(self, text):
		self.screen.do_send_msg(self.id, text)
		pass
		
	def close(self):
		if self.screen:
			self.screen.closeChat(self)
		
class userChat(chat):
	def __init__(self, object, height, width):
		chat.__init__(self, object, height, width)
		self.infoArea = self.newArea(2, 'ru', 25, 25, 74, 1)
		self.infoArea.goto(1,2)
		self.infoArea.putStr(self.object.info())
		self.chArea(self.inputArea)
	
class roomChat(chat):
	def __init__(self, object, height, width):
		chat.__init__(self, object, height, width)
		
		self.gameArea = self.newArea(2, 'ru', 10, 25, 74, 1)
		self.userlist = listArea(3, 'userlist', 13, 25)
		self.addArea(self.userlist, 74, 13)
		self.userlist.keyEnter = self.openChat
		self.chArea(self.inputArea)

		self.getUserList()
		self.userlist.setCursor('u1')
		
	#Need modify
	def getUserList(self):
		self.userlist.listData.clear()
		userlist = {'u1':"用户1",'u2':"用户2",'u3':"用户3",'u4':"用户4"}
		for id, name in userlist.items():
			_user = user(id, name)
			self.userlist.listData[id] = _user
			
	def flashUserList(self, userlist):
		self.userlist.listData.clear()
		for item in userlist:
			_user= user(item["id"], item["name"].encode("gbk"))
			self.userlist.listData[item["id"]] = _user
		if(len(self.userlist.listData.keys()) > 0):
			self.userlist.setCursor(self.userlist.listData.keys()[0])

	def openChat(self, _user):
		self.screen.newChat(_user)
	
	def close(self):
		self.screen.leaveRoom(self.object)
		#chat.close(self)

			
class Hall(window):
	def __init__(self, height, width):
		window.__init__(self, 0, "大厅", height, width)
		
		self.roomlist = listArea(1, 'roomlist', 25, 70)
		self.addArea(self.roomlist, 2, 1)
		self.roomlist.keyEnter = self.enterRoom
		
		self.userlist = listArea(3, 'userlist', 25, 25)
		self.addArea(self.userlist, 74, 1)
		self.userlist.keyEnter = self.openChat
		#self.inputArea = editor(2, "inputArea", 6, 25, maxLen = 3)
		#self.addArea(self.inputArea, 74, 20)
		self.chArea(self.roomlist)

		self.getRoomList()
		self.roomlist.setCursor(self.roomlist.listData.keys()[0])
	
	#Need modify
	def getRoomList(self):
		self.roomlist.listData.clear()
		roomlist = [{"id":1, "name":"room 1"}, {"id":2, "name":"room 2"}]
		for item in roomlist:
			_room = room(item["id"], item["name"])
			self.roomlist.listData[item["id"]] = _room
			
	def flashRoomList(self, roomlist):
		self.roomlist.listData.clear()
		for item in roomlist:
			_room = room(item["id"], item["name"].encode("gbk"))
			self.roomlist.listData[item["id"]] = _room
		if(len(self.roomlist.listData.keys()) > 0):
			self.roomlist.setCursor(self.roomlist.listData.keys()[0])
			
	#Need modify
	def getUserList(self):
		self.userlist.listData.clear()
		userlist = {'u1':"用户1",'u2':"用户2",'u3':"用户3",'u4':"用户4"}
		for id, name in userlist.items():
			_user = user(id, name)
			self.userlist.listData[id] = _user
			
	def flashUserList(self, userlist):
		self.userlist.listData.clear()
		for item in userlist:
			_user= user(item["id"], item["name"].encode("gbk"))
			self.userlist.listData[item["id"]] = _user
		if(len(self.userlist.listData.keys()) > 0):
			self.userlist.setCursor(self.userlist.listData.keys()[0])

	def enterRoom(self, _room):
		self.screen.enterRoom(_room)
		
	def openChat(self, _user):
		self.screen.openChat(_user)
		pass
		
	def forcus(self):
		self.screen.chWindow(self)
	
	def logout(self):
		self.screen.do_logout()
		pass
		
	# Cannot Close
	def close(self):
		self.screen.doConfirm("确认退出登录？", self.logout, None)

class room:
	def __init__(self, id, name):
		self.userList = []
		self.id = id
		self.name = name
		pass
	
	def shortInfo(self):
		return self.name
		
	def info(self):
		return self.name

class user:
	def __init__(self, id, name):
		self.id = id
		self.name = name
		pass
		
	def shortInfo(self):
		return self.name
	
	def info(self):
		return self.name + "\n\n  年龄:\n  性别:\n  在线时长:\n"

scr = None
		
def loginSuccess():
	global scr
	tmp = scr
	scr = chatScreen(scr.height, scr.width)
	del tmp
	
def logoutSuccess():
	global scr
	tmp = scr
	scr = loginScreen(scr.height, scr.width)
	del tmp
	
def Quit():
	global scr
	del scr
	os.system("cls")
	print "已退出聊天室，欢迎再来!"
	quit()

if __name__ == '__main__':
	scr = chatScreen(30, 100)
	chh = ''
	while True:
		scr.refresh()
		ch = msvcrt.getch()
		#rs.curWindow.talkArea.putLine("Press " + str(ord(ch)))
		if chh != '':
			ch = chh + ch
			scr.handle(ch)
			chh = ''
		elif ord(ch) > 127:				# Unicode
			
			chh = ch
		elif ch == chr(26):				# Ctrl-Z Quit
			break
			continue
		else:
			scr.handle(ch)
			#rs.curWindow.talkArea.putLine("You press " + ch)
		