from abc import ABC
from advertisement import AdvertisementTable
from psycopg2 import sql, connect
import pymysql
import paramiko
from sshtunnel import SSHTunnelForwarder
from paramiko import SSHClient
from model import Advertisement
from datetime import datetime

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
        csv_row = ';'.join([a.provider_id, a.provider_name, 'true' if a.is_dealer else 'false', a.city, a.brand, a.model, a.name, a.link, a.photo_link,
                            str(a.year), a.engine, str(a.mileage), a.price_with_vat, '\n'])
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
        template = "SELECT * from leads"
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
        cursor = self.connection.cursor()
        cursor.execute(template)
        result = cursor.fetchone()
        a=1   

    def exit(self) -> None:
        self.connection.close()

    def write(self, a: Advertisement) -> None: 
        template = ("""INSERT INTO leads (
                    provider_name, 
                    provider_id,
                    provider_lead_url,
                    brand,
                    car_name,
                    country,
                    vat_rate,
                    price_with_vat,
                    price_without_vat,
                    vat,
                    currency,
                    mileage_km,
                    images,
                    year,
                    engine,
                    is_dealer,
                    city,
                    created_at,
                    active_at
                ) VALUES (
                    %(provider_name)s,
                    %(provider_id)s,
                    %(provider_lead_url)s,
                    %(brand)s,
                    %(car_name)s,
                    %(country)s,
                    %(vat_rate)s,
                    %(price_with_vat)s,
                    %(price_without_vat)s,
                    %(vat)s,
                    %(currency)s,
                    %(mileage)s,
                    %(images)s,
                    %(year)s,
                    %(engine)s,
                    %(is_dealer)s,
                    %(city)s,
                    %(created_at)s,
                    %(active_at)s
                )""")
        values = {'provider_name':a.provider_name, 
                  'provider_id': str(a.provider_id),
                  'provider_lead_url': a.provider_link_url,
                  'brand': a.brand,
                  'car_name': a.car_name,
                  'country': a.country,
                  'vat_rate': a.vat_rate,
                  'price_with_vat': a.price_with_vat,
                  'price_without_vat': a.price_without_vat,
                  'vat': a.vat,
                  'currency': a.currency,
                  'mileage': a.mileage,
                  'images': a.images,
                  'year': a.year,
                  'engine': a.engine,
                  'is_dealer': a.is_dealer,
                  'city': a.city,
                  'created_at': datetime.now(),
                  'active_at': datetime.now()}
        with self.connection.cursor() as cursor:
            cursor.execute(template, values)
            self.connection.commit()
        