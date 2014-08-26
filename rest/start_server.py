from lib.bottle import run, PasteServer
from api import *

if __name__ == '__main__':
	run(host='0.0.0.0', port=8888, server=PasteServer)