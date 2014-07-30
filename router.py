#!/usr/bin/python
import httplib 
import json 
import os 
import time
import etcd
import traceback
import Queue
import threading
import config
import string
from log import logger

def sendHttpGetRequest(url, path, parameter, headers):
    _conn = httplib.HTTPConnection(url)
    _path=path
    if parameter :
        _path = _path + "?"
        for k in parameter.keys():
            _path = path + "&%s=%s" % (k, parameter[k])
    _conn.request("GET", _path, None, headers)
    _response = _conn.getresponse()
    if _response.status !=200:
        return _response.status, _response.reason,None
    _data = _response.read()
    return _response.status,_response.reason,_data

def sendHttpPostRequest(url, path, body, headers):
    _conn = httplib.HTTPConnection(url)
    _conn.request("POST", path, body, headers)
    _response = _conn.getresponse()
    if _response.status !=200:
        return _response.status, _response.reason,None
    _data = _response.read()
    return _response.status,_response.reason,_data

def sendHttpPutRequest(url, path, body, headers):
    _conn = httplib.HTTPConnection(url)
    _conn.request("PUT", path, body, headers)
    _response = _conn.getresponse()
    if _response.status !=200:
        return _response.status, _response.reason,None
    _data = _response.read()
    return _response.status,_response.reason,_data

def sendHttpDeleteRequest(url, path, body, headers):
    _conn = httplib.HTTPConnection(url)
    _conn.request("DELETE", path, body, headers)
    _response = _conn.getresponse()
    if _response.status !=200:
        return _response.status, _response.reason,None
    _data = _response.read()
    return _response.status,_response.reason,_data

def callRestApi(method, url, path, content=None, headers={"Content-Type":"application/json"}):
    if method == "GET":
        return sendHttpGetRequest(url,path,content, headers)
    if method == "POST":
        return sendHttpPostRequest(url,path,content, headers)
    if method == "PUT":
        return sendHttpPutRequest(url,path,content, headers)
    if method == "DELETE":
        return sendHttpDeleteRequest(url,path,content, headers)
    raise Exception("No Support Operator!!!")

def createUpstream(url, upstream):
    _body='''{
        "Id":"%s"}''' %(upstream)
    _status, _msg, _resp = callRestApi("POST", url, "/v1/upstreams", _body)
    logger.info("add upstream %s ,  status: %d, msg: %s, _resp: %s", upstream, _status, _msg, _resp)

def createLocation(url, host, name="default", path="/"):
    _body='''{
        "Id": "%s",
        "Hostname": "%s",
        "Path": "%s",
        "Upstream": {
            "Id": "%s"
        }
    }
    ''' %(name, host, path, host)
    _status, _msg, _resp = callRestApi("POST", url, "/v1/hosts/%s/locations" % (host), _body)	
    logger.info("add location %s{%s=>%s} status: %d, msg: %s, _resp: %s", host, name, host, _status, _msg, _resp)

def initRouter(url, host):
    createUpstream(url, host)
    createLocation(url, host, "default", "/")

def deleteEndpoint(url, upstream, endpoint):
    _status,_msg,_resp = callRestApi("DELETE", url, "/v1/upstreams/%s/endpoints/%s" %(upstream, endpoint))
    logger.info("delete endpoint %s====> %s status: %d, msg: %s, _resp: %s", upstream, endpoint, _status, _msg, _resp)

def addEndpoint(url, upstream, name, backend):
    _body='''{
        "UpstreamId": "%s",
        "Id": "%s",
        "Url": "%s"
    }
    ''' %(upstream,name, backend)

    _status, _msg, _resp=callRestApi("POST", url, "/v1/upstreams/%s/endpoints" % (upstream), _body)
    logger.info("add endpoint %s====> %s:%s status: %d, msg: %s, _resp: %s", upstream, name, backend, _status, _msg, _resp)

def getHosts(url):
    _status,_msg,_resp=callRestApi("GET", url, "/v1/hosts")
    return json.loads(_resp)['Hosts']

