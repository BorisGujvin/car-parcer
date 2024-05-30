from abc import ABC
import pymysql
import paramiko
from sshtunnel import SSHTunnelForwarder
from model import Advertisement
from store import AdvertisementStore
from db_connection import get_connection

class Writer(ABC):
    def write(self, a: Advertisement) -> None:
        pass
    def exit(self) -> None:
        pass 


class CSVWriter(Writer):
    def __init__(self):
        self.export_file = open("data.csv", 'w', encoding="utf-8")

    def exit(self):
        self.export_file.close()

    def write(self, a: Advertisement) -> None:
        csv_row = ';'.join([
            a.provider_id,
            a.provider_name,
            'true' if a.is_dealer else 'false',
            a.city, a.brand,
            a.car_name,
            a.provider_link_url,
            a.images,
            str(a.year),
            a.engine,
            str(a.mileage),
            str(a.price_with_vat),
            '\n'])
        self.export_file.write(csv_row)

class MySQLWriter(Writer):
    def __init__(self):
        self.connection = get_connection()
        self.store = AdvertisementStore(self.connection)
    def exit(self) -> None:
        self.connection.close()

    def write(self, a: Advertisement) -> None:
        if self.store.search(a=a):
            print(a.provider_id + ' exist')
        else:
            self.store.create(a=a)
            print(a.provider_id + ' created')

    
            