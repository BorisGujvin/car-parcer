from abc import ABC
from exporter import Writer

class AbstractParser(ABC):
    def parse(self, exporter: Writer):
        pass