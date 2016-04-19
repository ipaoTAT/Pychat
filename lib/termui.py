#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import msvcrt

#screen level
class screen:
	#Constructor
	#'hasTab' : Whether contains tab
	def __init__(self, height = 27, width = 100, hasTab = True):
		#First of all, set window size
		os.system("MODE con: COLS=" + str(width + 1)+" LINES=" + str(height + 2))
		self.windows ={}			#Window set
		self.height = height		#Properties
		self.width = width
		self.tabWindow = None
		#Special Windows
		if hasTab:						#
			self.tabWindow = tabWindow(self, 'tab', 3, width)
			
		self.emptyWindow = window(None, 'None', height - 3, width)
		self.alertWindow = None
		self.curWindow = self.emptyWindow
		# keyboard mapping handler
		self.keyHandler = {}
		
		#add key handler
		self.addHandler(handler.LEFT, lambda a,b : self.shiftLeft())# Ctrl + A for Shift to left window
		self.addHandler(handler.RIGHT, lambda a,b : self.shiftRight())# Ctrl + L for Shift to right window
		
	def newWindow(self, id, title, height, width):
		win = window(id, title, height, width)
		self.addWindow(win)
		self.chWindow(win)
		return win	
		
	def addWindow(self, win):
		if self.windows.has_key(win.id):
			return False
		win.screen = self
		self.windows[win.id] = win
		self.chWindow(win)
		return True
	
	def chWindow(self, _window):
		if _window.focus() and (self.curWindow == None or self.curWindow.blur()):
			self.curWindow = _window
			return True
		else:
			return False
	
	def closeWindow(self, win):
		if not self.windows.has_key(win.id):
			return False
		if win == self.curWindow and self.shiftLeft() == False:
			self.chWindow(self.emptyWindow)
		_win = self.windows.pop(win.id)
		del _win
		return True
	
	def shiftLeft(self):
		index = self.windows.values().index(self.curWindow)
		i = (index - 1) % len(self.windows)
		while i != index:
			if self.chWindow(self.windows.values()[i]):
				return True
			i = (i - 1) % len(self.windows)
		if i == index:
			return False
	def shiftRight(self):
		index = self.windows.values().index(self.curWindow)
		i = (index + 1) % len(self.windows)
		while i != index:
			if self.chWindow(self.windows.values()[i]):
				return True
			i = (i + 1) % len(self.windows)
		if i == index:
			return False
	
	def addHandler(self, key, handler):
		self.keyHandler[key] = handler
	
	def handle(self, key):
		if self.keyHandler.has_key(key):
			self.keyHandler[key](self, key)
		elif self.curWindow:
			if self.curWindow.handle(key) == False:
				return False
		#self.refresh()
		return True

	def doAlert(self, title, yesHandler = None):
		if self.alertWindow:
			self.alertWindow.cancel()
			self.alertWindow = None
		self.alertWindow = alert(self, title, self.height, self.width)
		if yesHandler:
			self.alertWindow.doYes = yesHandler 
		self.alertWindow.preWindow  = self.curWindow
		self.addWindow(self.alertWindow)
	def doConfirm(self, title, yesHandler = None, noHandler = None):
		if self.alertWindow:
			self.alertWindow.cancel()
			self.alertWindow = None
		self.alertWindow = confirm(self, title, self.height, self.width)
		if yesHandler:
			self.alertWindow.doYes = yesHandler 
		if noHandler:
			self.alertWindow.doNo = noHandler
		self.alertWindow.preWindow  = self.curWindow
		self.addWindow(self.alertWindow)
	def doPrompt(self, title, yesHandler = None, noHandler = None):
		if self.alertWindow:
			self.alertWindow.cancel()
			self.alertWindow = None
		self.alertWindow = prompt(self, title, self.height, self.width)
		if yesHandler:
			self.alertWindow.doYes = yesHandler 
		if noHandler:
			self.alertWindow.doNo = noHandler
		self.alertWindow.preWindow  = self.curWindow
		self.addWindow(self.alertWindow)
		
	def refresh(self):
		os.system('cls')
		if self.alertWindow:
			self.alertWindow.refresh()
			return
		#draw tab
		if self.tabWindow:
			self.tabWindow.refresh()
		self.curWindow.refresh()
	
	def __del__(self):
		for key,win in self.windows.items():
			del win
		del self.tabWindow
		del self.emptyWindow

