from dcloud.utils.restful import Restful
from dcloud.utils.log import logger
from dcloud.utils.config import Config
import json
class AppFactory(object):
    @staticmethod
    def push(_id, _instances, _cpu, _mem, _image, _cmd):
        _body = '''
        {
          "container": {
               "type": "DOCKER",
               "docker": {
                   "image": "%s"
               }
          },
          "id": "%s",
          "instances": "%s",
          "cpus": "%s",
          "mem": "%s",
          "uris": [] ,
          "ports": [0],
          "cmd": "%s"
        }
        ''' % (_image, _id, _instances, _cpu, _mem, _cmd)
        _status,_msg,_resp = Restful.callRestApi("POST", Config.get("marathon.url"), "/v2/apps" , _body)
        if _status != 201:
            return False,_msg
        return True,""

    @staticmethod
    def get(_id):
        _status, _msg, _resp = Restful.callRestApi("GET", Config.get("marathon.url"), "/v2/apps/%s" %(_id))
        if _status == 200:
            return json.loads(_resp)['app']
        return None

    @staticmethod
    def delete(_id):
        _status,_msg,_resp = Restful.callRestApi("DELETE", Config.get("marathon.url"), "/v2/apps/%s" % (_id))
        if _status != 200:
            return False, _msg
        return True, ""

    @staticmethod
    def scale(_id, _instances):
        _body = '''
        {
        "id":"%s",
        "instances": "%s"
        }
        ''' % (_id, _instances)
        print _body
        _status, _msg, _resp = Restful.callRestApi("PUT", Config.get("marathon.url"), "/v2/apps/%s" % (_id), _body)
        print _status
        print _msg 
        print _resp
        if _status != 204:
            return False, _msg
        return True, ""
