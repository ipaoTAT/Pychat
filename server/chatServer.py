#!/usr/bin/python
# -*- coding: utf-8 -*-
import socket
import json

import sys
sys.path.append("..")
import lib.threadpool as threadpool
import user
import lib.rpc as rpc
import time

class chatServer(rpc.server):
	def __init__(self, port):
		rpc.server.__init__(self, port)
		self.hall = hall(-1, "hall")
		# 1. Add RPC Handler
		self.add_method("login", self.login)				#["name","password"]->{True/False}
		self.add_method("logout", self.logout)				#[]->{True/False}
		self.add_method("register", self.register)			#["name","password","re-password"]->[True/False]
		self.add_method("userInfo", self.userInfo)			#[name]->[userInfo]
		self.add_method("listRoom", self.listRoom)			#[]->[roomList]
		self.add_method("createRoom", self.createRoom)		#["name"]->[id]
		self.add_method("enterRoom", self.enterRoom)		#["id"]->{True/False}
		self.add_method("leaveRoom", self.leaveRoom)		#["id"]->{True/False}
		self.add_method("listUser", self.listUser)			#["id"]->[userList]
		self.add_method("sendMessage", self.sendMessage)	#["type":{personal/public},"to":{user-id/room-id},"message"]->{True/False}
		# 2. New Thread pool
		#self.readPool = threadpool.threadpool(handle = XXX, size = 1)
		self.processPool = threadpool.threadpool(handle = self.process_job, size = 1)
		#self.writePool = threadpool.threadpool(handle = XXX, size = 1)
		# 3. 
		self.online_users = {}									# session to user mapping
	
	def start(self):
		self.processPool.start()
		rpc.server.start(self)
		
	def handle_data(self, fd, data):
		self.collector.handler = lambda msg: self.sessions[fd].add_input(msg)
		self.collector.collect(data)
		self.processPool.addTask(fd)
		
	def handle_close(self, fd):
		_session = self.sessions[fd]
		if _session and self.online_users.has_key(_session):
			#logout
			self.online_users.pop(_session)
		rpc.server.handle_close(self, fd)
			
	def process_job(self, fd):
		try:
			_session = self.sessions[fd]
			_message = _session.get_next_input()
			if _message:
				self.handle_msg(_message, _session)
		except Exception, e:
			pass
	
	def has_login(self, session):
		return self.online_users.has_key(session)
	
	def find_user(self, name):
		for _user in self.online_users.values():
			if _user.name == name:
				return _user
		return None

	def stop(self):
		self.processPool.stop()
		rpc.server.stop(self)
			
	# Methods
	def login(self, params, session):
		if params.has_key("name") and params.has_key("password"):
			name = params["name"]
			password = params["password"]
			if user.login_check(name, password):
				if self.find_user(name) == None:
					_user = user.get_user_by_name(name)
					_user.session = session
					self.online_users[session] = _user			# Add mapping
					# enter hall
					self.hall.addSubscriber(session)
					return True,{"name": _user.name, "screen_name":_user.screen_name}
				else:
					return False, {"reason":"%s has been login!" % name}
			else:
				return False,{"reason":"name or password is wrong!"}
		else:
			return False,{"reason":"name and password cannot be empty!"}
			
	def logout(self, params, session):
		if self.online_users.has_key(session):
			_user = self.online_users[session]
			self.online_users.pop(session)
			# Quit all rooms
			for notification in self.notifications.values():
				notification.delSubscriber(session)
			# Quit hall
			self.hall.delSubscriber(session)
			return True,{}
		else:
			return False,{"reason":"Have not been login!"}
			
	def register(self, params, session):
		if params.has_key("name") and params.has_key("password") and params.has_key("re_password"):
			name = params["name"]
			password = params["password"]
			re_password = params["re_password"]
			if password != re_password:
				return False, {"reason":"Different between twice Password input!"}
			if name == '' or password == '':
				return False,{"reason":"Name or Password must not be empty!"}
			if user.register(name, password):
				return True, {"name": name}
			else:
				return False,{"reason":"id '" + name + "' has been used!"}
		else:
			return False,{"reason":"name, password and re-password cannot be empty!"}
	
	def userInfo(self, params, session):
		if not self.has_login(session):
			return False, "Login before!"
		if params.has_key("name"):
			name = params["name"]
			_user = user.get_user_by_name(name)
			if _user:
				return True, _user.to_dict()
			else:
				return False, {"reason":"No such user named " + name}
		else:
			return False,{"reason":"name is needed!"}
	
	def listRoom(self, params, session):
		if not self.has_login(session):
			return False, "Login before!"
		_rooms = self.list_room()
		return True, _rooms
	def listUser(self, params, session):
		if not self.has_login(session):
			return False, "Login before!"
		if params.has_key("id"):
			room_id = params["id"]
			users = self.list_user(room_id)
			msg = {}
			msg["id"] = room_id
			msg["userlist"] = users
			return True, msg
		else:
			return False, {"reason":"room id is needed "}
	def createRoom(self, params, session):
		if not self.has_login(session):
			return False, "Login before!"
		if params.has_key("name"):
			name = params["name"]
			room_id = rpc.generate_id(self.notifications)
			if room_id:
				_room = room(room_id, name)
				self.add_notification(_room)
				#_room.addSubscriber(session)
				# send roomlist
				self.hall.send_roomlist(self.list_room())
				return True,{"id": room_id}
			return False,{"message": "Failed create room"}
		else:
			return False,{"reason":"name is needed!"}	
			
	def enterRoom(self, params, session):
		if not self.has_login(session):
			return False, "Login before!"
		if params.has_key("id"):
			res, msg = self.subscribe(params, session)
			# send userlist
			if res:
				room_id = params["id"]
				room = self.notifications[room_id]
				room.send_userlist(self.list_user(room_id))
				msg['name'] = room.name
			return res, msg
		else:
			return False, {"reason":"room id is needed "}		
			
	def leaveRoom(self, params, session):
		if not self.has_login(session): 
			return False, "Login before!"
		if params.has_key("id"):
			res, msg = self.unSubscribe(params, session)
			# send roomlist 
			if res:
				room_id = params["id"]
				room = self.notifications[room_id]
				# send userlist
				room.send_userlist(self.list_user(room_id))
				# no user
				if len(room.subscribers) == 0:
					self.del_notification(room)
					self.hall.send_roomlist(self.list_room())
			return res, msg
		else:
			return False, {"reason":"room id is needed "}

	def sendMessage(self, params, session):
		if not self.has_login(session):
			return False, "Login before!"
		src_user = self.online_users[session]
		if params.has_key("target") and params.has_key("content"):
			# Construct Message
			message = params["content"]
			_ts = time.localtime()
			_time = "%04d-%02d-%02d %02d:%02d:%02d"  % (_ts.tm_year, _ts.tm_mon, _ts.tm_mday,  _ts.tm_hour, _ts.tm_min, _ts.tm_sec)
			msg = {"speaker":src_user.screen_name, "time":_time, "content":message}
			# Find Target
			target = params["target"]
			if self.notifications.has_key(target):
				# To room
				_room = self.notifications[target]
				if _room:
					_room.send_message(msg)
					return True, {"target":target}
				else:
					return False, {"reason":"No this room [" + tatget + "]!"}
			else:
				# To user
				_user = self.find_user(target)
				if _user:
					_session = _user.session
					if _session:
						self.hall.send_personal_message(_session, msg)
						return True, {"target":target, "message":msg}
					return False,{"reason":"User " + name + " is offline!"}
				return False,{"reason":"No Such User [" + name + "]!"}
		else:
			return False,{"reason":"target and message is needed"}
			
	# tools		
	def list_room(self):
		rooms = []
		for room in self.notifications.values():
			rooms.append(room.to_dict())
		return rooms
					
	def list_user(self, room_id):
		users = []
		if self.notifications.has_key(room_id):
			_room = self.notifications[room_id]
			if _room:
				for _session in _room.subscribers:
					if self.online_users.has_key(_session):
						_user = self.online_users[_session]
						users.append(_user.to_dict())
					else:
						_room.delSubscriber(_session)
		return users
		

