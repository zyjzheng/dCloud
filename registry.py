import etcd, json, sys, time, traceback, string

from dcloud.utils.log import logger
from dcloud.utils.restful import Restful
from dcloud.utils.config import Config

REGISTRY_PREFIX="/apps"
TTL = 60
mesos_slave_url = sys.argv[1]

def callRestApi(_m, _u, _p, _b=None):
    return Restful.callRestApi(_m, _u, _p, _b)

def getEtcd():
    _etcd_host = Config.get("etcd.host")
    _etcd_port = string.atoi(Config.get("etcd.port"))
    _etcd = etcd.Client(host=_etcd_host,port=_etcd_port)
    return _etcd

def etcdNodeSet(path, value, ttl=None):
    _etcd = getEtcd()
    _etcd.node.set(path, value, ttl)

def etcdCreateDir(path, ttl=None):
    if etcdNodeExist(path) == False:
        _etcd = getEtcd()
        _etcd.directory.create(path, ttl)

def etcdNodeExist(path):
    try:
       _etcd = getEtcd()
       _tmp = _etcd.node.get(path)
       if _tmp != None:
           return True
    except Exception, e:
       pass
    return False

def freshRegistry():
    _status,_msg,_resp= callRestApi("GET", mesos_slave_url, "/state.json")
    if _status != 200:
        return
    _frameworks = json.loads(_resp)['frameworks']
    if len(_frameworks) == 0:
        return
    for _f in _frameworks:   
        _executors = _f['executors']
        for _e in _executors:
            if len(_e['tasks']) == 0:
                continue
            _id = _e['id']
            _container = _e['container']
            _app = _id[0 : _id.index(".")]
            _tmp = '''{"container":"%s"}''' % (_container)
            if etcdNodeExist(REGISTRY_PREFIX+"/"+ _app + "/instances/" + _id ) == True > 0 :
                etcdNodeSet(REGISTRY_PREFIX+"/"+_app + "/instances/" + _id, _tmp, TTL)
    
if __name__ == '__main__':
    while True:
        try:
            freshRegistry()
            time.sleep(30)
        except KeyboardInterrupt, ki:
            time.sleep(2)
            break
        except Exception, e:
            traceback.print_exc()
    print "Stop to refresh the router table."
