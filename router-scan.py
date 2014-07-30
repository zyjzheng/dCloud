from router import Router
from appwatcher import AppWatcher
import config
import log
import time

if __name__ == '__main__':
    watcher = AppWatcher(config.Config.get("zk.url"), config.Config.get("zk.rootnode"),log.logger)
    Router.run()
    while True:
        try:
            Router.pushHosts(["*"])
            Router.push(["helloxs"])
            time.sleep(5)
        except KeyboardInterrupt, ki:
            Router.stop()
            time.sleep(2)
            break
    print "Stop to refresh the router table."
