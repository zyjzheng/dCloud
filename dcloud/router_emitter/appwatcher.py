# coding: utf-8
# zktest.py

import logging
from os.path import basename, join

from dcloud.utils.zkclient import ZKClient, zookeeper, watchmethod
from dcloud.router_emitter.emitter import Emitter

logging.basicConfig(
    level = logging.DEBUG,
    format = "[%(asctime)s] %(levelname)-8s %(message)s"
)

log = logging

class AppWatcher(object):

    TIMEOUT = 10000
    app_list = []
    def __init__(self, zk_host, root, logger):
        self.zk_host = zk_host
        self.root_path = root
        self.logger = logger
        self.zk = ZKClient(self.zk_host, timeout = self.TIMEOUT)
        self.logger.info("+++++++zookeeper connected++++++++")
        
    def start(self):
        childrens = self.zk.get_children(self.root_path)
        for i in childrens:
            if i.startswith("tasks:"):
               self.app_list.append(i) 
        self.init_watcher()

    def init_watcher(self):
        @watchmethod
        def watcher(event):
            self.init_watcher()
            self.logger.info(dir(event))
            self.logger.info(event.type_name)
            type_name = event.type_name
            path = event.path
            except_node = []
            if type_name == "child" and path == self.root_path:
                temp_children = self.zk.get_children(self.root_path)
                for i in self.app_list:
                    try:
                        temp_children.index(i)
                    except Exception, e:
                        except_node.append(i)
                for i in temp_children:
                    if i.startswith("tasks:"):
                        try:    
                            self.app_list.index(i)
                        except Exception, e:
                            except_node.append(i)
                self.app_list = []
                for i in temp_children:
                    if i.startswith("tasks:"):
                        self.app_list.append(i)
            elif type_name == "changed" and path.startswith(self.root_path):
                try:
                    path.index("tasks:")
                    self.logger.info(path)
                    app_name = path.rsplit("/",1)[1]
                    except_node.append(app_name)
                except Exception, e:
                    pass
            self.logger.info(except_node)
            result = []
            for i in except_node:
                try:
                    result.append(i.split(":",1)[0])
                except Exception, e:
                    pass
            self.logger.info(result)
            #push node array to yuanjie
            Emitter.push(result)
        children = self.zk.get_children(self.root_path, watcher)
        for i in children:
            if i.startswith("tasks:"):
                self.zk.get(join(self.root_path, i), watcher)

def main():
    watcher = AppWatcher("9.115.210.54:2181", "/marathon/state",log)
    watcher.start()

if __name__ == "__main__":
    import time
    main()
    while True:
        time.sleep(10)

