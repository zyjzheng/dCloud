from lib.bottle import run, PasteServer
from app.utils.logger import DCLogger
from app.utils.config import Config
from app.api import *
import traceback

config = Config.getConfig()
logger = DCLogger.get_default_logger()
assert config != None
if logger == None:
	try:
		log_file = config['log']['log_file']
		log_level = config['log']['log_level']
		logger = DCLogger(log_file, log_level)
	except Exception, e:
		traceback.print_exc()
		logger = DCLogger()
	DCLogger.set_default_logger(logger)
assert logger != None

if __name__ == '__main__':
	logger.info("start rest api server")
	run(host='0.0.0.0', port=8888, server=PasteServer)