class window:
	def __init__(self, id, title, height, width):
		self.id = id
		self.screen = None
		self.title = title
		self.height = height
		self.width = width
		self.content = []
		self.areas = {}
		self.curArea = None
		# keyboard mapping handler
		self.keyHandler = {}
		# init content 
		for i in range (0, self.height):
			self.content.append(list(' ' * self.width))
			
		#add key handler
		self.addHandler(handler.TAB, lambda a,b:self.shiftRight())# RIGHT for Shift 2 right Area
		self.addHandler(handler.ESC, lambda a,b:self.close())		# ESC for Close Window
	
	def newArea(self, id, title, height = 0, width = 0, posX = 0, posY = 0, border = True, focusable = True):
		_area = area(id, title, height, width, border, focusable)
		self.addArea(_area, posX, posY)
		return _area
	
	def addArea(self, _area, posX = 0, posY = 0):
		if self.areas.has_key(_area.id):
			return False
		_area.posX = posX; _area.posY = posY
		_area.window = self
		self.areas[_area.id] = _area
		self.chArea(_area)
		return True
			
	def handle(self, key):
		if self.keyHandler.has_key(key):
			self.keyHandler[key](self, key)
			return True
		elif self.curArea:
			return self.curArea.handle(key)

	def chArea(self, _area):
		if _area.focus():
			if self.curArea:
				self.curArea.blur()
			self.curArea = _area
			return True
		else:
			return False
			
	def shiftLeft(self):
		index = self.areas.values().index(self.curArea)
		i = (index - 1) % len(self.areas)
		while i != index:
			if self.chArea(self.areas.values()[i]):
				return True
			i = (i - 1) % len(self.areas)
		if i == index:
			return False			
	def shiftRight(self):
		index = self.areas.values().index(self.curArea)
		i = (index + 1) % len(self.areas)
		while i != index:
			if self.chArea(self.areas.values()[i]):
				return True
			i = (i + 1) % len(self.areas)
		if i == index:
			return False
	
	def addHandler(self, key, handler):
		self.keyHandler[key] = handler
	
	def refresh(self):
		# dort by id as z-index
		keys = self.areas.keys() 
		keys.sort()
		for key in keys:
			_area = self.areas[key]
			if _area == self.curArea:
				continue
			# add area content to window
			_area.refresh()
		if self.curArea:
			self.curArea.boxStyle = ['-', '|','-','|']
			self.curArea.refresh()
			self.curArea.boxStyle = ['.', '.','.','.']
		for line in self.content:
			print "".join(line)
	
	def focus(self):
		return True if self.screen else False
	def blur(self):
		return True
			
	def close(self):
		if self.screen:
			self.screen.closeWindow(self)
			
	def __del__(self):
		for key, _area in self.areas.items():
			del _area

