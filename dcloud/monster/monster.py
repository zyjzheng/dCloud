import random
import time, uuid
from threading import Thread
from dcloud.api.router import Router
from dcloud.utils.config import Config
from dcloud.utils.restful import Restful
from dcloud.utils.log import logger
from dcloud.api.app import AppFactory

class HeathCheck(Thread):
    def __init__(self, _schema, _domain,_path, _interval):
        self.schema   = _schema
        self.domain   = _domain
        self.path     = _path
        self.interval = _interval
        self.success  = 0
        self.failed   = 0
        self.stoped   = False

    def check(self):
        _s, _m, _r = Restful.sendHttpGetRequest("%s://%s"%(self.schema, self._domain), "/%s" % (_path), None, None)
        if _s != 200:
            self.failed = self.failed + 1
        else:
            self.success = self.success + 1
	
    def cancel(self):
        self.stoped = True

    def run(self):
        while self.stoped != True:
            self.check()
            time.sleep(self.interval)

    def dump(self):
        _r = '''
        url     : %s://%s/%s
        success : %d
        failed  : %d
        ''' % (self.schema, self.domain, self.path, self.success, self.failed)
        return _r

class Monster(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.image = Config.get("benchmark.app.image", "Benchmark")
        self.cmd = Config.get("benchmark.app.cmd", "Benchmark")
        self.mem = Config.get("benchmark.app.mem", "Benchmark")
        self.cpu = Config.get("benchmark.app.cpu", "Benchmark")
        self.host = Config.get("benchmark.app.host", "Benchmark")
        self.instances = int(Config.get("benchmark.app.instances", "Benchmark"))
        self.timeout = Config.get("benchmark.timeout", "Benchmark")
        self.times = Config.get("benchmark.times", "Benchmark")
        self.startTime = time.time()
        self.id ="monster-" + str(uuid.uuid1())
        self.scale = 0
        self.stoped = False

    def checkStatus(self):
        _app = AppFactory.get(self.id)
        if _app:
            if _app['tasksStaged'] == _app['tasksRunning'] and _app['tasksRunning']!=0:
                return True
        return False
    
    def createApp(self):
        logger.info("create app!!!")
        _r, _m  = AppFactory.push(self.id, self.instances, self.cpu, self.mem, self.image, self.cmd)
        return _r
    
    def scaleApp(self):
        logger.info("scale app")
        self.scale = self.scale + 1
        app = AppFactory.get(self.id)
        if app:
            if app['instances'] == app['tasksRunning'] :
                _instances = app['instances']
                _num = random.randint(0,self.instances)
                _instances = abs(_instances - _num)
                if _instances <1:
                    _instances = 1
                if _instances >= self.instances:
                    _instances = self.instances
                AppFactory.scale(self.id, _instances)
                time.sleep(30)

    def deleteApp(self):
        logger.info("delete app")
        _r, _m = AppFactory.delete(self.id)
        return _r
    def stop(self):
        self.stoped = True

    def run(self):
        _r = self.createApp()
        if _r :
            while self.stoped != True:
                self.scaleApp()
                time.sleep(5)
            _r = self.deleteApp()
        else:
            logger.info("app create failed")
