from exporter import Writer, DBWriter, CSVWriter
from parsers.blocket import BlocketParcer
from parsers.ss import SSParcer
from parsers.carinfo import CarInfoParcer
import time
import sys


if __name__ == '__main__':
    start = time.time()
    exporter = CSVWriter()
    arg = sys.argv[-1]
    if arg == 'blocket':
        parcer = BlocketParcer()
    elif arg == 'ss':
        parcer = SSParcer()
    elif arg == 'carinfo':
        parcer = CarInfoParcer()
    else:
        print('argument can be "blocket" or "ss"')
        exit
    parcer.parce(exporter=exporter)
    finish = time.time()
    print (f"Time: {finish - start}")
    exporter.exit()