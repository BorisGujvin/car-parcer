from typing import Optional
from .abstract import AbstractParcer
from exporter import Writer
from selenium import webdriver
import time
from model import Advertisement
from bs4 import BeautifulSoup



class BlocketParcer(AbstractParcer):

    def parce(self, exporter: Writer):
        cService = webdriver.ChromeService(executable_path='chromedriver.exe')
        self.driver = webdriver.Chrome(service=cService)
        self.exporter = exporter
        self.run()

    def run(self, page = 1):
        
        url = 'https://www.blocket.se/bilar/sok' #?sortOrder=Äldst'
        if page > 1:
            url += f'&page={page}'

        html = self.get_selenium(url)
        soup = BeautifulSoup(html, "html.parser")
        container = soup.find('div', class_='scroll-container')
        ads = container.find_all('a')
        for ad in ads:
            current = self.normalize_ad(ad)
            if current:
                self.exporter.write(current)
        next_page = soup.find('button', attrs={'aria-label': 'Nästa sida'})
        if next_page and page < 599:
            print(page)
            self.run(page + 1)

    def get_selenium(self, href):
        self.driver.get(href)
        time.sleep(1)
        return self.driver.execute_script("return document.documentElement.outerHTML")

    def normalize_ad(self, ad) -> Optional[Advertisement]:
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
            mileage = self.normailize_mileage(mileage_wrap.contents[0].contents[0]) if mileage_wrap else None
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
            return Advertisement(id=self.get_id(link),
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
        
    def get_id(self, s: str) -> str:
        return s.split('/')[-1]

    def normailize_mileage(self, s: str) -> Optional[str]:
        s = s.replace(' ', '')
        if s.endswith('mil'):
            return int(s.replace('mil', '')) * 10