class area:
	def __init__(self, id, title, height = 0, width = 0, border = False, focusable = True):
		self.id = id
		self.title = title
		self.window = None		#Parent Container
		self.height = height
		self.width = width
		self.border = border			# properties
		self.focusable = focusable
		self.content = []			#Display Buffer
		self.startLine = 0			#Start display line
		self.posX = 0				#Position in Parent container
		self.posY = 0
		self.curX = 0				#Cursor
		self.curY = 0
		self.MAX_LINES = 2 * self.height	#
		self.boxStyle = ['.', '.','.','.']	#Box board style for [top, left, bottom, right]
		self.keyHandler = {}				#Keyboard Event - Handler Mappings

		self.addHandler(handler.CTRLA, lambda a,b:self.keyUp())		# UP 
		self.addHandler(handler.UP, lambda a,b:self.keyUp())		# UP 
		self.addHandler(handler.DOWN, lambda a,b:self.keyDown())		# DOWN 
		self.addHandler(handler.PAGEUP, lambda a,b:self.keyPageUp())	# Page UP 
		self.addHandler(handler.PAGEDOWN, lambda a,b:self.keyPageDown())	# Page DOWN 
		
		for i in range (0, self.height):		#Init Display buffer
			self.newLine()
			
	def newLine(self):
		line = list(' ' * self.width)
		line.append(0)
		self.content.append(line)
		if len(self.content) > 2 * self.MAX_LINES and self.startLine > self.MAX_LINES:
			self.content = self.content[self.MAX_LINES:]
			self.curX = self.curX - self.MAX_LINES	#Cursor
			self.curY = self.curY - self.MAX_LINES
			self.startLine = self.startLine - self.MAX_LINES
	
	def clear(self):
		self.content = self.content[:self.height]
		for line in self.content:
			line[0 : self.width] = list(' ' * self.width)
			line[self.width] = 0
		self.curX = 0
		self.curY = 0
		self.startLine = 0
		
	def goto(self, x, y):
		self.curX = x
		self.curY = y
		while self.curY >= len(self.content):
			self.newLine()
		self.calculateStartLine()
	
	def putLine(self, s):
		# s should not contain '\n'
		s = "".join(s).replace('\n', '\\n')
		# end position
		end = self.curX + len(s)
		offset = 0
		while end > self.width:
			# line to end
			self.content[self.curY][self.curX : self.width] = list(s[offset:])[:self.width - self.curX]
			self.content[self.curY][self.width] = self.width
			end -= self.width
			offset += self.width - self.curX
			self.curY += 1
			# add one line
			if self.curY == len(self.content):
				self.newLine()
			self.curX = 0
		self.content[self.curY][self.curX : end] = list(s[offset:])[:end - self.curX]
		self.content[self.curY][self.width] = end
		self.curX = end
		self.calculateStartLine()
		
	def putStr(self, s):
		lines = s.split('\n')
		for line in lines:
			self.putLine(line)
			self.goto(0, self.curY + 1)
	
	def drawLine(self, ch):
		self.goto(0, self.curY)
		while len(ch) <= self.width - self.curX:
			self.putLine(ch)
	
	def deleteCh(self):
		if self.curX == 0:
			if self.curY == 0:
				return
			else:
				self.goto(self.content[self.curY - 1][self.width] - 1, self.curY - 1)
		else:
			self.goto(self.curX - 1, self.curY)
		self.content[self.curY][self.curX] = ' '
		self.content[self.curY][self.width] = self.content[self.curY][self.width] - 1
	
	def drawborder(self):
		_window = self.window
		#draw top line
		startX = self.posX - 1; endX = self.posX + self.width
		startY = self.posY - 1; endY = self.posY - 1
		#print "(",startX,",",startY,")->(",endX,",",endY,")"
		_window.content[startY][startX:endX] = list(self.boxStyle[0] * (endX - startX))
		#draw bottom line
		startX = self.posX - 1; endX = self.posX + self.width
		startY = self.posY + self.height; endY = self.posY + self.height;
		#print "(",startX,",",startY,")->(",endX,",",endY,")"
		_window.content[startY][startX:endX] = list(self.boxStyle[2] * (endX - startX))
		#draw left line
		startX = self.posX - 1; endX = startX
		startY = self.posY; endY = self.posY + self.height;
		#print "(",startX,",",startY,")->(",endX,",",endY,")"
		for i in range(startY, endY):
			_window.content[i][startX] = self.boxStyle[1]
			_window.content[i][startX + self.width + 1] = self.boxStyle[3]
	
	def calculateStartLine(self):
		if self.startLine > self.curY:
			self.startLine = self.curY
		elif self.startLine < self.curY - self.height:
			self.startLine = self.curY - self.height
	
	# no test
	def pageUp(self):
		self.startLine -= self.height
		if self.startLine <= self.height :
			self.startLine = 0
	
	# no test
	def pageDown(self):
		self.startLine += self.height
		if self.startLine > len(self.content) - self.height:
			self.startLine = len(self.content) - self.height
	
	def lineUp(self):
		self.startLine -= 1
		if self.startLine < 0:
			self.startLine = 0
		
	def lineDown(self):
		self.startLine += 1
		if self.startLine > len(self.content) - self.height:
			self.startLine = len(self.content) - self.height
	
	def addHandler(self, key, handler):
		self.keyHandler[key] = handler
	
	def handle(self, key):
		if self.keyHandler.has_key(key):
			self.keyHandler[key](self, key)
			return True
		else:
			return False
			
	#handlers
	def keyUp(self):
		self.lineUp()
	def keyDown(self):
		self.lineDown()
	def keyPageUp(self):
		self.pageUp()
	def keyPageDown(self):
		self.pageDown()
	
	def focus(self):
		return self.focusable if self.window else False
	def blur(self):
		pass
		
	def refresh(self):
		_window = self.window
		for i in range (0, self.height):
			if(i + self.posY > _window.height):
				break
			start = self.posX
			end = start + self.width
			if(start > _window.width):
				break
			if(end > _window.width):
				end = _window.width
			_window.content[self.posY + i][start : end] = self.content[i + self.startLine][0 : end - start]
		#Draw border
		if self.border:
			self.drawborder()
		return
		
	def _refresh(self):
		os.system('cls')
		for line in self.content:
			print "".join(line)

