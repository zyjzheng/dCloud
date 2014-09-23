import logging, os, inspect

class DCLogger:
	default_logger = None

	def __init__(self, path = None, level = None):
		self.logger = logging.getLogger()
		if path != None:
			log_dir = os.path.split(path)[0]
			if os.path.exists(log_dir):
				self.handler = logging.FileHandler(path)
				formatter = logging.Formatter('%(name)-12s %(asctime)s  %(filename)s[line:%(lineno)d] %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S')
				self.handler.setFormatter(formatter)
				self.logger.addHandler(self.handler)
		if level == 'INFO':
			self.logger.setLevel(logging.INFO)
		elif level == 'WARNING':
			self.logger.setLevel(logging.WARNING)
		elif level == 'DEBUG':
			self.logger.setLevel(logging.DEBUG)
		else:
			self.logger.setLevel(logging.INFO)

	@staticmethod
	def set_default_logger(dclogger):
		DCLogger.default_logger = dclogger
	
	@staticmethod
	def get_default_logger():
		return DCLogger.default_logger

	def info(self, message):
		self.logger.info(message)

	def debug(self, message):
		self.logger.debug(message)

	def error(self, message):
		self.logger.error(message)

	def warning(self, message):
		self.logger.warning(message)

	def critical(self, message):
		self.logger.critical(message)
