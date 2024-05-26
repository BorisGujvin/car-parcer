from exporter import Writer, PostgreDBWriter, CSVWriter, MySQLWriter
from parsers.blocket import BlocketParser
from parsers.ss import SSParcer
from parsers.carinfo import CarInfoParser
from parsers.mobile_de import MobileDeParser
import time
import sys
from model import Advertisement


if __name__ == '__main__':
    arg = sys.argv[-1]
    if arg == 'blocket':
        parser = BlocketParser()
    elif arg == 'ss':
        parser = SSParcer()
    elif arg == 'carinfo':
        parser = CarInfoParser()
    elif arg == 'mobile.de':
        parser = MobileDeParser()
    else:
        print('argument can be "blocket" or "ss" or "carinfo" or "mobile.de"')
        exit()
    while True:
        exporter = MySQLWriter()
        start = time.time()
        parser.parse(exporter=exporter)
        finish = time.time()
        print (f"Time: {finish - start}")
        exporter.exit()