class room(rpc.notification):
	def __init__(self, id, name):
		rpc.notification.__init__(self, id)
		self.name = name
		pass
	
	def to_dict(self):
		return {"id":self.id, "name":self.name}
	
	def send_message(self, message):
		msg = {}
		msg["page"] = "message"
		msg["data"] = message
		msg["room"] = self.id
		self.notify(msg)
	
	def send_userlist(self, userlist):
		msg = {}
		msg["page"] = "userlist"
		msg["data"] = userlist
		msg["room"] = self.id
		self.notify(msg)
		
class hall(room):
	def __init__(self, id, name):
		room.__init__(self, id, name)
		pass
		
	def send_roomlist(self, roomlist):
		msg = {}
		msg["page"] = "roomlist"
		msg["data"] = roomlist
		self.notify(msg)
		
	def send_personal_message(self, session, message):
		msg = {}
		msg["page"] = "message"
		msg["data"] = message
		msg["room"] = self.id
		_notify = {}
		_notify["type"] = "notify"
		_notify["id"] = self.id
		_notify["message"] = msg
		for session in self.subscribers:
			if session:
				self.send(json._default_encoder.encode(_notify), session)
			else:
				self.subscribers.remove(session)
	
	
		
if __name__ == "__main__":
	serv = chatServer(port = 6666)
	serv.start()