#!/usr/bin/python
# -*- coding: utf-8 -*-
#RPC Handler based json
import json
import collector
import socket
import select
import Queue
import threading

import logging 
import logging.config
logging.config.fileConfig("../conf/log.conf")
logger = logging.getLogger('rpc')
logger.setLevel(logging.INFO)

# RPC Server based on single thread
class server:
	def __init__(self, port):
		self.port = port
		self.sessions = {}
		self.inputs = []
		self.outputs = []
		self.exceptions = []
		self.timeout = 1
		self._stop = False
		self.collector = collector.collector(handler = None, seperater = '\n')
		self.notifications = {}
		self.server_notify = notification(0)
		
		self.methods = {}			#Key is same to method name 
		self.methods['getMethods'] = self.getMethods
		self.methods['addNotification'] = self.addNotification
		self.methods['addNotify'] = self.addNotify
		self.methods['subscribe'] = self.subscribe
		self.methods['unSubscribe'] = self.unSubscribe
	
	# Main loop
	def start(self):
		#Initial socket
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.socket.setblocking(False)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind(('', self.port))
		self.socket.listen(5)
		self.inputs.append(self.socket)
		
		while not self._stop:
			read_set , write_set , exception_set = select.select(self.inputs, self.outputs, self.exceptions, self.timeout)

			for fd in read_set:
				if fd == self.socket:
					self.handle_accept(fd)
				else:
					self.handle_read(fd)
				pass

			for fd in write_set:
				self.handle_write(fd)
				pass

			for fd in exception_set:
				self.handle_except(fd)
				pass
		
		self.on_stop()
	
#######################################
	# Default handler
	def handle_accept(self, fd):
		socket, addr = fd.accept()
		logger.info("Client Connecting...")
		self.add_session(socket)
		socket.setblocking(False)
		self.inputs.append(socket)
		self.outputs.append(socket)
		self.exceptions.append(socket)
		pass
		
	def handle_read(self, fd):
		try:
			data = fd.recv(1024)
			if len(data) == 0:	   			#Socket has closed
				self.handle_close(fd)
			else:
				# Single Thread
				logger.info("Recv data :" + data)
				self.handle_data(fd, data)
		except socket.error, e:
			self.handle_close(fd)
		
	def handle_write(self, fd):
		next_msg = None
		try:
			next_msg = self.sessions[fd].get_next_output()
		except Exception, e:
			#logger.info(e.message)
			pass
		if next_msg:
			fd.send(next_msg)
					
	def handle_except(self, fd):
		#self.notify("Exception Occured in Server", self.sessions[fd])
		pass
	
	def handle_data(self, fd, data):
		if data and len(data) > 0:
			self.collector.handler = lambda msg:self.handle_msg(msg, self.sessions[fd])
			self.collector.collect(data)
		pass
		
	def handle_close(self, fd):
		self.inputs.remove(fd)
		self.outputs.remove(fd)
		self.exceptions.remove(fd)
		self.sessions.pop(fd)
		# delete from notification
		for notification in self.notifications.values():
			notification.delSubscriber(session)
		if fd:
			fd.close()
		
		logger.info("Client Closed!")
		

#######################################		
	# Process Message
	# Format:{"type":"rpc", "methodName":"XXX", "parameters":"$parms"}
	def handle_msg(self, msg, session):
		try:
			if type(msg) == str:
				msg = json._default_decoder.decode(msg)
				if type(msg) != dict:
					raise Exception("Message is not a dict")
			if not msg.has_key("type") or msg["type"] != "rpc":
				raise Exception("Message is not a RPC Request")
			# Now msg is a Valide dict type
			if not msg.has_key("id"):
				raise Exception("RPC Message has no 'id' field")
			if not msg.has_key("methodName"):
				raise Exception("RPC Message has no 'methodName' field")
			id = msg["id"]
			methodName = msg["methodName"]
			logger.info("Remote calling method '" + methodName + "'")
			if not self.methods.has_key(methodName):
				self.reply(id, False, "Unsupport Method", session)
				return
			parameters = msg["parameters"] if msg.has_key("parameters") else {}
			result, message = self.methods[methodName](parameters, session)
			print result, message
			self.reply(id, result, message, session)
		except Exception, e:
			logger.info("RPC Error: " + e.message)
			#raise e
	
	# RPC Reply Sender
	# Format:{"type":"reply", "result":"True/False", "message":"$message"}
	def reply(self, id, result, msg, session):
		if not id:
			raise Exception("Reply has no id") 
		_reply = {}
		_reply["type"] = "reply"
		_reply["id"] = id
		_reply['result'] = result
		_reply['message'] = msg
		self.send(json._default_encoder.encode(_reply), session)
		
	def notify(self, not_id, msg):
		if self.notifications.has_key(not_id):
			self.notifications[not_id].notify(msg)
	
	# Message Sender
	def send(self, data, session):
		logger.info("Send data '" + data + "'")
		session.add_output(data + "\n")
	
