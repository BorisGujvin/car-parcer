from .abstract import AbstractParcer
from exporter import Writer


class CarInfoParcer(AbstractParcer):

    def parce(self, exporter: Writer):
        print('CarInfo')