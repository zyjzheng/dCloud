from app.utils.httpclient import HttpClient
from app.utils.sysutils import SysUtils
import json
import traceback
import os, inspect

header = {'Content-Type':'application/json'}
class AppController:
	def __init__(self,config,logger):
		self.config = config
		self.logger = logger
		try:
			marathon_host = self.config['marathon']['host']
			marathon_port = self.config['marathon']['port']
			self.marathon_client = HttpClient(marathon_host, marathon_port)
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return 

	def get_apps(self):
		try:
			result = self.marathon_client.get_request('/v2/apps',header)
			if result == None:
				self.__reinit_client()
				result = self.marathon_client.get_request('/v2/apps',header)
			status, content = SysUtils.getResult(result)
			status_bool = False
			if str(status).startswith('2'):
				status_bool = True
				content = json.loads(content)
				apps = content['apps']
				tmp_apps = []
				for app in apps:
					tmp_app = {}
					tmp_app['id'] = app['id']
					tmp_app['cmd'] = app['cmd']
					tmp_app['env'] = app['env']
					tmp_app['instances'] = app['instances']
					tmp_app['cpus'] = app['cpus']
					tmp_app['mem'] = app['mem']
					tmp_app['container'] = app['container']
					tmp_app['staged'] = app['tasksStaged']
					tmp_app['running'] = app['tasksRunning']
					tmp_apps.append(tmp_app)
				content = tmp_apps
			return status_bool, content
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return False, "exception happended"


	def get_app(self, name):
		try:
			print(name)
			result = self.marathon_client.get_request('/v2/apps/' + name, header)
			if result == None:
				self.__reinit_client()
				result = self.marathon_client.get_request('/v2/apps/' + name, header)
			status, content = SysUtils.getResult(result)
			rtn_content = {}
			if str(status).startswith('2'):
				content_json = json.loads(content)
				rtn_content['id'] = content_json['app']['id']
				rtn_content['cmd'] = content_json['app']['cmd']
				rtn_content['env'] = content_json['app']['env']
				rtn_content['instances'] = content_json['app']['instances']
				rtn_content['cpus'] = content_json['app']['cpus']
				rtn_content['mem'] = content_json['app']['mem']
				rtn_content['container'] = content_json['app']['container']
				rtn_content['staged'] = content_json['app']['tasksStaged']
				rtn_content['running'] = content_json['app']['tasksRunning']
				
			status_bool = False
			if str(status).startswith('2'):
				status_bool = True
			return status_bool, rtn_content
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return False, "exception happended"

	def is_app_exist(self, name):
		try:
			result = self.marathon_client.get_request('/v2/apps/' + name,  header)
			if result == None:
				self.__reinit_client()
				result = self.marathon_client.get_request('/v2/apps/' + name,  header)
			status, content = SysUtils.getResult(result)
			if str(status).startswith('2'):
				return True
			else:
				return False
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return False

	def create_app(self, body):
		try:
			body = json.dumps(body)
			result = self.marathon_client.post_request('/v2/apps',body,header)
			if result == None:
				self.__reinit_client()
				result = self.marathon_client.post_request('/v2/apps',body,header)
			status, content = SysUtils.getResult(result)
			status_bool = False
			if str(status).startswith('2'):
				status_bool = True
				content = json.loads(content)
			return status_bool, content
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return False, "exception happended"

	def update_app(self, name, body):
		try:
			body = json.dumps(body)
			result = self.marathon_client.put_request('/v2/apps/' + name, body, header)
			if result == None:
				self.__reinit_client()
				result = self.marathon_client.put_request('/v2/apps/' + name, body, header)
			status, content = SysUtils.getResult(result)
			status_bool = False
			if str(status).startswith('2'):
				status_bool = True
			return status_bool, content
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return False, "exception happended"

	def delete_app(self, name):
		try:
			result = self.marathon_client.del_request('/v2/apps/' + name, header)
			if result == None:
				self.__reinit_client()
				result = self.marathon_client.del_request('/v2/apps/' + name, header)
			status, content = SysUtils.getResult(result)
			status_bool = False
			if str(status).startswith('2'):
				status_bool = True
			return status_bool, content
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return False, "exception happended"

	def map_app_to_router(self, app_name, router):
		try:
			cur_dir = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
			map_sh = cur_dir + "/../" + "../bin/map.sh"
			status_code = SysUtils.run_cmd(map_sh + " " + router + " " + app_name)
			status = False
			if status_code == 0:
				status = True
			return status, ""
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return False, "exception happended"

	def unmap_app_to_router(self, app_name, router):
		try:
			cur_dir = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])
			unmap_sh = cur_dir + "/../" + "../bin/unmap.sh"
			status_code = SysUtils.run_cmd(unmap_sh + " " + router + " " + app_name)
			status = False
			if status_code == 0:
				status = True
			return status, ""
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return False, "exception happended"

	def __reinit_client(self):
		try:
			marathon_host = self.config['marathon']['host']
			marathon_port = self.config['marathon']['port']
			self.marathon_client = HttpClient(marathon_host, marathon_port)
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return None

