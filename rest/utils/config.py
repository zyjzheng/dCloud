import json
import os, inspect

cur_dir = os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0])

class Config:
	config = None
	@staticmethod
	def getConfig(path = None):
		if Config.config == None:
			if path == None or not os.path.exists(path):
				default_path = cur_dir + "/../config/dCloud.json"
				config_file = file(default_path)
				Config.config = json.load(config_file)
			else:
				config_file = file(path)
				Config.config = json.load(config_file)
		return Config.config
			


