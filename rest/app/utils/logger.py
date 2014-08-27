import logging, os, inspect

class DCLogger:
	default_logger = None

	def __init__(self, path = None, level = None):
		self.logger = logging.getLogger()
		if path == None:
			if os.path.exists(path):
				self.handler = logging.FileHandler(path)
				formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
				self.handler.setFormatter(formatter)
		if level == 'INFO':
			self.logger.setLevel(logging.INFO)
		elif level == 'WARNING':
			self.logger.setLevel(logging.WARNING)
		elif level == 'DEBUG':
			self.logger.setLevel(logging.DEBUG)
		else:
			self.logging.setLevel(logging.INFO)

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
