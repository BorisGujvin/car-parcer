from abc import ABC
from advertisement import AdvertisementTable
from psycopg2 import sql, connect
import pymysql
import paramiko
from sshtunnel import SSHTunnelForwarder
from paramiko import SSHClient
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


class PostgreDBWriter(Writer):
    def __init__(self):
        self.connection = connect(
            host='localhost',
            user='postgres',
            password=''
        )

    def exit(self) -> None:
        pass

    def write(self, a: Advertisement) -> None:
        template = f"""INSERT INTO advertisements ({{}}) VALUES ({{}}) ON CONFLICT DO NOTHING"""
        keys = AdvertisementTable.COLUMN_KEYS
        values = [a.provider_id, a.provider_name, a.brand, a.car_name, a.year, a.mileage,
                  a.price, 1 if a.is_dealer else 0, a.city, a.link]
        keys_sql = sql.SQL(', ').join(map(sql.Identifier, keys))
        values_sql = sql.SQL(', ').join(map(sql.Literal, values))
        statement = sql.SQL(template).format(keys_sql, values_sql)
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement)

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
            print('updated:' + a.provider_id)
            self.store.mark_active(a=a)
        else:
            print('created:' + a.provider_id)
            self.store.create(a=a)

    
            