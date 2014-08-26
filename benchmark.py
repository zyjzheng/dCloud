from dcloud.monster.monster import Monster
from dcloud.utils.log import logger
import time


if __name__ == '__main__':
    monster = Monster()
    try:
        monster.start()
        while True:
            time.sleep(5)
    except KeyboardInterrupt, ki:
        logger.info("Benchmark stopping")
        monster.stop()
