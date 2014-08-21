from dcloud.router_emitter.emitter import Emitter
from dcloud.router_emitter.appwatcher import AppWatcher
from dcloud.utils.config import Config
from dcloud.utils.log import logger
import time

if __name__ == '__main__':
    watcher = AppWatcher(Config.get("zk.url"), Config.get("zk.rootnode"), logger)
    Emitter.run()
    while True:
        try:
            Emitter.pushHosts(["*"])
            time.sleep(5)
        except KeyboardInterrupt, ki:
            Emitter.stop()
            time.sleep(2)
            break
    print "Stop to refresh the router table."
