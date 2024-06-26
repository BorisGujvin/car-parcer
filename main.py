from exporter import Writer, CSVWriter, MySQLWriter
from parsers.blocket import BlocketParser
from parsers.ss import SSParcer
from parsers.carinfo import CarInfoParser
from parsers.mobile_de import MobileDeParser
import time
import sys
from exception import NeedResetException

if __name__ == '__main__':
    arg = sys.argv[-1]
    if arg == 'main.py':
        arg = 'mobile.de'
    while True:
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
        try:
            exporter = MySQLWriter()
            start = time.time()
            parser.parse(exporter=exporter)
            finish = time.time()
            exporter.exit()
        except NeedResetException:
            print('TimeOut Exception')
            continue
        except Exception as e:
            print(e)
            continue
        print('successfully finished')
        print (f"Time: {finish - start}")