#tab window			
class tabWindow(window):
	def __init__(self, screen, title, height, width):
		window.__init__(self, None, title, height, width)
		self.screen = screen
		self.tabArea = self.newArea(0, 'tabArea', height, width, border = False)
		self.maxLen = 8
		
	def drawtab(self):
		#don't forget clear
		self.tabArea.clear()
		self.tabArea.goto(0,2)
		self.tabArea.drawLine('_')	
		index = 1
		self.tabArea.goto(index, 1)
		self.tabArea.putLine("│ ")
		for id, win in self.screen.windows.items():
			title_len = len(win.title)
			if win != self.screen.curWindow and title_len > self.maxLen:
				title_len = self.maxLen
			self.tabArea.goto(index + 1, 0)
			self.tabArea.putLine(list('_' * (title_len + 2)))
			self.tabArea.goto(index + 2, 1)
			self.tabArea.putLine(win.title[0:title_len] + " │ ")
			if win == self.screen.curWindow:
				self.tabArea.goto(index + 1, 0)
				self.tabArea.putLine(list('-' * (title_len + 2)))
				self.tabArea.goto(index + 1, 2)
				self.tabArea.putLine(list(' ' * (title_len + 3)))
			index += title_len + 3
		
	def focus(self):
		return False
		
	def refresh(self):
		self.drawtab()
		window.refresh(self)
					
	def __del__(self):
		window.__del__(self)
		del self.tabArea

#Confirm Window	
class alert(window):
	def __init__(self, screen, title, height, width):
		window.__init__(self, "alert", title, height, width)
		self.screen = screen
		self.title = title
		self.blurable = False
		self.background = self.newArea(-1, 'background', self.height - 2, self.width - 2, 1, 1, border = True, focusable = False)
		self.preWindow = None
		
		self.context = self.newArea(0, 'context', 10, 40, 30, 10, border = True, focusable = False)
		
		for i in range(0, self.background.height):
			self.background.goto(0, i)
			self.background.drawLine('.')
		
		startX = (self.width - len(self.title)) / 2
		startY = self.height + len(self.title)/self.width/2
		startX = 0 if startX < 0 else True
		startY = 0 if startY < 0 else True
		self.context.goto(startX, startY)
		self.context.putLine(self.title)
	
		self.yesBtn = button("YES", "确定", 1, 10)
		self.addArea(self.yesBtn, 55 , 18)
		self.yesBtn.onClick = lambda:self.doYes()
		
	def doYes(self):
		self.cancel()
	
	def cancel(self):
		self.blurable = True
		if self.preWindow:
			self.screen.curWindow = self.preWindow
		self.screen.closeWindow(self)
		self.screen.alertWindow = None
		
	def blur(self):
		return self.blurable
		
