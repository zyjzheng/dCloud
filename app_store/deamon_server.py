import os
import json
import time
import inspect
import traceback
from httpclient import HttpClient
from influxdb import InfluxDBClient
from influxdb import InfluxDBClientError

cur_dir = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])

class DeamonServer:
	def __init__(self, config_path = None):
		try:
			if config_path == None or not os.path.exists(config_path):
				default_config_file = cur_dir + "/config/config.json"
				if os.path.exists(default_config_file):
					config_fd = open(default_config_file)
					self.config = json.load(config_fd)
				else:
					return None
			else:
				config_fd = open(config_path)
				self.config = json.load(config_fd)
			#self.init_database()
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			return None

#	def init_database(self):
#		client = self.__get_influxdb_client()
#		dbname = self.config["database"]
#		try:
#			client.create_database(dbname)
#		except InfluxDBClientError, e:
#			print(e.code)
#			print(e.message)
#		client.switch_db(dbname)

	def start(self):
		tasks = self.get_marathon_tasks()
		done_task = []
		running_task = []
		for task in tasks:
			host = task["host"]
			try:
				done_task.index(host)
			except Exception, e:
				print(host)
				running_task.extend(self.__get_mesos_slave_container(host))
				done_task.append(host)
		self.__store_app_container(running_task)


	def get_marathon_tasks(self):
		marathon_api = self.config["marathon_api"]
		api_version = self.config["marathon_api_version"]
		marathon_client = HttpClient(marathon_api)
		result = marathon_client.get_request("/" + api_version +"/tasks",{})
		if result is not None:
			status = result[0]
			content = result[1]
			try:
				tasks = json.loads(content)["tasks"]
			except Exception, e:
				raise Exception("can not format response content")
			return tasks
		else:
			raise Exception("can not get marathon running task")

	def __store_app_container(self, running_task):
		client = self.__get_influxdb_client()
		table_name = self.config["table_name"]
		client.query("delete from %s" %(table_name))
		items = [{
		"points": [],
		"name": table_name,
		"columns": ["app_name", "container"]
		}]
		for task in running_task:
			task_id = task["id"]
			container = "/docker/" + task["container"]
			app_name = task_id
			split_index = task_id.rfind('.',0)
			if split_index >= 0:
				app_name = task_id[0:split_index]
			point = []
			point.append(app_name)
			point.append(container)
			items[0]["points"].append(point)
		client.write_points(items)

	def __get_running_task(self,framework):
		running_tasks = []
		executors = framework["executors"]
		for task in executors:
			running_task = {}
			running_task["id"] = task["id"]
			running_task["container"] = task["container"]
			running_tasks.append(running_task)
		return running_tasks

	def __get_mesos_slave_container(self, host):
		port = self.config["slave_port"]
		state_url = "/state.json"
		client = HttpClient(host,port)
		result = client.get_request(state_url,{})
		if result is not None:
			status = result[0]
			content = result[1]
			if status == 200:
				slave_status = json.loads(content)
				framework = slave_status["frameworks"][0]
				running_task = self.__get_running_task(framework)
				return running_task
			else:
				raise Exception("http response error, code is %d" %(status))
		else:
			raise Exception("can not get containers of %s" %(host))

	def __get_influxdb_client(self):
		influxdb_host = self.config["influxdb_host"]
		influxdb_port = self.config["influxdb_port"]
		influxdb_user = self.config["influxdb_user"]
		influxdb_password = self.config["influxdb_password"]
		influxdb_database = self.config["database"]
		influxdb_client = InfluxDBClient(influxdb_host, influxdb_port, influxdb_user, influxdb_password, influxdb_database)
		return influxdb_client
		


if __name__ == "__main__":
	try:
		ds = DeamonServer()
		while(True):
			ds.start()
			time.sleep(100)

	except Exception, e:
		trace = traceback.format_exc()
		print(trace)
