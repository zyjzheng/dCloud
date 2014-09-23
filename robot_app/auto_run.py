import os
import sqlite3
import uuid
import json
import time
import inspect
import traceback
import httplib
from httpclient import HttpClient
from logger import DCLogger

cur_dir = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
class Robot:

	def __init__(self, target, config):
		self.config = config
		log_file = config["log_file"]
		level = config["level"]
		self.db_path = config["db"]
		self.target_url  = target
		self.logger = DCLogger(log_file, level)
		DCLogger.set_default_logger(self.logger)

	def init_db(self):
		self.state_db = sqlite3.connect(self.db_path)
		self.cursor = self.state_db.cursor()
		self.cursor.execute("create table if not exists history(id varchar(255), start_time decimal, end_time decimal, primary key(id))")
		self.cursor.execute("create table if not exists action_status(id varchar(255), last decimal, action varchar(255), status integer, description text, primary key(id, action))")		
		self.state_db.commit()

	def auto_run(self):
		run_uuid = str(uuid.uuid1())
		start_time = time.time()
		app_name = "robot-app-" + run_uuid
		host = app_name
		self.dClient = HttpClient(self.target_url)
		self.init_db()
		try:
			self.check_target(run_uuid)
			self.check_push(run_uuid, app_name)
			self.check_create_host(run_uuid, host)
			self.check_map_app(run_uuid,app_name,host)
			#self.check_visit_app(run_uuid,host)
			self.check_unmap_app(run_uuid,app_name,host)
			self.check_delete_host(run_uuid, host)
			self.check_delete_app(run_uuid, app_name)
			end_time = time.time()
			self.cursor.execute("insert into history values(?,?,?)",(run_uuid,start_time,end_time))
			self.state_db.commit()
		except Exception, e:
			trace = traceback.format_exc()
			self.logger.error(trace)
		finally:
			self.cursor.close()
			self.state_db.close()

	def __store_status(self, run_id, start_time, end_time, action, status, description=""):
		self.cursor.execute("insert into action_status values(?,?,?,?,?)",(run_id, end_time - start_time, action ,status,description))
		self.state_db.commit()

	def __get_action_status(self, result):
		content = result[1]
		status = json.loads(content)["status"]
		return status

	def check_target(self,run_uuid):
		start_time = time.time()
		result = self.dClient.get_request("/info")
		end_time = time.time()
		if result is not None:
			status = result[0]
			if status == 200:
				self.logger.info("succeed to target " + self.target_url)
				self.__store_status(run_uuid,start_time,end_time,"target",0)
			else:
				self.logger.error("failed to target " + self.target_url)
				self.__store_status(run_uuid,start_time,end_time,"target",1,"failed to target " + self.target_url)
		else:
			self.logger.error("target request send failed")
			self.__store_status(run_uuid, start_time,end_time,"target", 1 ,"target request send failed")

	def check_push(self, run_uuid, app_name):
		app_file_path = cur_dir + "/config/robot_app.json"
		if os.path.exists(app_file_path):
			app_file = open(app_file_path)
			app_body = json.load(app_file)
			app_body["id"] = app_name
			start_time = time.time()
			result = self.dClient.post_request("/apps",json.dumps(app_body),{"Content-Type":"application/json"})
			end_time = time.time()
			print(result)
			if result is not None:
				status = self.__get_action_status(result)
				if status:
					self.logger.info("succeed to push app" + app_name)
					self.__store_status(run_uuid,start_time,end_time,"push",0)
				else:
					self.logger.error("failed to push app" + app_name)
					self.__store_status(run_uuid,start_time,end_time,"push",1,"failed to push app" + app_name)
			else:
				self.logger.error("push request send failed")
				self.__store_status(run_uuid,start_time,end_time,"push",1, "push request send failed")
		else:
			raise Exception("can not found app config file")

	def check_create_host(self,run_uuid, host):
		host_body = {"host": host}
		start_time = time.time()
		result = self.dClient.post_request("/router/hosts",json.dumps(host_body),{"Content-Type":"application/json"})
		end_time = time.time()
		if result is not None:
			status = self.__get_action_status(result)
			if status:
				self.logger.info("succeed to create host")
				self.__store_status(run_uuid,start_time,end_time,"create_host",0)
			else:
				self.logger.error("failed to create host " + host)
				self.__store_status(run_uuid,start_time,end_time,"create_host",1, "failed to create host " + host)				
		else:
			self.logger.error("create host request send failed")
			self.__store_status(run_uuid,start_time,end_time,"create_host",1,"create host request send failed")

	def check_map_app(self, run_uuid, app_name, host):
		start_time = time.time()
		result = self.dClient.post_request("/apps/%s/routers/%s" %(app_name,host), '', {"Content-Type":"application/json"})
		end_time = time.time()
		if result is not None:
			status = self.__get_action_status(result)
			if status:
				self.logger.info("succeed to map %s to host %s" %(app_name,host))
				self.__store_status(run_uuid,start_time,end_time,"map",0)
			else:
				self.logger.error("failed to map %s to host %s" %(app_name, host))
				self.__store_status(run_uuid,start_time,end_time,"map",1)
		else:
			self.logger.error("map request send failed")
			self.__store_status(run_uuid,start_time,end_time,"map",1,"map request send failed")

