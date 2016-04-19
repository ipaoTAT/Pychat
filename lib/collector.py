#!/usr/bin/python
# -*- coding: utf-8 -*-
import Queue
import threading

import logging 
import logging.config
logging.config.fileConfig("../conf/log.conf")
logger = logging.getLogger('collector')
logger.setLevel(logging.INFO)

class collector:
	def __init__(self, handler = None, seperater = '\n'):
		self.seperater = seperater
		self.bufferLock = threading.Lock()
		self.buffer = ""
		if handler:
			self.handler = handler
		
	def collect(self, data):
		self.bufferLock.acquire()
		_buffer = self.buffer + data
		self.buffer = _buffer.split(self.seperater)[-1]
		self.bufferLock.release()
		segments = _buffer.split(self.seperater)[:-1]
		for seg in segments:
			if self.handler:
				self.handler(seg)
	
	def handler(self, data):
		logger.info("Default handler: " + data)
		
class test:
	def __init__(self, addition = ""):
		self.addition = addition
		self.collector = collector(handler = self.handler, seperater = ' ')
		pass
	
	def add(self, data):
		self.collector.collect(data)
	
	def handler(self, data):
		logger.info("Handler: " + data + self.addition)

if __name__ == '__main__':
	t = test('+')
	t.add("a bc dddd s")
	t.add("bb")
	t.add("d ")