class confirm(alert):
	def __init__(self, screen, title, height, width):
		alert.__init__(self, screen, title, height, width)
		
		self.noBtn = button("NO", "取消", 1, 10)
		self.addArea(self.noBtn, 35, 18)
		self.noBtn.onClick = lambda:self.doNo()
	
	def doNo(self):
		self.cancel()
		
class prompt(confirm):
	def __init__(self, screen, title, height, width):
		confirm.__init__(self, screen, title, height, width)
		self.input = input(1, "content", 1, 30)
		self.addArea(self.input, 35, 14)
		self.yesBtn.onClick = lambda:self.doYes(self.input.getText())
		
	def doYes(self, text):
		confirm.doYes(self)
		pass

		
#Input Box
class editor(area):
	def __init__(self, id, title, height = 0, width = 0, maxLen = -1):
		area.__init__(self, id, title,  height, width, True, True)
		self.maxLen = maxLen
		self.text = []	#multiple lines
		self.addHandler(handler.CTRLENTER, lambda a,b:self.keyEnter(self.getText()))	# Enter
		
	def getText(self):
		text = ''
		for line in self.text:
			text = text + line + '\n'
		return text.rstrip()
	
	def clear(self):
		self.text = []
	
	def putLine(self, line):
		if self.maxLen > 0 and len(self.getText()) >= self.maxLen:
			return 
		if len(self.text) == 0:
			self.text.append('')
		self.text[len(self.text) - 1] += line
	
	def putStr(self, s):
		lines = s.split('\n')
		for line in lines:
			self.putLine(line)
			self.text.append('')	#new Line
			
	def deleteCh(self):
		if len(self.text) == 0:		#empty
			return False
		if len(self.text[len(self.text) - 1]) == 0:
			self.text.pop()
			return self.deleteCh()
		line = self.text[len(self.text) - 1]
		if 127 < ord(line[len(line) - 1]) and 1 < len(self.text[len(self.text) - 1]):
			self.text[len(self.text) - 1] = self.text[len(self.text) - 1][:-2]	#delete a unicode char
		else:
			self.text[len(self.text) - 1] = self.text[len(self.text) - 1][:-1]	#delete a char
		return True
		
	def keyEnter(self, text):
		pass
		
	def handle(self, key):
		if self.keyHandler.has_key(key):
			self.keyHandler[key](self, key)
			return True
		else:
			return self.putch(self, key)
			
	def putch(self, area, key):
		if len(key) == 1:
			if key == handler.BACKSPACE:				# Backspace -> 
				area.deleteCh()
			elif key == handler.TAB:				# tab -> 4 spaces
				area.putLine("    ")
			elif key == handler.ENTER:			# Ctrl + Enter -> new Line  
				area.putStr('')	
			elif self.canDisplay(key):
				area.putLine(key)
			else:
				return False
		else:						
			area.putLine(key)			#Unicode, HOW 2 Deal		
	
	#from text to display content
	def toContent(self):
		area.clear(self)
		area.goto(self, 0,0)
		for line in self.text:
			area.putLine(self, line)
			area.putStr(self, '')		#new line
	
	#from display content to text 	
	# deprecate
	def toText(self):
		text = ""
		insertNL = False
		for line in self.content:
			if insertNL:
				text = text + ''.join('\n') 
				insertNL = False
			text = text + ''.join(line[:line[self.width]])
			if self.width > line[self.width]:
				insertNL = True
		self.clear()
		self.putStr(text.rstrip())
		
	def canDisplay(self, key):
		if len(key) > 1:
			return True
		code = ord(key)
		return True if code >= ord(handler.DISPLAYSTART) and code <= ord(handler.DISPLAYEND) else False
	
	def refresh(self):
		self.toContent()
		area.refresh(self)
		
	pass

class input(editor):
	def __init__(self, id, title, height = 0, width = 0, maxLen = -1):
		editor.__init__(self, id, title, height, width, maxLen)
		self.maxLen = width if width < maxLen or maxLen == -1 else maxLen
		