#######################################
	def add_session(self, socket):
		_session = session(socket)
		self.sessions[socket] = _session

	def add_notification(self, notification):
		if notification:
			self.notifications[notification.id] = notification
	def del_notification(self, notification):
		if notification:
			self.notifications.pop(notification.id)
			del notification
			
	# Process Method
	def add_method(self, method_name, handler):
		if method_name:
			self.methods[method_name] = handler

########################################
	# Remote Method
	def getMethods(self, *NoUse):
		names = []
		for name in self.methods.keys():
			names.append(name)
		return True, names

	# About Notification
	def addNotification(self, params, session):
		not_id = generate_id(self.notifications)
		if not_id:
			_notification = notification(not_id)
			self.add_notification(_notification)
			return True,{"id": not_id}
		return False,{"message": "Failed to allocate id"}
		
	# Parameters: {"id":"$notification-id"}
	def subscribe(self, params, session):
		if params.has_key("id"):
			not_id = params["id"]
			if self.notifications.has_key(not_id):
				self.notifications[not_id].addSubscriber(session)
				return True,{"id": not_id}
		return False,{}
		
	def unSubscribe(self, params, session):
		if params.has_key("id"):
			not_id = params["id"]
			if self.notifications.has_key(not_id):
				self.notifications[not_id].delSubscriber(session)
				return True,{"id": not_id}
		return False, {"id": not_id}

	def addNotify(self, params, session):
		if params.has_key("id") and params.has_key("message"):
			not_id = params["id"]
			message = params["message"]
			if self.notifications.has_key(not_id):
				self.notifications[not_id].notify(message)
				return True,{}
		return False, {}
#######################################
	def stop(self):
		self._stop = True
	
	def on_stop(self):
		self.socket.close()

# Client in Server's eye is Session
class session:
	def __init__(self, socket):
		self.socket = socket
		self.input_buffer = Queue.Queue(-1)
		self.output_buffer = Queue.Queue(-1)
	
	#May except
	def get_next_input(self):
		return self.input_buffer.get_nowait()
	def get_next_output(self):
		return self.output_buffer.get_nowait()
	def add_input(self, msg):
		self.input_buffer.put_nowait(msg)
	def add_output(self, msg):
		self.output_buffer.put_nowait(msg)
	pass

# Notifications are sent by Server
class notification:
	def __init__(self, id):
		self.id = id
		self.subscribers = []		# Session Set
	
	def addSubscriber(self, session):
		if session:
			self.subscribers.append(session)
	
	def delSubscriber(self, session):
		try:
			self.subscribers.remove(session)
		except Exception, e:
			logger.info(e.message)
			pass
	
	# Notification Sender
	# Format:{"type":"notify", "message":"$message"}
	def notify(self, msg): 
		_notify = {}
		_notify["type"] = "notify"
		_notify["id"] = self.id
		_notify["message"] = msg
		for session in self.subscribers:
			if session:
				self.send(json._default_encoder.encode(_notify), session)
			else:
				self.subscribers.remove(session)
	
	# Message Sender
	def send(self, data, session):
		logger.info("Send data '" + data + "'")
		session.add_output(data + "\n")
	
# RPC Client based on thread
class client(threading.Thread):
	def __init__(self, target_port, target_host = '127.0.0.1'):
		threading.Thread.__init__(self)
		self.server_addr = (target_host, target_port)
		self.rpc_wait = {}		#Key:RPC ID, value: handler
		self.notify_wait = {}	#Key:Notify ID, value:handler
		self.socket = None
		self.collector = collector.collector(handler = self.handle_msg, seperater = '\n')
		self._stop = False
	
	#Main Loop
	def run(self):
		#Initial socket
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect(self.server_addr)
		while not self._stop:
			try:
				data = self.socket.recv(1024)
				if len(data) == 0:	   			#Socket has closed
					handle_close()
				else:
					# Single Thread
					# logger.info("Recv data :" + data)
					self.collector.handler = lambda msg : self.handle_msg(msg)
					self.collector.collect(data)
			except socket.error, e:
				break
				
		self.handle_close()

