from abc import ABC
from exporter import Writer

class AbstractParcer(ABC):
    def parce(self, exporter: Writer):
        pass