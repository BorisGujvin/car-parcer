from exporter import Writer, PostgreDBWriter, CSVWriter, MySQLWriter
from parsers.blocket import BlocketParcer
from parsers.ss import SSParcer
from parsers.carinfo import CarInfoParcer
from parsers.mobile_de import MobileDeParcer
import time
import sys
from model import Advertisement


if __name__ == '__main__':
    start = time.time()
    exporter = MySQLWriter()

    arg = sys.argv[-1]
    if arg == 'blocket':
        parcer = BlocketParcer()
    elif arg == 'ss':
        parcer = SSParcer()
    elif arg == 'carinfo':
        parcer = CarInfoParcer()
    elif arg == 'mobile.de':
        parcer = MobileDeParcer()
    else:
        print('argument can be "blocket" or "ss" or "carinfo" or "mobile.de"')
        exit()
    parcer.parce(exporter=exporter)
    finish = time.time()
    print (f"Time: {finish - start}")
    exporter.exit()