###########################################
	# Message Handler
	# May raise exception
	def handle_msg(self, msg):
		#try:
		if type(msg) == str:
			msg = json._default_decoder.decode(msg)
			if type(msg) != dict:
				raise Exception("Message is not a dict")
		if not msg.has_key("type"):
			raise Exception("Message has no 'type' field")
		# Now msg is a Valide dict type
		msg_type = msg["type"]
		if msg_type == "reply" and msg.has_key("id"):
			result = msg["result"] if msg.has_key("result") else None
			message = msg["message"] if msg.has_key("message") else None
			self.handle_reply(msg["id"], result, message)
		elif msg_type == "notify" and msg.has_key("id"):
			message = msg["message"] if msg.has_key("message") else None
			self.handle_notify(msg["id"], message)
		else:
			raise Exception("Message error")
		#except Exception, e:
		#	logger.info(e.message)
	
	# Handle RPC reply
	def handle_reply(self, rpc_id, result, message):
		if not self.rpc_wait.has_key(rpc_id):
			pass
		else:
			handler = self.rpc_wait.pop(rpc_id)
			if handler:
				handler(result, message)
	
	# Handle Notifications
	def handle_notify(self, notify_id, message):
		if not self.notify_wait.has_key(notify_id):
			pass
		else:
			handler = self.notify_wait[notify_id]
			if handler:
				handler(message)
	
	# Handle Close
	def handle_close(self):
		try:
			self.socket.close()
			logger.info("Server Closed!")
		except Exception, e:
			pass
		self.stop()

###############################################################
	# RPC Request Sender
	def request(self, method, parameters, handler):
		_rpc = {}
		id = generate_id(self.rpc_wait)
		if not id:
			raise Exception("ID alloc failed")
		_rpc["type"] = "rpc"
		_rpc["id"] = id
		_rpc["methodName"] = method
		_rpc["parameters"] = parameters
		self.rpc_wait[id] = handler
		if not self.send(json._default_encoder.encode(_rpc)):
			pass
	# Message Sender
	def send(self, data):
		try:
			# logger.info("Send data '" + data + "'")
			self.socket.send(data + "\n")
			return True
		except Exception, e:
			logger.error(e.message)
			return False
		
###########################################
# Sample Test 
	def addNotification(self):
		self.request("addNotification", {}, lambda res, msg: self.subscribe(msg["id"]))
	
	def subscribe(self, not_id):
		self.notify_wait[1] = lambda msg: logger.error("> " + msg)
		self.request("subscribe", {"id": 1}, None)
		
	def addNotify(self, not_id, msg):
		self.request("addNotify", {"id": 1, "message": msg}, None)
		
	def show_message(self, result, message):
		print "result:" + str(result) + ",message:" + str(message)
###########################################
		
	def stop(self):
		self._stop = True
		if self.socket:
			self.socket.close()

def generate_id(set):
	id = None
	for i in range(1, 65536):
		if not set.has_key(i):
			id = i
			break
	return id

####################################
# Test	
if __name__ == "__main__":
	import sys
	import time
	
	def show_message(result, message):
		print "result:" + str(result) + ",message:" + str(message)
		
	def rpc_h(msg, *NoUse):
		i = msg["i"]
		i = int(i) + 1
		return True, i
		
	argv = sys.argv[1]
	if argv == "server":
		serv = server(port = 6666)
		#serv.add_method("addition", rpc_h)
		serv.start()
	elif argv == "client":
		cli = client(target_port = 6666)
		cli.start()
		time.sleep(1)
		#cli.request("getMethods","",show_message)
		#cli.request("addition", {"i":1}, cli.show_message)
		#time.sleep(3)
		cli.addNotification()
		time.sleep(3)
		cli.addNotify(1, "Hello RPC")
	elif argv == "client2":
		cli2 = client(target_port = 6666)
		cli2.start()
		time.sleep(1)
		#cli.request("getMethods","",show_message)
		#cli.request("addition", {"i":1}, cli.show_message)
		#time.sleep(3)
		cli2.subscribe(1)
		time.sleep(1)
		cli2.addNotify(1, "Hello Too")
		
		#cli.stop()
		