# coding: utf-8
# zktest.py

import logging
from os.path import basename, join

from zkclient import ZKClient, zookeeper, watchmethod

logging.basicConfig(
    level = logging.DEBUG,
    format = "[%(asctime)s] %(levelname)-8s %(message)s"
)

log = logging

class AppWatcher(object):

    TIMEOUT = 10000
    app_list = []
    def __init__(self, zk_host, root):
        self.zk_host = zk_host
        self.root_path = root

        self.zk = ZKClient(self.zk_host, timeout = self.TIMEOUT)
        
        childrens = self.zk.get_children(self.root_path)
        for i in childrens:
            if i.startswith("tasks:"):
               self.app_list.append(i) 
        self.init_watcher()

    def init_watcher(self):
        @watchmethod
        def watcher(event):
            self.init_watcher()
            log.info(dir(event))
            log.info(event.type_name)
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
#push wrong node to yuanjie's code
            elif type_name == "changed" and path.startswith(self.root_path):
                try:
                    path.index("tasks:")
                    log.info(path)
                    app_name = path.rsplit("/",1)[1]
                    except_node.append(app_name)
                except Exception, e:
                    pass
            print except_node
        children = self.zk.get_children(self.root_path, watcher)
        for i in children:
            if i.startswith("tasks:"):
                self.zk.get(join(self.root_path, i), watcher)

def main():
    watcher = AppWatcher("9.115.210.54:2181", "/marathon/state")

if __name__ == "__main__":
    import time
    main()
    while True:
        time.sleep(10)