def refreashRouter(host=None):
    
    _marathon_url = config.Config.get("marathon.url")
    _etcd_host = config.Config.get("etcd.host")
    _etcd_port = string.atoi(config.Config.get("etcd.port"))
    _vulcand_url = config.Config.get("vulcand.url")
    _etcd = etcd.Client(host=_etcd_host,port=_etcd_port,debug=logger)

    _hosts = getHosts(_vulcand_url)
    for _host in _hosts:

        if host and host != _host['Name']:
            continue	
        initRouter(_vulcand_url, _host['Name'])
        apps = []
        try:
            _tmp = _etcd.node.get("/vulcand/hosts/%s/apps" %(_host['Name'])).node.children
            while True:
                _n = _tmp.next()
                apps.append(_n.key[_n.key.rindex("/")+1:])
        except Exception,e:
            #traceback.print_exc()
            pass
        except Exception,e:
            #traceback.print_exc()
            continue
        tasks = []
        for app in apps:
            _status,_msg,_resp= callRestApi("GET", _marathon_url, "/v2/apps/%s/tasks" % (app))
            _t = json.loads(_resp)['tasks']
            for task in _t:
                tasks.append(task)
        endpoints = []
        for _loc in _host["Locations"]:
            if _loc['Id'] == 'default':
                endpoints = _loc["Upstream"]["Endpoints"]
                break;
        for _end in endpoints:
            find = False
            for _task in tasks:
                if _task["id"] == _end["Id"]:
                    find = True
                    break
            if find == False:
                deleteEndpoint(_vulcand_url, _host['Name'], _end["Id"])
        for _task in tasks:
            find = False
            for _end in endpoints:
                if _task["id"] == _end["Id"]:
                    find = True
                    break
            if find == False:
                addEndpoint(_vulcand_url, _host['Name'], _task["id"], "http://%s:%s" % (_task['host'], _task['ports'][0]))

def getHostsByApps(apps):
    hosts = {}
    _etcd_host = config.Config.get("etcd.host")
    _etcd_port = string.atoi(config.Config.get("etcd.port"))
    _etcd = etcd.Client(host="etcd.bluemix.cdl.ibm.com",port=_etcd_port)
    _hosts = _etcd.node.get("/vulcand/hosts").node.children
    while True:
        _host = None
        try:
            _host = _hosts.next()
        except Exception,e:
            pass
        if _host == None:
            break
        _hostname = _host.key[_host.key.rindex("/")+1:]
        apps = None 
        try:
            _apps = _etcd.node.get("%s/apps" %(_host.key)).node.children
        except Exception, e:
            pass
        if _apps == None:
            break
        while True:
            _app = None
            try:
                _app = apps.next()
            except Exception,e :
                pass
            if _app == None:
                break;
            _appname = _app.key[_app.key.rindex("/")+1:]
            for app in apps:
                if app == _appname:
                    hosts[_hostname] = _hostname
    return hosts

queue = Queue.Queue(0)

class Worker(threading.Thread):
    _stop = False
    def stop(self):
        self._stop = True
    def run(self):
        while(self._stop is not True):
            _host = None
            try:
                _host = queue.get(timeout=2)
            except Exception, e:
                pass
            if _host == None:
                continue
            logger.info("handler host %s" %(_host))
            if _host == "*":
                refreashRouter()
            else:
                refreashRouter(_host)

worker = Worker()

class Router:
    
    @staticmethod
    def push(apps):
        hosts = getHostsByApps(apps)
        for _k, _v  in hosts:
            queue.put(_v)

    @staticmethod
    def pushHosts(hosts):
        for host in hosts:
            queue.put(host)

    @staticmethod
    def run():
        worker.start()

    @staticmethod
    def stop():
        worker.stop()

if __name__ == '__main__':
    Router.run()
    while True:
        try:
            Router.pushHosts(["*"])
            Router.push(["helloxs"])
            time.sleep(5)
        except KeyboardInterrupt, ki:
            Router.stop()
            time.sleep(10)
            break
    print "Stop to refresh the router table."