#Password Input Box
class password(input):
	def __init__(self, id, title, height = 0, width = 0, maxLen = -1):
		editor.__init__(self, id, title, height, width, maxLen)
		
	#from text to display content
	def toContent(self):
		area.clear(self)
		area.goto(self, 0,0)
		for line in self.text:
			area.putLine(self, '*' * len(line))
			area.putStr(self, '')		#new line
			
	# Cannot to text
	def toText(self):
		pass

#list area
class listArea(area):
	def __init__(self, id, title, height = 0, width = 0):
		area.__init__(self, id, title,  height, width, True, True)
		self.listData = {}
		self.curItem = None
		
		self.addHandler(handler.ENTER, lambda a,b:self.keyEnter(self.curItem))	# Enter

	def drawList(self):
		# Fixed 
		self.clear()
		#self.goto(0,0)
		for id, data in self.listData.items():
			if data == self.curItem:
				self.putStr("\n->" + data.shortInfo())
			else:
				self.putStr("\n  " + data.shortInfo())
	
	def setCursor(self, id):
		if self.listData.has_key(id):
			self.curItem = self.listData[id]
		
	def keyUp(self):
		index = self.listData.values().index(self.curItem)
		i = (index - 1) % len(self.listData)
		self.curItem = self.listData.values()[i]
	def keyDown(self):
		index = self.listData.values().index(self.curItem)
		i = (index + 1) % len(self.listData)
		self.curItem = self.listData.values()[i]
	def keyPageUp(self):
		pass
	def keyPageDown(self):
		pass
	#need override
	def keyEnter(self, item):
		pass
		
	def refresh(self):
		self.drawList()
		area.refresh(self)

class button(area):
	def __init__(self, id, title, height = 0, width = 0):
		area.__init__(self, id, title,  height, width, border = False, focusable = True)
		
		self.addHandler(handler.ENTER, lambda a,b:self.onClick())
		
		startX = (self.width - len(self.title)) / 2
		startY = self.height + len(self.title)/self.width/2 - 1
		startX = 0 if startX < 0 else startX
		startY = 0 if startY < 0 else startY
		self.goto(startX, startY)
		self.putLine(self.title)
		
	def focus(self):
		self.border = True
		area.focus(self)
		return True
	
	def blur(self):
		self.border = False
	
	#need override
	def onClick(self):
		pass

#Key Code
class handler:
	CTRLTAB = '\x00'
	CTRLA = '\x01'
	BACKSPACE = '\x08'
	TAB = '\x09'
	CTRLENTER = '\x0A'
	CTRLL = '\x0C'
	ENTER = '\x0D'
	CTRLN = '\x0E'
	CTRLQ = '\x11'
	EOF = '\x1A'
	ESC = '\x1B'
	DISPLAYSTART = '\x20'
	DISPLAYEND = '\xFE'
	HOME = '\xE0\x47'
	UP = '\xE0\x48'
	DOWN = '\xE0\x50'
	LEFT = '\xE0\x4B'
	RIGHT = '\xE0\x4D'
	PAGEUP = '\xE0\x49'
	PAGEDOWN = '\xE0\x51'
	
	
if __name__ == '__main__':
	scr = screen(30, 100)
	win1 = scr.newWindow("3", "张三", 27, 100)
	win2 = scr.newWindow("6", "李四王", 27, 100)
	win3 = window("10", "李四王五", 27, 100)
	scr.addWindow(win3)
	talk1 = win1.newArea(1, 'talk1', 17, 70, 2, 1, border= True)
	input1 = win1.newArea(2, 'input', 6, 70, 2, 20)
	input2 = win1.newArea(3, 'input', 10, 25, 74, 1)
	input3 = win1.newArea(4, 'input', 13, 25, 74, 13)
	btn1 = button(1, "btn1", 1, 10)
	win3.addArea(btn1, 10, 10)
	scr.chWindow(win3)
	scr.refresh()