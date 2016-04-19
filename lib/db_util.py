import sqlite3

import logging 
import logging.config
logging.config.fileConfig("../conf/log.conf")
logger = logging.getLogger('DB')
logger.setLevel(logging.DEBUG)

class DB:
	def __init__(self, name, path = "./"):
		self.__db_name = path + name
		self.__conn = sqlite3.connect(self.__db_name)
		self.__cu = self.__conn.cursor()

	def execute(self, sql, data = []):
		logger.debug("Query: " + sql)
		print "Query: " + sql
		return self.__cu.execute(sql, data)
	
	def insert(self, table, data):
		if type(data) != dict:
			raise Exception("DB insert need dict type data")
		
		keys = ""; values = ""
		for key, value in data.items():
			keys += key + ","
			values += "?,"
		keys = keys[:-1]
		values = values[:-1]
		sql = "insert into " + table + "(" + keys + ") values(" + values + ")"
		try:
			res = self.execute(sql, data.values())
			self.__conn.commit()
		except sqlite3.IntegrityError, e:
			logger.info(e.message)
			return False
		return True

	def query(self, table, cond = None):
		sql = "SELECT * FROM " + table
		condstr = self.__construct_str(cond, ' and ')
		if condstr.strip() != '':
			sql += " WHERE " + condstr
		
		_cu = self.execute(sql)
		valueset = _cu.fetchall()
		keys = [ key[0] for key in _cu.description]
		data = []
		for values in valueset:
			if len(keys) != len(values):
				continue
			tmp = {}
			for i in range (0, len(keys)):
				tmp[keys[i]] = values[i]
			data.append(tmp)
		return data

	def update(self, table, data, cond):
		sql = "update " + table + " set "
		sql += self.__construct_str(data, ',')
		sql += " where "
		sql += self.__construct_str(cond, ' and ')
		try:
			self.execute(sql)
			self.__conn.commit()
		except Exception, e:
			return False
		return True

	def __construct_str(self, data, split):
		if data == None:
			return ''
		if type(data) != dict:
			raise Exception("DB: Parameters Error!")
		res = " "
		for key, value in data.items():
			res += key + "="
			res += "'" + value + "'" if type(value) in (str, unicode) else str(value)
			res += split
		# remove the last dot
		res = res[:0 - len(split)]
		return res

db = None
def get_db():
	global db
	if db == None:
		db = DB("ChatServer.db")
	return db
		
		
if __name__ == "__main__":
	#db = DB("ChatServer.db", "./")
	get_db().execute("CREATE TABLE IF NOT EXISTS user(name VARCHAR(100) PRIMARY KEY, screen_name VARCHAR(100), password VARCHAR(100))")
	#user_info = get_db().update("user", {'name':"Miss. Liu"}, {'id': 10003, 'name':'Mr. Dong'})
	#user_info = get_db().query("user",{})
	#user_info = get_db().execute("SELECT last_insert_rowid()").fetchone()[0]
	#print user_info
	
	