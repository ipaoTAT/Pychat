#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
import lib.db_util as db_util

class user:
	def __init__(self, name, screen_name, session = None):
		self.name = name
		self.screen_name = screen_name
		self.session = session
		pass
		
	def to_dict(self):
		res = {}
		res['id'] = self.name
		res['name'] = self.screen_name
		return res

def register(name, password):
	if name and password:
		if db_util.get_db().insert('user',{'name':name, 'screen_name':name, 'password':password}):
			return True
		return None
	return None
		
def get_user_by_name(name):
	results = db_util.get_db().query('user', {'name':name})
	if len(results) != 1:
		return None
	_user_info = results[0]
	return user(_user_info['name'], _user_info['screen_name'])
		
def login_check(name, password):
	print type(password)
	results = db_util.get_db().query("user",{'name':name, 'password':password})
	return False if len(results) == 0 else True
	
if __name__ == "__main__":
	print login_check(10003, "misstina")