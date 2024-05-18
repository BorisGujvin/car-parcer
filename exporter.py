from abc import ABC
from advertisement import AdvertisementTable
from psycopg2 import sql, connect
from model import Advertisement

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
        csv_row = ';'.join([a.id, a.provider, 'true' if a.is_dealer else 'false', a.city, a.brand, a.model, a.name, a.link, a.photo_link,
                            str(a.year), a.volume, str(a.mileage), a.price, '\n'])
        self.export_file.write(csv_row)


class DBWriter(Writer):
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
        values = [a.id, a.provider, a.brand, a.model, a.name, a.photo_link, a.year, a.volume, a.mileage,
                  a.price, 1 if a.is_dealer else 0, a.city, a.link]
        keys_sql = sql.SQL(', ').join(map(sql.Identifier, keys))
        values_sql = sql.SQL(', ').join(map(sql.Literal, values))
        statement = sql.SQL(template).format(keys_sql, values_sql)
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement)
        