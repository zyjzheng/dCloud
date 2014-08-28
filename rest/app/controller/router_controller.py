from app.utils.httpclient import HttpClient
from app.utils.sysutils import SysUtils
import json
import traceback

header = {'Content-Type':'application/json'}

class RouterController:
	def __init__(self, config, logger):
		self.config = config
		self.logger = logger
		try:
			vulcand_host = self.config['router']['vulcand']['host']
			vulcand_port = self.config['router']['vulcand']['port']
			self.vulcand_app_version = self.config['router']['vulcand']['api_version']
			self.vulcand_client = HttpClient(vulcand_host, vulcand_port, self.logger)
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			if self.logger is not None:
				self.logger.error(trace)
			return 

	def get_hosts(self):
		try:
			result = self.vulcand_client.get_request('/%s/hosts'%(self.vulcand_app_version), header)
			if result == None:
				self.__reinit_client()
				result = self.vulcand_client.get_request('/%s/hosts'%(self.vulcand_app_version), header)
			status, content = SysUtils.getResult(result)
			status_bool = False
			if str(status).startswith('2'):
				status_bool = True
				content = json.loads(content)
				tmp_hosts = []
				for host in content['Hosts']:
					tmp_hosts.append(host['Name'])
				content = tmp_hosts
			return status_bool, content
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return False, "exception happended"

	def create_host(self,host):
		try:
			host_domain = str(host) + '.' + self.config['router']['domain']
			body = '{"name":"%s"}' % (host_domain)
			result = self.vulcand_client.post_request('/%s/hosts'%(self.vulcand_app_version), body, header)
			if result == None:
				self.__reinit_client()
				result = self.vulcand_client.post_request('/%s/hosts'%(self.vulcand_app_version), body, header)
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

	def delete_host(self, host):
		try:
			host_domain = str(host) + '.' + self.config['router']['domain']
			url = '/%s/hosts/'%(self.vulcand_app_version) + host_domain
			result = self.vulcand_client.del_request(url, header)
			if result == None:
				self.__reinit_client()
				result = self.vulcand_client.del_request(url, header)
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

	def is_host_exist(self, host_name):
		try:
			domain = self.config['router']['domain']
			host = host_name + "." + domain
			url = '/%s/hosts/'%(self.vulcand_app_version) + host + "/locations"
			result = self.vulcand_client.get_request(url, header)
			if result == None:
				self.__reinit_client()
				result = self.vulcand_client.get_request(url, header)
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

	def __reinit_client(self):
		try:
			vulcand_host = self.config['router']['vulcand']['host']
			vulcand_port = self.config['router']['vulcand']['port']
			self.vulcand_client = HttpClient(vulcand_host, vulcand_port, self.logger)
		except Exception, e:
			trace = traceback.format_exc()
			print(trace)
			self.logger.error(trace)
			return None
