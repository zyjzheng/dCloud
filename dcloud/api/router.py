from dcloud.utils.restful import Restful
import etcd

class Router(object):

    @staticmethod
    def getETCDClient():
        _etcd_host = Config.get("etcd.host")
        _etcd_port = string.atoi(Config.get("etcd.port"))
        return etcd.Client(host=_etcd_host,port=_etcd_port)

    @staticmethod
    def getAPIURL():
        return Config.get("vulcand.url")
    @staticmethod
    def getAPIVersion():
        return Config.get("vulcand.api.version")

    @staticmethod
    def createHost(host, app=None):
        _b = '''{
         "Name":"%s"
        }
        ''' % (host)
        _s,_m,_r = Restful.callRestApi("POST", Router.getAPIURL(), "/%s/%s" %(Router.getAPIVersion(), "hosts"), _b)
        if _s != 200:
            return False, _m
        return True, ""
    
    @staticmethod
    def createUpstream(upstream):
        _body='''{"Id":"%s"}''' %(upstream)
        _s, _m, _r = Restful.callRestApi("POST", Router.getAPIURL(), "/%s/%s" %(Router.getAPIVersion(), "upstreams"), _body)
        if _s != 200:
            return False, _m
        return True, ""

    @staticmethod
    def createLocation(host, name, path="/"):
        _body='''{
        "Id": "%s",
        "Hostname": "%s",
        "Path": "%s",
        "Upstream": {
            "Id": "%s"}
            }''' %(name, host, path, host)
        _s, _m, _r = Restful.callRestApi("POST", Router.getAPIURL(), "/%s/%s" %(Router.getAPIVersion(), "locations"), _body)
        if _s != z00:
            return False, _m
        return True, ""

    @staticmethod
    def deleteHost(host):
        _s, _m, _r = Restful.callRestApi("DELETE", Router.getAPIURL(), "/%s/%s" %(Router.getAPIVersion(), "hosts"))
        if _s != 200:
            return False, _m
        return True,""

    @staticmethod
    def map(host, app):
        _etcd = Router.getETCDClient()
        try:
            _etcd.directory().create("/vulcand/hosts/%s/apps/%s" % (host, app))
        except Exceptiopn,e:
            return False, e.strerror
        return True,""

    @staticmethod
    def unmap(host, app=None):
        _etcd = Router.getETCDClient()
        try:
            _etcd.directory().delete("/vulcand/hosts/%s/apps/%s" % (host, app))
        except Exceptiopn,e:
            return False, e.strerror
        return True,""
