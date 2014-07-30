import logging

#LOG_FILE="/tmp/install.log"
logger = logging.getLogger()  
#fileHandler = logging.FileHandler(LOG_FILE)

consoleHandler = logging.StreamHandler()
#logger.addHandler(fileHandler) 
logger.addHandler(consoleHandler) 
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
#fileHandler.setFormatter(formatter)
consoleHandler.setFormatter(formatter)
#set log level  
logger.setLevel(logging.INFO)  
