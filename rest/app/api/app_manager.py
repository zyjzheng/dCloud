from lib.bottle import request, route, response
from app.utils.logger import DCLogger
from app.utils.config import Config
from app.controller.app_controller import AppController
from app.controller.router_controller import RouterController
import json


config = Config.getConfig()
logger = DCLogger.get_default_logger()

app_controller = AppController(config, logger)
router_controller = RouterController(config,logger)

assert app_controller != None
assert router_controller != None

@route('/apps', method = ['GET'])
def get_all_apps():
	status, content = app_controller.get_apps()
	set_http_status(status, response)
	result = {"status":status,"content":content}
	return json.dumps(result)
	
@route('/apps', method = ['POST'])
def create_app():
	body = request.json
	status, content = app_controller.create_app(body)
	set_http_status(status, response)
	result = {"status":status,"content":content}
	return json.dumps(result)

@route('/apps/:name', method = ['GET'])
def get_app(name):
	status, content = app_controller.get_app(name)
	set_http_status(status, response)
	result = {"status":status,"content":content}
	return json.dumps(result)

@route('/apps/:name', method = ['PUT'])
def update_app(name):
	put_body = request.json
	put_body['id'] = name
	status, content = app_controller.update_app(name, put_body)
	set_http_status(status, response)
	result = {"status":status,"content":content}
	return json.dumps(result)

@route('/apps/:name', method = ['DELETE'])
def delete_app(name):
	status, content = app_controller.delete_app(name)
	set_http_status(status, response)
	result = {"status":status,"content":content}
	return json.dumps(result)

@route('/apps/:name/routers/:router', method = ['POST'])
def map_app_to_router(name, router):
	if app_controller.is_app_exist(name) and router_controller.is_host_exist(router):
		status, content = app_controller.map_app_to_router(name, router)
		set_http_status(status, response)
		result = {"status":status,"content":content}
		return json.dumps(result)
	else:
		result = {"status":False,"content":"app or router not exist!"}
		set_http_status(False, response)
		return json.dumps(result)

@route('/apps/:name/routers/:router', method = ['DELETE'])
def unmap_app_to_router(name, router):
	if app_controller.is_app_exist(name) and router_controller.is_host_exist(router):
		status, content = app_controller.unmap_app_to_router(name, router)
		set_http_status(status, response)
		result = {"status":status,"content":content}
		return json.dumps(result)
	else:
		result = {"status":False,"content":"app or router not exist!"}
		set_http_status(False, response)
		return json.dumps(result)

def set_http_status(status, resp):
	if status:
		resp.status = 200
	else:
		resp.status = 400



