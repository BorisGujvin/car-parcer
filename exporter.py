from abc import ABC
import pymysql
import paramiko
from sshtunnel import SSHTunnelForwarder
from model import Advertisement
from store import AdvertisementStore

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
        mypkey = paramiko.RSAKey.from_private_key_file('C:/Users/think/.ssh/id_rsa', 'K0r0stel!')
        self.tunnel = SSHTunnelForwarder(('68.183.217.93', 22),
            ssh_username='forge',
            ssh_pkey=mypkey,
            remote_bind_address=('127.0.0.1', 3306)
        )
        self.tunnel.start()
        self.connection = pymysql.connect(
            host='127.0.0.1',
            user='forge',
            passwd='nSvGDEPZwsE625VhpPco', db='forge',
            port=self.tunnel.local_bind_port
        )
        self.store = AdvertisementStore(self.connection)

    def exit(self) -> None:
        self.connection.close()

    def write(self, a: Advertisement) -> None:
        if self.store.search(a=a):
            self.store.mark_active(a=a)
            print(a.provider_id + ' updated')
        else:
            self.store.create(a=a)
            print(a.provider_id + ' created')

    
            