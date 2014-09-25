import os
import json
import time
import inspect
import traceback
import etcd
from elasticsearch import Elasticsearch
from httpclient import HttpClient
from marathon import MarathonClient

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
			self.pre_apps = []
			self.pre_task = {}
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			return None

	def start(self):
		marathon_client = MarathonClient(self.config)
		apps = marathon_client.get_marathon_apps()
		running_apps = []
		running_task = {}
		for app in apps:
			app_id = self.format_app_id(app["id"])
			running_apps.append(app_id)
			running_task[app_id] = self.__get_app_tasks(app_id)
		print("start to update grafana templates")                                
		self.update_templates(running_task)
		self.pre_task = running_task
		print("finish updating")
		print("delete useless templates")
		self.delete_app_templates(running_apps)
		self.pre_apps = running_apps
		print("finish deleting useless templates")


	def format_app_id(self,app_id = ""):
		if app_id != "":
			if app_id[0] == '/':
				app_id = app_id.split("/",2)[1]
		return app_id

	def delete_app_templates(self, running_apps):
		for old_app in self.pre_apps:
			try:
				running_apps.index(old_app)
			except Exception, e:
				es = self.__get_es_client()
				es.delete(index="grafana-dash",doc_type="dashboard",id=old_app)

	
	def __compare_tasks(self, new_tasks, old_tasks):
		for new_key in new_tasks.keys():
			try:
				temp = old_tasks[new_key]
				if new_tasks[new_key] != temp:
					return False
			except Exception, e:
				return False
		for old_key in old_tasks.keys():
			try:
				temp = new_tasks[old_key]
				if old_tasks[old_key] != temp:
					return False
			except Exception, e:
				return False
		return True

	def update_templates(self, running_task):
		need_change_apps = []
		temp_containers = {}
		for app_id in running_task.keys():
			new_tasks = running_task[app_id]
			try:
				old_tasks = self.pre_task[app_id]
				if not self.__compare_array(new_tasks, old_tasks):
					need_change_apps.append(app_id)
			except Exception, e:
				need_change_apps.append(app_id)
		self.__update_templates_es(need_change_apps,running_task)

	def __get_es_client(self):
		es_host = self.config["ES_host"]
		es_port = self.config["ES_port"]
		es = Elasticsearch([{"host": es_host, "port": es_port}])
		return es		

	def __update_templates_es(self, apps, running_task):
		es = self.__get_es_client()
		for app in apps:
			containers = running_task[app]
			where_str = " and ( 1 > 2 "
			for task in containers.keys():
				container = "/docker/mesos-" + containers[task]
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
	def __get_app_tasks(self, app_id):
		etcd_host = self.config["etcd"]["host"]
		etcd_port = self.config["etcd"]["port"]
		etcd_client = etcd.Client(host=etcd_host, port=etcd_port)
		running_tasks = {}
		try:
			all_apps = etcd_client.node.get("/apps/%s/instances" %(app_id)).node.children	
	
			try:
				while True:
					app_node = all_apps.next()
					task_id = app_node.key[app_node.key.rindex("/")+ 1:]
					value = app_node.value
					try:
						container = json.loads(value)["container"]
						running_tasks[task_id] = container
					except Exception, e:
						#traceback.print_exc()
						pass

			except Exception, e:
				traceback.print_exc()
		except Exception,e:
			traceback.print_exc()			
		return running_tasks

if __name__ == "__main__":
	try:
		ds = DeamonServer()
		while(True):
			try:
				ds.start()
			except Exception, e:
				trace = traceback.format_exc()
				print(trace)
			time.sleep(100)

	except Exception, e:
		trace = traceback.format_exc()
		print(trace)
