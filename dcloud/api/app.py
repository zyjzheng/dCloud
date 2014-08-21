class Application(object):
	def __init__(self, id, instances, cpu, mem, image, cmd)
		
		

class AppFactory(object):
	@staticmethod
	def push(id, instances, cpu, mem, image, cmd):
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
		''' % (image, id, instances, cpu, mem, cmd)
		_status,_msg,_resp = callRestApi("POST", config.Config.get("marathon.url"), "/v2/apps" , _body)
		if _status != 200:
			return False,_msg
	return True,""

	def get(id)

	@staticmethod
	def delete(id):
		_status,_msg,_resp = callRestApi("DELETE", config.Config.get("marathon.url"), "/v2/apps/%s" % (_id))
		if _status != 200:
			return False, _msg
		return True, ""

	@staticmethod
	def scale(id, instances):
		_body = '''
		{
		"id":"%s",
		"instances": "%s"
		}
		''' % (id, instances)
		_status, _msg, _resp = callRestApi("POST", config.Config.get("marathon.url"), "/v2/apps/%s" % (_id))
		if _status != 200:
			return False, _msg
		return True, ""