#	def check_visit_app(self, run_uuid, host):
#		domain = self.config["domain"]
#		port = self.config["vulcan_port"]
#		client = None
#		start_time = time.time()
#		print(host)
#		print(domain)
#		print(port)
#		try:
#			client = httplib.HTTPConnection(host + "." + domain, port ,timeout=10)
#			client.request('GET', '/')
#			end_time = time.time()
#			response = client.getresponse()
#			print(response.status)
#			if response.status >= 200 and response.status <= 300:
#				self.logger.info("succeed to visit the " + host + "." + domain)
#				self.__store_status(run_uuid, start_time, end_time, "visit", 0)
#			else:
#				self.logger.error("cannot visit " + host + "." + domain)
#				self.__store_status(run_uuid, start_time, end_time, "visit", 1, "cannot visit " + host + "." + domain)
#		except Exception, e:
#			traceback.print_exc()
#		finally:
#			if client:
#				client.close()

	def check_unmap_app(self, run_uuid, app_name, host):
		start_time = time.time()
		result = self.dClient.del_request("/apps/%s/routers/%s" %(app_name,host),  {"Content-Type":"application/json"})
		end_time = time.time()
		if result is not None:
			status = self.__get_action_status(result)
			if status:
				self.logger.info("succeed to unmap %s from %s" %(app_name,host))
				self.__store_status(run_uuid,start_time, end_time, "unmap", 0)
			else:
				self.logger.error("failed to unmap %s from %s" %(app_name, host))
				self.__store_status(run_uuid, start_time, end_time, "unmap", 1, "failed to unmap %s from %s" %(app_name, host))
		else:
			self.logger.error("unmap request send failed")
			self.__store_status(run_uuid,start_time,end_time,"unmap",1,"unmap request send failed")


	def check_delete_host(self, run_uuid, host):
		start_time = time.time()
		result = self.dClient.del_request("/router/hosts/%s" %(host),  {"Content-Type":"application/json"})
		end_time = time.time()
		if result is not None:
			status = self.__get_action_status(result)
			if status:
				self.logger.info("succeed to delete host")
				self.__store_status(run_uuid, start_time, end_time, "delete_host", 0)
			else:
				self.logger.error("failed to delete host " + host)
				self.__store_status(run_uuid, start_time, end_time, "delete_host", 1,"failed to delete host " + host)
		else:
			self.logger.error("delete host request send failed")
			self.__store_status(run_uuid, start_time, end_time, "delete_host", 1,"delete host request send failed")

	def check_delete_app(self, run_uuid, app_name):
		start_time = time.time()
		result = self.dClient.del_request("/apps/%s" %(app_name),  {"Content-Type":"application/json"})
		end_time = time.time()
		if result is not None:
			status = self.__get_action_status(result)
			if status:
				self.logger.info("succeed to delete app")
				self.__store_status(run_uuid, start_time, end_time, "delete_app", 0)
			else:
				self.logger.error("failed to delete app " + app_name)
				self.__store_status(run_uuid, start_time, end_time, "delete_app", 1,"failed to delete app " + app_name)
		else:
			self.logger.error("delete app request send failed")
			self.__store_status(run_uuid, start_time, end_time, "delete_app", 1,"delete app request send failed")

if __name__ == "__main__":
	config_file_path = cur_dir + "/config/config.json"
	config_file = open(config_file_path)
	config = json.load(config_file)
	robot_app = Robot("http://9.181.27.232:8888", config)
	robot_app.auto_run()


