import argparse
import traceback
from influxdb import InfluxDBClient


def main(host='localhost', port=8086):
    user = 'root'
    password = 'root'
    dbname = 'cadvisor'
    dbuser = 'root'
    dbuser_password = 'root'
    query_stats = 'DELETE FROM stats WHERE time < now() - 2h;'
    query_check_data = 'DELETE FROM check_data WHERE time < now() - 2h;'

    client = InfluxDBClient(host, port, user, password, dbname,timeout=10)
    try:
        result = client.query(query_stats)
    except Exception,e:
        traceback.print_exc()
    try:
        result = client.query(query_check_data)
    except Exception,e:
        traceback.print_exc()



def parse_args():
    parser = argparse.ArgumentParser(
        description='example code to play with InfluxDB')
    parser.add_argument('--host', type=str, required=True)
    parser.add_argument('--port', type=int, required=True)
    return parser.parse_args()


if __name__ == '__main__':
    main('9.181.27.234', 8086)
