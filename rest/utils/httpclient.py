import httplib, base64
import logging
import traceback

class HttpClient():
    http_host = "localhost"
    http_port = ""
    endpoint = ""
    conn = None
    
    def __init__(self, host = None, port = None, logger = None):
        if logger is not None:
            self.logger = logger
        else:
            self.logger = logging.getLogger()

        if host is not None:
            self.http_host = host
        if port is not None:
            self.http_port = port
            self.endpoint = (self.http_host + ":" + str(self.http_port)).lower()
        else:
            self.endpoint = (self.http_host).lower()
        if self.endpoint.startswith("https"):
            conn_url =  self.endpoint.replace("https://", "")
            self.conn = httplib.HTTPSConnection(conn_url)
        elif self.endpoint.startswith("http"):
            conn_url =  self.endpoint.replace("http://", "")
            print conn_url
            self.conn = httplib.HTTPConnection(conn_url)
        else:
            conn_url =  self.endpoint
            self.conn = httplib.HTTPConnection(conn_url)
    
    def __restart_connection(self):
        if self.endpoint.startswith("https"):
            conn_url =  self.endpoint.replace("https://", "")
            self.conn = httplib.HTTPSConnection(conn_url)
        elif self.endpoint.startswith("http"):
            conn_url =  self.endpoint.replace("http://", "")
            print conn_url
            self.conn = httplib.HTTPConnection(conn_url)
        else:
            conn_url =  self.endpoint
            self.conn = httplib.HTTPConnection(conn_url)

    def __del__(self):
        if self.conn is not None:
            self.conn.close();
            
    def close(self):
        if self.conn is not None:
            self.conn.close();
    
    def get_request(self, url, header = {}):
        try:
            self.conn.request('GET', url, '', header)
            result=self.conn.getresponse()  
            status=result.status
            print(status)
            content=result.read()
            print(content)
            header = result.getheaders()
            result.close()
            return [status, content, header]
        except Exception, e:
            self.__restart_connection()
            traceback.print_exc()
            self.logger.error("send GET reqeust error: %s" % e)
            return None        
        
    def post_request(self, url, body = '', header = {}):
        print url,body,header
        try:
            self.conn.request('POST', url, body, header)
            result=self.conn.getresponse()
            status=result.status
            print(status)
            content=result.read()
            print(content)
            header = result.getheaders()
            result.close()
            return [status, content, header]
        except Exception, e:
            self.__restart_connection()
            traceback.print_exc()
            self.logger.error("send POST reqeust error: %s" % e)
            return None        
    
    def put_request(self, url, body = '', header = {}):
        try:
            self.conn.request('PUT', url, body, header)
            result=self.conn.getresponse()
            status=result.status
            content=result.read()
            header = result.getheaders()
            result.close()
            return [status, content, header]
        except Exception, e:
            self.__restart_connection()
            traceback.print_exc()
            self.logger.error("send PUT reqeust error: %s" % e)
            return None
    
    def del_request(self, url, header = {}): 
        try:
            self.conn.request('DELETE', url,'', header)
            result=self.conn.getresponse()
            status=result.status
            content=result.read()
            header = result.getheaders()
            result.close()
            return [status, content, header]
        except Exception, e:
            self.__restart_connection()
            traceback.print_exc()
            self.logger.error("send DELETE reqeust error: %s" % e)
            return None
    
