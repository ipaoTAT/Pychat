
from chatClient import chatClient
import chatUi
import msvcrt
import time

class client(chatClient):
	def __init__(self, target_port, target_host = 'localhost'):
		chatClient.__init__(self, target_port, target_host)
		self.chat_screen = chatUi.loginScreen(30, 100)
		self.chat_screen.do_login = self.login
		self.chat_screen.do_register = self.register
		self.shutdown = True
		self.unRead = {}		#{Username:message}
		self.whoAmI = None
		
	def start(self):
		chatClient.start(self)
		self.shutdown = False
		ch = ''; chh = ''
		while not self.shutdown:
			self.chat_screen.refresh()
			ch = msvcrt.getch()
			if chh != '':
				ch = chh + ch
				self.chat_screen.handle(ch)
				chh = ''
			elif ord(ch) > 127:				# Unicode
				chh = ch
			elif ch == chr(26):				# Ctrl-Z Quit
				self.chat_screen.doAlert("Quit")
				self.chat_screen.refresh()
				break
			else:
				self.chat_screen.handle(ch)
		self.stop()
	
	def stop(self):
		self.shutdown = True
		chatClient.stop(self)
	
	def login_res(self, result, message):
		if result:
			tmp = self.chat_screen
			self.chat_screen = chatUi.chatScreen(self.chat_screen.height, self.chat_screen.width)
			del tmp
			self.chat_screen.doAlert("Welcome! " + message["screen_name"], None)
			self.whoAmI = message["name"].encode("gbk")
			self.chat_screen.hall.title = "Hall (" + self.whoAmI + ")"
			# Register Notify Handler
			self.notify_wait[-1] = self.hall_handler
			self.list_room()
			self.chat_screen.refresh()
			self.chat_screen.do_logout = self.do_logout
			self.chat_screen.do_create_room = self.do_create_room
			self.chat_screen.do_enter_room = self.do_enter_room
			self.chat_screen.do_leave_room = self.do_leave_room
			self.chat_screen.do_send_msg = self.do_send_msg
			self.chat_screen.do_open_chat = self.do_open_chat
		else:
			self.chat_screen.doAlert(message["reason"], None)
			self.chat_screen.refresh()
		pass
	def register_res(self, result, message):
		if result:
			self.chat_screen.chWindow(self.chat_screen.loginWindow)
			self.chat_screen.doAlert("[" + message["name"] + "] Register Successful, Please Login !", None)
			self.chat_screen.refresh()
		else:
			self.chat_screen.doAlert(message["reason"], None)
			self.chat_screen.refresh()
		pass
	def logout_res(self, result, message):
		if result:
			#self.chat_screen.alertWindow.cancel()
			self.whoAmI = None
			tmp = self.chat_screen
			self.chat_screen = chatUi.loginScreen(self.chat_screen.height, self.chat_screen.width)
			del tmp
			self.chat_screen.do_login = self.login
			self.chat_screen.do_register = self.register
			self.chat_screen.doAlert("Logout Success!", None)
			self.chat_screen.refresh()
		else:
			self.chat_screen.doAlert("Logout Failed!", None)
		pass
	def list_room_res(self, result, message):
		self.chat_screen.hall.flashRoomList(message)
		self.chat_screen.refresh()
		pass
	def create_room_res(self, result, message):
		if result:
			if message.has_key('id'):
				self.enter_room(message['id'])
			else:
				self.chat_screen.doAlert("Create Room Failed!", None)
		else:
			self.chat_screen.doAlert("Create Room Failed!", None)
		pass
	def enter_room_res(self, result, message):
		if result:
			room_id = message['id']
			room_name = message['name'].encode("gbk")
			# Register Notify Handler
			self.notify_wait[room_id] = self.room_handler
			_room = chatUi.room(room_id, room_name)
			self.chat_screen.newChat(_room)
			self.chat_screen.refresh()
			self.list_user(room_id)
			pass
		else:
			pass
		pass
	def leave_room_res(self, result, message):
		if result:
			room_id = message['id']
			# Register Notify Handler
			self.notify_wait.pop(room_id)
			_chat = self.chat_screen.windows[room_id]
			self.chat_screen.closeWindow(_chat)
			self.chat_screen.refresh()
			pass
		else:
			pass
		pass
	def list_user_res(self, result, message):
		if result:
			room_id = message['id']
			users = message["userlist"]
			_chat = self.chat_screen.windows[room_id]
			_chat.flashUserList(users)
			self.chat_screen.refresh()
			pass
		else:
			pass
		pass
	def send_msg_res(self, result, message):
		if result:
			chat_id = message['target']
			_chat = self.chat_screen.windows[chat_id]
			_chat.inputArea.clear()
			if message.has_key("message"):
				_data = message["message"]
				_speaker = _data['speaker'].encode("gbk")
				_time = _data['time'].encode("gbk")
				_content = _data['content'].encode("gbk")
				_chat.addMsg(_speaker, _time, _content)
			self.chat_screen.refresh()
			pass
		else:
			reason = message["reason"].encode("gbk")
			self.chat_screen.doAlert("Send Message Failed:[" + reason + "]", None)
		pass
	
	def do_logout(self):
		self.logout()
		pass
	def do_create_room(self, name):
		self.create_room(name)
		self.chat_screen.alertWindow.cancel()
	def do_enter_room(self, room):
		self.enter_room(room.id)
		pass
	def do_leave_room(self, id):
		self.leave_room(id)
		pass
	def do_send_msg(self, target, content):
		self.send_msg(target, content)
		pass
	def do_open_chat(self, object):
		object.name = object.id
		if object.name == self.whoAmI:
			return
		self.chat_screen.newChat(object)
		_msgs = []
		if self.unRead.has_key(object.id):
			_msgs = self.unRead[object.id]
			self.unRead.pop(object.id)
		if self.chat_screen.windows.has_key(object.id):
			_chat = self.chat_screen.windows[object.id]
		for _data in _msgs:
			_speaker = _data['speaker'].encode("gbk")
			_time = _data['time'].encode("gbk")
			_content = _data['content'].encode("gbk")
			_chat.addMsg(_speaker, _time, _content)
		self.chat_screen.refresh()
		pass
		
	def hall_handler(self, msg):
		page = msg["page"]
		if page == "roomlist":
			self.chat_screen.hall.flashRoomList(msg["data"])
			self.chat_screen.refresh()
			pass
		elif page == "userlist":
			pass
		elif page == "message":
			_data = msg["data"]
			_speaker = _data['speaker'].encode("gbk")
			_time = _data['time'].encode("gbk")
			_content = _data['content'].encode("gbk")
			if self.chat_screen.windows.has_key(_speaker):
				_chat = self.chat_screen.windows[_speaker]
				_chat.addMsg(_speaker, _time, _content)
			else:
				if not self.unRead.has_key(_speaker):
					self.unRead[_speaker] = []
				self.unRead[_speaker].append(_data)
				_list = []
				for id in self.unRead.keys():
					count = len(self.unRead[id])
					_list.append({"id" : id, "name": "" + id + " (" + str(count) + ")"})
				self.chat_screen.hall.flashUserList(_list)
			self.chat_screen.refresh()
			pass
		pass		
	def room_handler(self, msg):
		page = msg["page"]
		room_id = msg['room']
		_chat = self.chat_screen.windows[room_id]
		if page == "userlist":
			_chat.flashUserList(msg["data"])
			self.chat_screen.refresh()
		elif page == "message":
			_data = msg["data"]
			_speaker = _data['speaker'].encode("gbk")
			_time = _data['time'].encode("gbk")
			_content = _data['content'].encode("gbk")
			_chat.addMsg(_speaker, _time, _content)
			self.chat_screen.refresh()
			pass
		pass
			
if __name__ == "__main__":
	client = client(6666)
	client.start()
	
	
	
	