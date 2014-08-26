import os

class SysUtils:
	@staticmethod
	def getResult(result):
		if result is not None:
			if isinstance(result, list):
				if len(result) >2:
					return result[0], result[1]
				elif len(result) == 1:
					return '', result[0]
				else:
					return '', ''
			else:
				return '', result
		else:
			raise Exception('no result returned')

	@staticmethod
	def run_cmd(cmd):
		status = os.system(cmd)
		status = status >> 8
		return status
