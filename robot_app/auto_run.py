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
from influxdb import InfluxDBClient

cur_dir = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
class Robot:

	def __init__(self, target, config):
		self.config = config
		log_file = config["log_file"]
		level = config["level"]
		self.target_url  = target
		self.logger = DCLogger(log_file, level)
		DCLogger.set_default_logger(self.logger)

	def init_db(self):
                influxdb_host = self.config["db"]["influxdb_host"]
                influxdb_port = self.config["db"]["influxdb_port"]
                influxdb_user = self.config["db"]["influxdb_user"]
                influxdb_password = self.config["db"]["influxdb_password"]
                influxdb_database = self.config["db"]["database"]
                self.state_db = InfluxDBClient(influxdb_host, influxdb_port, influxdb_user, influxdb_password, influxdb_database)

	def auto_run(self):
		run_uuid = str(uuid.uuid1())
		start_time = time.time()
		app_name = "robot-app-" + run_uuid
		host = app_name
		self.dClient = HttpClient(self.target_url)
		self.init_db()
		try:
			print("check target")
			self.check_target(run_uuid)
			print("check push")
			self.check_push(run_uuid, app_name)
			print("check create host")
			self.check_create_host(run_uuid, host)
			print("check map app")
			self.check_map_app(run_uuid,app_name,host)
			#self.check_visit_app(run_uuid,host)



		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
		finally:
			try:
				print("check unmap app")
				self.check_unmap_app(run_uuid,app_name,host)
			except Exception, e:
				trace = traceback.format_exc()
				print(trace)
				self.logger.error(trace)
			try:
				print("check delete host")
				self.check_delete_host(run_uuid, host)
			except Exception, e:
				trace = traceback.format_exc()
				print(trace)
				self.logger.error(trace)				
			try:
				print("check delete app")
				self.check_delete_app(run_uuid, app_name)
			except Exception, e:
				trace = traceback.format_exc()
				print(trace)
				self.logger.error(trace)				

	def __store_status(self, run_id, start_time, end_time, action, status, description=""):
		json_body = [{
			"points": [
            		[run_id, start_time, end_time, action, status,description]
        		],
			"name": "check_data",
			"columns": ["run_id", "start_time", "end_time","action","status","description"]
    			}]
		self.state_db.write_points(json_body)
		

	def __get_action_status(self, result):
		content = result[1]
		print(str(content))
		status = json.loads(content)["status"]
		return status

	def __check_app_status(self, app_name):
		result = self.dClient.get_request("/apps/" + app_name, {"Content-Type": "application/json"})
		if result is not None:
			content = result[1]
			app_info = json.loads(content)["content"]
			instances = app_info["instances"]
			running = app_info["running"]
			self.logger.info("app " + app_name + ":" + str(running) + "/" + str(running) )
			if instances == running:
				return True
			else:
				return False
		else:
			return False

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
			print(result)
			if result is not None:
				status = self.__get_action_status(result)
				if status:
					self.logger.info("succeed to push app" + app_name)
					app_running_status = self.__check_app_status(app_name)
					count = 0
					while not app_running_status:
						time.sleep(5)
						app_running_status = self.__check_app_status(app_name)
						count+=1
						if count > 4:
							break
					if app_running_status:
						self.logger.info("all app instances are running")
						end_time = time.time()
						self.__store_status(run_uuid,start_time,end_time,"push",0)
					else:
						self.logger.error("not all the instances are running")
						end_time = time.time()
						self.__store_status(run_uuid,start_time,end_time,"push",1,"not all the instances are running")
				else:
					self.logger.error("failed to push app" + app_name)
					end_time = time.time()
					self.__store_status(run_uuid,start_time,end_time,"push",1,"failed to push app" + app_name)
			else:
				self.logger.error("push request send failed")
				end_time = time.time()
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
	while True:
		robot_app.auto_run()
		time.sleep(600)


