import ConfigParser

config = ConfigParser.ConfigParser()
config.readfp(open("./config/dCloud.conf", "r"))

class Config:
    @staticmethod
    def get(key, section="Default"):
        return config.get(section, key)

if __name__ == '__main__':
    print Config.get("zk.url")
    print Config.get("etcd.host")
    print Config.get("etcd.port")
