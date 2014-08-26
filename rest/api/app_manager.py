from lib.bottle import request, route, response
from utils.logger import DCLogger
from utils.config import Config
from controller.app import AppController
from controller.router import RouterController
import json

config = Config.getConfig()
logger = DCLogger.get_default_logger()

if logger == None:
	log_file = config['log']['log_file']
	log_level = config['log']['log_level']
	logger = DCLogger(log_file, log_level)
	DCLogger.set_default_logger(logger)
app_controller = AppController(config, logger)
router_controller = RouterController(config,logger)

@route('/apps', method = ['GET'])
def get_all_apps():
	status, content = app_controller.get_apps()
	result = {"status":status,"content":content}
	return json.dumps(result)
	
@route('/apps', method = ['POST'])
def create_app():
	body = request.json
	status, content = app_controller.create_app(body)
	result = {"status":status,"content":content}
	return json.dumps(result)

@route('/apps/:name', method = ['GET'])
def get_app(name):
	status, content = app_controller.get_app(name)
	result = {"status":status,"content":content}
	return json.dumps(result)

@route('/apps/:name', method = ['PUT'])
def update_app(name):
	put_body = request.json
	put_body['id'] = name
	status, content = app_controller.update_app(name, put_body)
	result = {"status":status,"content":content}
	return json.dumps(result)

@route('/apps/:name', method = ['DELETE'])
def delete_app(name):
	status, content = app_controller.delete_app(name)
	result = {"status":status,"content":content}
	return json.dumps(result)

@route('/apps/:name/routers/:router', method = ['POST'])
def map_app_to_router(name, router):
	if app_controller.is_app_exist(name) and router_controller.is_host_exist(router):
		status, content = app_controller.map_app_to_router(name, router)
		result = {"status":status,"content":content}
		return json.dumps(result)
	else:
		result = {"status":False,"content":"app or router not exist!"}
		return json.dumps(result)

@route('/apps/:name/routers/:router', method = ['DELETE'])
def unmap_app_to_router(name, router):
	if app_controller.is_app_exist(name) and router_controller.is_host_exist(router):
		status, content = app_controller.unmap_app_to_router(name, router)
		result = {"status":status,"content":content}
		return json.dumps(result)
	else:
		result = {"status":False,"content":"app or router not exist!"}
		return json.dumps(result)




