from lib.bottle import request, route, response
from utils.logger import DCLogger
from utils.config import Config
from controller.router import RouterController
import json

config = Config.getConfig()
logger = DCLogger.get_default_logger()

if logger == None:
	log_file = config['log']['log_file']
	log_level = config['log']['log_level']
	logger = DCLogger(log_file, log_level)
	DCLogger.set_default_logger(logger)
router_controller = RouterController(config,logger)

@route('/router/hosts', method = ['GET'])
def get_hosts():
	status, content = router_controller.get_hosts()
	result = {"status":status,"content":content}
	return json.dumps(result)

@route('/router/hosts', method = ['POST'])
def create_host():
	body = request.json
	name = body['host']
	status, content = router_controller.create_host(name)
	result = {"status":status,"content":content}
	return json.dumps(result)

@route('/router/hosts/:host', method = ['DELETE'])
def delete_host(host):
	status, content = router_controller.delete_host(host)
	result = {"status":status,"content":content}
	return json.dumps(result)