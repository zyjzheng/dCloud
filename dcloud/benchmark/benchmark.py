'''
[Default]
zk.url = zk.bluemix.cdl.ibm.com:2181
marathon.url = 9.115.210.55:8080
vulcand.url = 9.115.210.51:8182
vulcand.api.version = v1
zk.rootnode = /marathon/state
etcd.host = etcd.bluemix.cdl.ibm.com
etcd.port = 4001


[Benchmark]
benchmark.app.image = helloworld
benchmark.app.cmd = node hello.js
benchmark.app.mem = 256
benchmark.app.cpu = 0.1
benchmark.app.host = test.de.bluemix.cdl.ibm.com
benchmark.app.heathcheck.path = /
benchmark.app.heathcheck.schema = http
benchmark.app.heathcheck.interval = 30
benchmark.app.instances = 200
benchmark.timeout = 600
benchmark.times = 60
'''
from dcloud.utils.config import Config
from dcloud.utils.restful import restful
from dcloud.api.app import app
from dcloud.api.router import router
from threading import Thread
import time

class HeathCheck(Thread):
	def __init__(self, _schema, _domain,_path, _interval):
		self.schema   = _schema
		self.domain   = _domain
		self.path     = _path
		self.interval = _interval
		self.success  = 0
		self.failed   = 0

	def check():
		_s, _m, _r = Restful.sendHttpGetRequest("%s://%s"%(self.schema, self._domain), "/%s" % (_path), None, None)
		if _s != 200:
			self.failed = self.failed + 1
		else:
			self.success = self.success + 1

    def cancel():
    	self.stoped = True

	def run():
		while !self.stoped:
			self.check()

	def dump():
		_r = '''
		url     : %s://%s/%s
		success : %d
		failed  : %d
		''' % (self.schema, self.domain, self.path, self.success, self.failed)
		return _r

class Monster():

	def 

	def __init__():
		pass
	def createApp():
		pass
	def scale()

class Benchmark(object):
	def __init__(self):
		self.image = Config.get("benchmark.app.image")
		self.cmd = Config.get("benchmark.app.cmd")
		self.mem = Config.get("benchmark.app.mem")
		self.cpu = Config.get("benchmark.app.cpu")
		self.host = Config.get("benchmark.app.host")
		self.heathcheck = HeathCheck.new(Config.get("benchmark.app.heathcheck.schema"), 
			host, 
			Config.get("benchmark.app.heathcheck.path"),
			Config.get("benchmark.app.heathcheck.interval"))
		self.instances = Config.get("benchmark.app.instances")
		self.timeout = Config.get("benchmark.timeout")
		self.times = Config.get("benchmark.times")
		self.startTime = time.time()

		pass

	def start(self):
		pass