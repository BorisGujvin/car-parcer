from typing import NamedTuple, Optional
from abc import ABC
import requests
from psycopg2 import sql, connect
import re
from bs4 import BeautifulSoup
import time


root_url = 'https://www.ss.com'

valid_brands = ['Alfa Romeo', 'Audi', 'BMW', 'Chevrolet', 'Chrysler',
                'Citroen', 'Cupra', 'Dacia', 'Dodge', 'Fiat', 'Ford',
                'Honda', 'Hyundai' ,'Infiniti', 'Jaguar', 'Jeep',
                'Kia', 'Lancia','Land Rover', 'Lexus', 'Mazda', 'Mercedes', 'Mini',
                'Mitsubishi', 'Nissan', 'Opel', 'Peugeot', 'Porsche', 'Renault',
                'Saab', 'Seat', 'Skoda', 'Smart', 'Subaru', 'Suzuki',
                'Toyota', 'Volkswagen', 'Volvo', 'Ваз', 'Газ', 'Другие марки']


class Advertisement(NamedTuple):
    id: str
    brand: Optional[str] = None
    model: Optional[str] = None
    name: Optional[str] = None
    photo_link: Optional[str] = None
    year: Optional[str] = None
    volume: Optional[str] = None
    mileage: Optional[int] = None
    price: Optional[str] = None


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
        csv_row = ';'.join([a.id, a.brand, a.model, a.name, a.photo_link,
                            a.year, a.volume, a.mileage, a.price, '\n'])
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
        keys = ['id', 'brand', 'model', 'name', 'photo_link', 'year', 'volume', 'mileage', 'price']
        values = [a.id, a.brand, a.model, a.name, a.photo_link, a.year, a.volume, a.mileage, a.price]
        keys_sql = sql.SQL(', ').join(map(sql.Identifier, keys))
        values_sql = sql.SQL(', ').join(map(sql.Literal, values))
        statement = sql.SQL(template).format(keys_sql, values_sql)
        with self.connection as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement)



def get_page(sub_url: str, brand: str, exporter: Writer):
    print(sub_url)
    x = requests.get(root_url + sub_url)
    html = x.text
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr", id=True)
    for row in rows:
        id = row["id"]
        if "tr_" in id:
            columns = row.find_all("td")
            if len(columns) < 8:
                continue
            photo = str(columns[1].find("a").contents[0]['src']) 
            name = prepeare_str(str(columns[2].find("div").find("a").contents[0]))
            model = prepeare_str(str(columns[3].contents[0]))
            year = prepeare_str(str(columns[4].contents[0]))
            volume = prepeare_str(str(columns[5].contents[0]))
            mileage = prepeare_str(str(columns[6].contents[0]))
            price = prepeare_str(str(columns[7].contents[0]))
            current = Advertisement(id=id[3:],
                                  brand=brand,
                                  model=model,
                                  name=name,
                                  photo_link=photo,
                                  year=year,
                                  volume=volume,
                                  mileage=mileage, price=price)
            exporter.write(current)
    navi = soup.find_all("a", class_='navi')
    for button in navi:
        attributes = button.attrs
        rel  = attributes['rel']
        text = str(button.contents[0])
        if ('next' not in rel) or len(text) < 5:
            continue
        href = attributes['href']
        next_page = href.split('/')[-1]
        if not next_page.startswith('page'):
            continue
        get_page(sub_url=href, brand=brand, exporter=exporter)

def prepeare_str(string: str):
    return string.replace('\r', '').replace('\n', '').replace('</b>', '').replace('<b>', '').replace(';', '.,')


def run():
    start = time.time()
    # exporter = CSVWriter()
    exporter = DBWriter()

    x = requests.get(root_url + '/ru/transport/cars/')
    html = x.text
    template = r"(<a .+)href=\"(.+)\".+class=\"a_category\"[^>]+>([^<]+)"
    x = re.findall(template, html)
    for item in x:
        ref = item[1] + 'sell/'
        name = item[2]
        if name not in valid_brands:
            continue
        print(' ----- ' + name + ' -----')
        get_page(ref, name, exporter)
    finish = time.time()
    print (f"Time: {finish - start}")
    exporter.exit()

if __name__ == '__main__':
    run()