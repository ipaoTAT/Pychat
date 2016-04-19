#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

import sys
sys.path.append("..")
import lib.rpc as rpc

class chatClient(rpc.client):
	def __init__(self, target_port, target_host = 'localhost'):
		rpc.client.__init__(self, target_port = target_port, target_host = target_host)
	
	def start(self):
		rpc.client.start(self)
	
	# Login Handler
	def login(self, name, password):
		self.request("login", {"name":name, "password":password}, self.login_res)
	def login_res(self, result, message):
		self.bool_res(result, message)
		pass
	
	# Logout Handler
	def logout(self):
		self.request("logout", {}, self.logout_res)
	def logout_res(self, result, message):
		self.bool_res(result, message)
		pass

	# Register Handler
	def register(self, name, password, re_password):
		self.request("register", {"name":name, "password":password, "re_password": re_password}, self.register_res)
	def register_res(self, result, message):
		self.bool_res(result, message)
		pass
	
	# List Users Handler
	def list_user(self, id):
		self.request("listUser", {"id":id}, self.list_user_res)
		pass
	def list_user_res(self, result, message):
		self.bool_res(result, message)
		pass
	
	# List Rooms Handler
	def list_room(self):
		self.request("listRoom", {}, self.list_room_res)
		pass
	def list_room_res(self, result, message):
		self.bool_res(result, message)
		pass
	
	# Create Room Handler
	def create_room(self, name):
		self.request("createRoom", {"name":name}, self.create_room_res)
		pass
	def create_room_res(self, result, message):
		self.bool_res(result, message)
		pass
	
	# Enter Room Handler
	def enter_room(self, id):
		self.request("enterRoom", {"id":id}, self.enter_room_res)
		pass
	def enter_room_res(self, result, message):
		self.bool_res(result, message)
		pass
		
	# Leave Room Handler
	def leave_room(self, id):
		self.request("leaveRoom", {"id":id}, self.leave_room_res)
		pass
	def leave_room_res(self, result, message):
		self.bool_res(result, message)
		pass
	
	#Send Message Handler
	def send_msg(self, target, content):
		self.request("sendMessage", {"target":target, "content":content}, self.send_msg_res)
		pass
	def send_msg_res(self, result, message):
		self.bool_res(result, message)
		pass
		
		
	def user_info(self, name):
		self.request("userInfo", {"name":name}, self.bool_res)

		
	def send_msg_to_user(self, name, msg):
		self.request("sendMessage", {"type":"personal", "to":name, "message":msg}, self.bool_res)
	
	def bool_res(self, result, message):
		print "Result:",result
		print "Message:", message
		
	def stop(self):
		rpc.client.stop(self)

		
if __name__ == "__main__":
	
	
	import sys
	import time
		
	argv = sys.argv[0]

	if argv == "client":
		cli = chatClient(target_port = 6666)
		cli.start()
		time.sleep(1)
		#cli.register("Li Lei", "missing", "missing")
		cli.login("Li Lei", "missing")
		#time.sleep(1)
		#cli.logout()
		#cli.user_info("new")
		#cli.enter_room(1)
		#cli.list_room()
		#cli.send_msg_to_user("Li Lei", "Hello Li Lei!")
	#elif argv == "client2":
	cli = chatClient(target_port = 6666)
	cli.start()
	time.sleep(1)
	#cli.register("Li Lei", "missing", "missing")
	cli.login("new", "missing")
	time.sleep(1)
	cli.create_room("Testttt")
	#cli.logout()
	#cli.user_info("new")
	#cli.enter_room(1)
	#cli.list_room()
	#cli.send_msg_to_user("Li Lei", "Hello Li Lei!")
		