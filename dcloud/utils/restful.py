import httplib 
import json

class Restful(object):
    @staticmethod
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
    
    @staticmethod
    def sendHttpPostRequest(url, path, body, headers):
        _conn = httplib.HTTPConnection(url)
        _conn.request("POST", path, body, headers)
        _response = _conn.getresponse()
        if _response.status !=200:
            return _response.status, _response.reason,None
        _data = _response.read()
        return _response.status,_response.reason,_data
    
    @staticmethod
    def sendHttpPutRequest(url, path, body, headers):
        _conn = httplib.HTTPConnection(url)
        _conn.request("PUT", path, body, headers)
        _response = _conn.getresponse()
        if _response.status !=200:
            return _response.status, _response.reason,None
        _data = _response.read()
        return _response.status,_response.reason,_data
    
    @staticmethod
    def sendHttpDeleteRequest(url, path, body, headers):
        _conn = httplib.HTTPConnection(url)
        _conn.request("DELETE", path, body, headers)
        _response = _conn.getresponse()
        if _response.status !=200:
            return _response.status, _response.reason,None
        _data = _response.read()
        return _response.status,_response.reason,_data
    
    @staticmethod
    def callRestApi(method, url, path, content=None, headers={"Content-Type":"application/json"}):
        if method == "GET":
            return Restful.sendHttpGetRequest(url,path,content, headers)
        if method == "POST":
            return Restful.sendHttpPostRequest(url,path,content, headers)
        if method == "PUT":
            return Restful.sendHttpPutRequest(url,path,content, headers)
        if method == "DELETE":
            return Restful.sendHttpDeleteRequest(url,path,content, headers)
        raise Exception("No Support Operator!!!")
