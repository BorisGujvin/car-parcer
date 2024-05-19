from typing import NamedTuple, Optional
import requests
import re
from bs4 import BeautifulSoup
import time
import sys
from exporter import Writer,DBWriter, CSVWriter
from model import Advertisement

from selenium import webdriver


root_url = 'https://www.ss.com'

valid_brands = ['Alfa Romeo', 'Audi', 'BMW', 'Chevrolet', 'Chrysler',
                'Citroen', 'Cupra', 'Dacia', 'Dodge', 'Fiat', 'Ford',
                'Honda', 'Hyundai' ,'Infiniti', 'Jaguar', 'Jeep',
                'Kia', 'Lancia','Land Rover', 'Lexus', 'Mazda', 'Mercedes', 'Mini',
                'Mitsubishi', 'Nissan', 'Opel', 'Peugeot', 'Porsche', 'Renault',
                'Saab', 'Seat', 'Skoda', 'Smart', 'Subaru', 'Suzuki',
                'Toyota', 'Volkswagen', 'Volvo', 'Ваз', 'Газ', 'Другие марки']


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
            try:
                mileage = int(mileage)
            except Exception as e:
                mileage = None
            price = prepeare_str(str(columns[7].contents[0]))
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
        get_page(sub_url=href, brand=brand, exporter=exporter)

def prepeare_str(string: str):
    return string.replace('\r', '').replace('\n', '').replace('</b>', '').replace('<b>', '').replace(';', '.,')


def run_ss(exporter: Writer):
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

def run_blocket(driver, exporter: Writer, page = 1):
    
    url = 'https://www.blocket.se/bilar/sok?sortOrder=Äldst'
    if page > 1:
        url += f'&page={page}'

    html = get_selenium(driver, url)
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find('div', class_='scroll-container')
    ads = container.find_all('a')
    #ads = filter(filter_anons_link, links)
    for ad in ads:
        current = normalize_blocket_ad(ad)
        if current:
            exporter.write(current)
    next_page = soup.find('button', attrs={'aria-label': 'Nästa sida'})
    if next_page and page < 599:
        print(page)
        run_blocket(driver, exporter, page + 1)

def get_selenium(driver, href):
    driver.get(href)
    time.sleep(1)
    return driver.execute_script("return document.documentElement.outerHTML")

def normalize_blocket_ad(ad) -> Optional[Advertisement]:
    try:
        link = ad.attrs['href']
        info = ad.contents[1]
        main = info.contents[1]
        line = info.contents[0].contents[0]
        foretag = line.find_all('div', class_='shrink-0')
        is_dealer = not not foretag
        place = line.find('div', class_='TextCallout2__TextCallout2Wrapper-sc-1bir8f0-0').contents[0]
        info_list = main.find_all('li')
        year_wrap = info_list[0]
        year = int(year_wrap.contents[0].contents[0]) if year_wrap else None
        mileage_wrap = info_list[2] if len(info_list) > 2 else None
        mileage = blocket_normailize_mileage(mileage_wrap.contents[0].contents[0]) if mileage_wrap else None
        main_children = main.contents
        if len(main_children) == 2:
            name = main.contents[0].contents[0].contents[0].contents[0]
            price = main.contents[1].contents[0].contents[0].contents[0]
        elif len(main_children) == 3:
            name = main.contents[0].contents[0].contents[0].contents[0]
            price = main.contents[2].contents[0].contents[0].contents[0]
        else:
            print('wrong structure')
            return
        return Advertisement(id=blocket_get_id(link),
                            provider='blocket',
                            brand=name.split(' ')[0],
                            model='',
                            name=name,
                            photo_link='',
                            year=year,
                            volume='',
                            mileage=mileage, 
                            city=place,
                            is_dealer=is_dealer,
                            price=price,
                            link=link)
    except Exception as e:
        print('wrong data')
        return
    
def blocket_get_id(s: str) -> str:
    return s.split('/')[-1]

def blocket_normailize_mileage(s: str) -> Optional[str]:
    s = s.replace(' ', '')
    if s.endswith('mil'):
        return int(s.replace('mil', '')) * 10

if __name__ == '__main__':
    start = time.time()
    exporter = DBWriter()
    arg = sys.argv[-1]
    if arg == 'blocket':
        cService = webdriver.ChromeService(executable_path='chromedriver.exe')
        driver = webdriver.Chrome(service=cService)
        run_blocket(driver, exporter, page=1)
    elif arg == 'ss':
        run_ss(exporter)
    else:
        print('argument can be "blocket" or "ss"')
    finish = time.time()
    print (f"Time: {finish - start}")
    exporter.exit()
