import traceback
import json
import time
from httpclient import HttpClient

class MarathonClient:

	def __init__(self, config):
		self.config = config

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

	def get_marathon_apps(self):
		marathon_api = self.config["marathon_api"]
		api_version = self.config["marathon_api_version"]
		marathon_client = HttpClient(marathon_api)
		result = marathon_client.get_request("/" + api_version +"/apps",{})
		if result is not None:
			status = result[0]
			content = result[1]
			#print(content)
			try:
				apps = json.loads(content)["apps"]
			except Exception, e:
				raise Exception("can not format response content")
			return apps
		else:
			raise Exception("can not get marathon apps")

	def __get_running_task(self,framework):
		running_tasks = []
		executors = framework["executors"]
		for task in executors:
			running_task = {}
			running_task["id"] = task["id"]
			running_task["container"] = task["container"]
			running_tasks.append(running_task)
		return running_tasks

	def get_mesos_slave_container(self, host):
		port = self.config["slave_port"]
		state_url = "/state.json"
		try:
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
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			return []