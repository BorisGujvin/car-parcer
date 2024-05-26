from typing import Optional
from .abstract import AbstractParser
from exporter import Writer
from selenium import webdriver
from model import Advertisement
import time
from bs4 import BeautifulSoup


class CarInfoParser(AbstractParser):

    def parse(self, exporter: Writer):
        print('CarInfo')
        cService = webdriver.ChromeService(executable_path='chromedriver.exe')
        self.driver = webdriver.Chrome(service=cService)
        self.exporter = exporter
        self.run()


    def run(self):
        url = 'https://www.car.info/en-se/filter'
        html = self.get_selenium(url)
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find('table', class_='cf-table sn_close_exc_xxl table mb-2 table_filter_list_small position-relative default_column_list')
        tbody = table.find('tbody')
        initial_rows = tbody.find_all('tr')
        done = 1
        for ad in initial_rows:
            a = self.normalize_ad(ad)
            if a:
                self.exporter.write(a)
            done += 1
        while True:
            new_rows = self.get_new_part(done)
            for ad in new_rows:
                a = self.normalize_ad(ad)
                if a:
                    self.exporter.write(a)
                    done += 1   
        
    def normalize_ad(self, ad) -> Optional[Advertisement]:
        if len(ad.contents) < 2:
            print('no info')
            return
        secondary = ad.contents[0] == '\n'
        href = ad.contents[1].contents[1].contents[3].attrs['href'] if secondary else ad.contents[0].contents[0].contents[1].attrs['href']
        id = href.split('-')[-1]
        name = ad.contents[1].contents[1].contents[3].contents[1].contents[0] if secondary else ad.contents[0].contents[0].contents[1].contents[0].contents[0]
        year = ad.contents[5].contents[0].replace('\n', '')  if secondary else ad.contents[2].contents[0].replace('\n', '')
        brand = name.split(' ')[0]
        city = self.get_city(ad)
        mileage = self.get_mileage(ad)
        price = self.get_price(ad)
        is_dealer = self.get_is_dealer(ad, secondary)


        return Advertisement(id=id,
                             provider='carinfo',
                             brand=brand,
                             model='',
                             name=name,
                             photo_link='',
                             year=year,
                             volume='',
                             mileage=mileage,
                             price=price,
                             is_dealer=is_dealer,
                             city=city,
                             link=href)
    
    @classmethod
    def get_price(cls, ad):
        price_wraper = ad.find('td', attrs={'data-param':'price'}).contents[0]
        try:
            price = ad.find('td', attrs={'data-param':'price'}).contents[1].contents[1].contents[0]
            a = 1
        except Exception:
            price = price_wraper
        price = str(price).replace('\n', '').replace(',', '') + ' kr'

        if price == 'kr':
            try:
                price = str(price_wraper.contents[0].contents[0]).replace('\n', '').replace(',', '') + ' kr'
            except Exception as e:
                price = ''
        return price

    @classmethod
    def get_is_dealer(cls, ad, secondary) -> bool:
        dealer_wraper = ad.find('td', attrs={'data-param':'seller'})
        dealer = str(dealer_wraper.contents[1].contents[0]).replace('\n', '') if secondary else str(dealer_wraper.contents[0].contents[0]).replace('\n', '')
        return dealer == 'Private'


    @classmethod
    def get_city(cls, ad):
        city_wraper = ad.find('td', attrs={'data-param':'city'})
        city = str(city_wraper.contents[0]).replace('\n', '')
        if city.startswith('<span'):
            city = ''
        return city

    @classmethod
    def get_mileage(cls, ad):
        mileage_wraper = ad.find('td', attrs={'data-param': 'mileage'})
        mileage = int(str(mileage_wraper.contents[0]).replace('\n', '').replace(',', ''))
        return mileage

    def get_new_part(self, done: int):
        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(1)
        html = self.driver.execute_script("return document.documentElement.outerHTML")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find('table', class_='cf-table sn_close_exc_xxl table mb-2 table_filter_list_small position-relative default_column_list')
        all_rows = table.find_all('tr')
        return all_rows[done:]


    def get_selenium(self, href):
        self.driver.get(href)
        time.sleep(1)
        return self.driver.execute_script("return document.documentElement.outerHTML")

    