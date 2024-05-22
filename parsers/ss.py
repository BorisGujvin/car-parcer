import requests
import re
from bs4 import BeautifulSoup
from exporter import Writer
from model import Advertisement
from .abstract import AbstractParcer


class SSParcer(AbstractParcer):

    root_url = 'https://www.ss.com'

    valid_brands = ['Alfa Romeo', 'Audi', 'BMW', 'Chevrolet', 'Chrysler',
                    'Citroen', 'Cupra', 'Dacia', 'Dodge', 'Fiat', 'Ford',
                    'Honda', 'Hyundai' ,'Infiniti', 'Jaguar', 'Jeep',
                    'Kia', 'Lancia','Land Rover', 'Lexus', 'Mazda', 'Mercedes', 'Mini',
                    'Mitsubishi', 'Nissan', 'Opel', 'Peugeot', 'Porsche', 'Renault',
                    'Saab', 'Seat', 'Skoda', 'Smart', 'Subaru', 'Suzuki',
                    'Toyota', 'Volkswagen', 'Volvo', 'Ваз', 'Газ', 'Другие марки']


    def get_page(self, sub_url: str, brand: str, exporter: Writer):
        print(sub_url)
        x = requests.get(self.root_url + sub_url)
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
                name = self.prepeare_str(str(columns[2].find("div").find("a").contents[0]))
                model = self.prepeare_str(str(columns[3].contents[0]))
                year = self.prepeare_str(str(columns[4].contents[0]))
                volume = self.prepeare_str(str(columns[5].contents[0]))
                mileage = self.prepeare_str(str(columns[6].contents[0]))
                try:
                    mileage = int(mileage)
                except Exception as e:
                    mileage = None
                price = self.prepeare_str(str(columns[7].contents[0]))
                current = Advertisement(id=id[3:],
                                    provider = 'ss',
                                    brand=brand,
                                    model=model,
                                    name=name,
                                    photo_link=photo,
                                    year=year,
                                    volume=volume,
                                    mileage=mileage,
                                    city='',
                                    is_dealer=False, 
                                    price=price,
                                    link='')
                if current:
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
            self.get_page(sub_url=href, brand=brand, exporter=exporter)

    def prepeare_str(self, string: str):
        return string.replace('\r', '').replace('\n', '').replace('</b>', '').replace('<b>', '').replace(';', '.,')


    def parce(self, exporter: Writer):
        x = requests.get(self.root_url + '/ru/transport/cars/')
        html = x.text
        template = r"(<a .+)href=\"(.+)\".+class=\"a_category\"[^>]+>([^<]+)"
        x = re.findall(template, html)
        for item in x:
            ref = item[1] + 'sell/'
            name = item[2]
            if name not in self.valid_brands:
                continue
            print(' ----- ' + name + ' -----')
            self.get_page(ref, name, exporter)


