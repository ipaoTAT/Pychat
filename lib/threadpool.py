#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import Queue
import time

import logging 
import logging.config
logging.config.fileConfig("../conf/log.conf")
logger = logging.getLogger('threadpool')
logger.setLevel(logging.INFO)

class threadpool:
	def __init__(self, handle, size = 1):	
		self.cond = threading.Condition(threading.Lock())
		self.taskQueue = Queue.Queue(maxsize = -1)
		self.workers = []
		for i in range (0, size):
			_worker = worker(self, handle)
			self.workers.append(_worker)
	
	def start(self):
		for _worker in self.workers:
			_worker.start()
	
	def stop(self):
		for _worker in self.workers:
			_worker.stop()
		time.sleep(0.5)
		for _worker in self.workers:
			_worker.handle = lambda a:1 == 1	# Dont do anything
			self.cond.acquire()
			self.taskQueue.put("End")
			self.cond.notify()					
			self.cond.release()
	
	def addTask(self, object):
		self.cond.acquire()
		self.taskQueue.put(object)
		self.cond.notify()						# Notify a worker to work
		self.cond.release()
		
	def clearTask(self):
		self.cond.acquire()
		self.taskQueue.clear()
		self.cond.release()
		
	pass

class worker(threading.Thread):
	def __init__(self, pool, handle):
		threading.Thread.__init__(self)
		if handle:
			self.handle = handle
		self.pool = pool
		self._stop = True
		
	def run(self):
		self._stop = False
		while not self._stop:
			self.pool.cond.acquire()
			self.pool.cond.wait()
			_task = self.pool.taskQueue.get_nowait()
			self.pool.cond.release()
			self.handle(_task)
			#time.sleep(1)
		self.doStop()
	
	def stop(self):
		self._stop = True
			
	def handle(self, item):
		logger.info("calling function 'handle' - " + item)
		pass
	
	def doStop(self):
		self.pool.workers.remove(self)
		logger.info(str(self) + "stoped.")
		
	pass
	
if __name__ == '__main__':
	tp = threadpool(None, 2)
	tp.start()
	logger.info("Test")
	time.sleep(3)
	tp.addTask("task1")
	tp.stop()