import os
import json
import time
import inspect
import traceback
from elasticsearch import Elasticsearch
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
			self.task_containers = {}
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
			if host.strip(" ") != "":
				try:
					done_task.index(host)
				except Exception, e:
					print("----" + host)
					running_task.extend(self.__get_mesos_slave_container(host))
					done_task.append(host)
		print("start to update grafana templates")                                
		self.update_templates(running_task)
		print("finish updating")


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

	def update_templates(self, running_task):
		need_change_apps = []
		temp_containers = {}
		for task in running_task:
			task_id = task["id"]
			container = "/docker/mesos-" + task["container"]
			app_name = task_id
			split_index = task_id.rfind('.',0)
			if split_index >= 0:
				app_name = task_id[0:split_index]
			try:
				temp_containers.keys().index(app_name)
				temp_containers[app_name].append(container)
			except ValueError, e:
				temp_containers[app_name] = []
				temp_containers[app_name].append(container)
		for app_name in temp_containers.keys():
			try:
				app_added = 0
				self.task_containers.keys().index(app_name)
				new_app_containers = temp_containers[app_name]
				for container in new_app_containers:
					try:
						self.task_containers[app_name].index(container)
					except ValueError, e:
						need_change_apps.append(app_name)
						app_added = 1
						self.task_containers[app_name].append(container)
				need_removed_container = []
				for container in self.task_containers[app_name]:
					try:
						new_app_containers.index(container)
					except ValueError, e:
						if app_added == 0:
							need_change_apps.append(app_name)
						need_removed_container.append(container)
				for container in need_removed_container:
					self.task_containers[app_name].remove(container)
			except ValueError, e:
				need_change_apps.append(app_name)
				self.task_containers[app_name] = temp_containers[app_name]
			
		self.__update_templates_es(need_change_apps)

	def __update_templates_es(self, apps):
		es_host = self.config["ES_host"]
		es_port = self.config["ES_port"]
		
		es = Elasticsearch([{"host": es_host, "port": es_port}])	
		for app in apps:
			containers = self.task_containers[app]
			where_str = " and ( 1 > 2 "
			for container in containers:
				where_str = where_str + " or container_name = '" + container + "' "
			where_str = where_str + ")"
			template = self.__change_template(app, where_str)
			template_str = json.dumps(template)
			template_body = {"user":"guest","group":"guest","title":"cpuandmem","tags":[],"dashboard":template_str}		
			es.index(index="grafana-dash", doc_type="dashboard", id=app, body=template_body)
				
	def __change_template(self,app, where_str):
		template_file = self.config["template"]	
		template_fd = open(template_file)
		template = json.load(template_fd)
		template["title"] = app
		for row in template["rows"]:
			for panel in row["panels"]:
				for target in panel["targets"]:
					target["query"] = target["query"].replace("<CONTAINER_LIST>",where_str)
		return template
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
