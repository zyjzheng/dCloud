from lib.bottle import request, route, response


@route('/info', method = ['GET'])
def get_all_apps():
	response.status = 200
	return "welcome to dCloud!"
	
