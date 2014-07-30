#!/usr/bin/python
import httplib 
import json 
import os 
import logging 
import time
import etcd
import traceback

#LOG_FILE="/tmp/install.log"

logger = logging.getLogger()  
#fileHandler = logging.FileHandler(LOG_FILE)

consoleHandler = logging.StreamHandler()
#logger.addHandler(fileHandler) 
logger.addHandler(consoleHandler) 
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
#fileHandler.setFormatter(formatter)
consoleHandler.setFormatter(formatter)
#set log level  
logger.setLevel(logging.INFO)  


def getEndpoints():
    _marathon='9.115.210.55:8080'
    _etcd='etcd.bluemix.cdl.ibm.com'
    _vulcand='9.115.210.51:8182'
    return _marathon,_etcd, _vulcand

def getDomain():
    return 'de.bluemix.cdl.ibm.com'

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
	
def refreashRouter():
    _marathon_url, _etcd_url, _vulcand_url = getEndpoints()
    _etcd = etcd.Client(host=_etcd_url,port=4001,debug=logger)
    hosts = getHosts(_vulcand_url)
    for host in hosts:	
        initRouter(_vulcand_url, host['Name'])
        apps = []
        try:
            _tmp = _etcd.node.get("/vulcand/hosts/%s/apps" %(host['Name'])).node.children
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
        for _loc in host["Locations"]:
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
                deleteEndpoint(_vulcand_url, host['Name'], _end["Id"])
        for _task in tasks:
            find = False
            for _end in endpoints:
                if _task["id"] == _end["Id"]:
                    find = True
                    break
            if find == False:
                addEndpoint(_vulcand_url, host['Name'], _task["id"], "http://%s:%s" % (_task['host'], _task['ports'][0]))
		
def run():
	while True:
		refreashRouter()
		time.sleep(5)
    

if __name__ == '__main__':
   run()
   # _installCloudOE()
