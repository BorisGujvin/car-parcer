from typing import Tuple
from exception import NeedResetException
from .abstract import AbstractParser
from exporter import Writer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from model import Advertisement
import time
from datetime import datetime
from bs4 import BeautifulSoup
import re
import json


class MobileDeParser(AbstractParser):

    def __init__(self) -> None:
        print('mobile.de')
        #cService = webdriver.ChromeService(executable_path='chromedriver.exe')
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument("--window-size=2560,1440")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.4147.125 Safari/537.36")
        self.driver = webdriver.Chrome(options=options)
        
    def parse(self, exporter: Writer):
        self.exporter = exporter
        self.run()

    def run(self):
        url = 'https://suchen.mobile.de'
        html = self.get_selenium(url)
        self.agree()
        root = BeautifulSoup(html, "html.parser")
        groups = root.find_all('div', class_='mIdDf', text='Pkw')
        
        for group in groups:
            group_name = group.contents[0]
            print(group_name)
            for brand in group.parent.find_all('a'):
                brand_name = brand.next
                url = brand.attrs['href']
                self.get_branch(url, brand_name)

    def update_info(self, url) -> tuple[str,str]:
        self.get_selenium(url)
        self.driver.delete_all_cookies()
        self.driver.refresh()
        time.sleep(4)
        show_page = self.driver.execute_script("return document.documentElement.outerHTML")
        root = BeautifulSoup(show_page, "html.parser")
        
        imgs = root.find_all('img', class_='thumbnail')
        links = [obj.attrs.get('src') or obj.attrs.get('data-lazy') for obj in imgs if obj.attrs.get('class') == ['thumbnail']]
        status = 'active'

        deleted_wraper = root.find('div', class_='vip-error__title')
        if deleted_wraper:
            text = str(deleted_wraper.contents[1].contents[0])
            if text == 'Dieses Fahrzeug ist nicht mehr verfügbar':
                status = 'closed'
            else:
                status = 'error: ' + text
        return status, json.dumps([re.sub(r'rule=mo-[\d]+.jpg', 'rule=mo-1024.jpg', link) for link in links])


    def get_selenium(self, href: str):
        self.driver.get(href)
        try:
            return self.driver.execute_script("return document.documentElement.outerHTML")
        except Exception as e:
            print(str(e))
            raise NeedResetException
    
    def get_branch(self, url: str, branch: str = 'unknown'):
        current_url = url
        html = self.get_selenium(url)
        secondary = False
        while True:
            param = [i for i in current_url.split('?')[-1].split('&') if i.startswith('pageNumber')] or ['pageNumber=1']
            page = param[0].split('=')[-1]
            print(branch + ' page: ' + page)
            root = BeautifulSoup(html, "html.parser")
            list = root.find('article', attrs={'data-testid': 'result-list-container'})
            results = list.find_all('a') if secondary else list.find_all('span')
            self.index_window = self.driver.current_window_handle
            for result in results:
                a = self.get_advertisement(result, secondary)
                if a:
                    self.exporter.write(a)
            html, current_url, secondary = self.next_page()
            if not html:
                return

    def next_page(self):
        xpath = "//button[@data-testid = 'pagination:next']"
        button_next = self.driver.find_element(By.XPATH, xpath)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", button_next)
            self.driver.execute_script("window.scrollBy(0, -100);")
            button_next.click()
            time.sleep(7)
            self.agree()
            html = self.driver.execute_script("return document.documentElement.outerHTML")
            current_url = str(self.driver.execute_script('return window.location.href'))
            secondary = True
            return html, current_url,secondary 
        except Exception:
            return None, None, None


    def get_advertisement(self, result, secondary) -> Advertisement:
        try:
            if not result.attrs['data-testid'].startswith('result-listing'):
                return
        except Exception as e:
            return
        name = result.find('h2').contents[0]
        attributes = str(result.find('div', attrs={'data-testid':'listing-details-attributes'}))
        list = self.parce_attr(attributes)
        year = list['registered']
        mileage = int(list['mileage']) if list['mileage'] else 0
        engine = 'power ' + list['power'] + 'HP' if list['power'] else ''
        price = int(result.find('span', attrs={'data-testid': 'price-label'}).contents[0][:-2].replace('.', ''))
        if secondary:
            link = str(result.attrs['href'])
            if not link.startswith('https://'):
                link = ('https://suchen.mobile.de' + link)
            if link.find('?lastSearch') > -1:
                link = link.split('?')[0]
            else:
                link = link.split('&')[0]
        else:
            ekraned_name = name.replace("'", r"\'")
            try:
                xpath = f"//h2[text()='{ekraned_name}']"    
                icon_element = self.driver.find_element(By.XPATH, xpath)
            except Exception:
                return
            parent = icon_element.find_element(By.XPATH, '../../..')
            self.driver.execute_script("arguments[0].scrollIntoView();", parent)
            parent.click()
            windows = self.driver.window_handles
            new_window = windows[-1]
            self.driver.switch_to.window(new_window)
            try:
                link = str(self.driver.execute_script('return window.location.href')).split('&')[0]
            except Exception as e:
                print(str(e))
                raise NeedResetException

            self.driver.close()
            self.driver.switch_to.window(self.index_window)

        provider_id = self.get_id(link)
        
        return Advertisement(
            provider_name='mobile.de',
            provider_id=provider_id,
            provider_link_url=link,
            brand=name.split(' ')[0],
            car_name=name,
            country='DE',
            vat_rate=19,
            price_with_vat=price,
            price_without_vat=0,
            vat=0,
            currency='EUR',
            mileage=mileage,
            images=None,
            year=year,
            engine=engine,
            is_dealer=False,
            city='unknown'
        )
    
    def agree(self):
        try:
            button_element = self.driver.find_element(By.CLASS_NAME, 'mde-consent-accept-btn')
            button_element.click()
        except:
            pass
    
    def get_id(self, link: str) -> str:
        get_param = link.split('?')[-1].split('&')[0].split('=')[-1]
        if len(get_param) < 10:
            return get_param
        last = link.split('?')[0].split('/')[-1]
        return last
    
    @classmethod
    def parce_attr(cls, attrs):
        new_car = ['Neuwagen', 'Tageszulassung']
        vehicle_types = ['SUV', 'Geländewagen', 'Pickup', 'Kombi',
                         'Jahreswagen', 'Vorführfahrzeug', 'Limousine',
                         'Kleinwagen', 'Andere']
        conditions = ['Reparierter Unfallschaden','Unfallfrei',
                      'Beschädigt']
        fuels = ['Benzin', 'Diesel']
        transmisions = ['Automatik', 'Schaltgetriebe']
        doorss = ['2/3 Türen','4/5 Türen']

        def is_register(s: str) -> bool:
           return s.startswith('EZ') or s in new_car
       
        def is_mileage(s: str) -> bool:
           return s.endswith('km')     
        def is_power(s:str) -> bool:
           return  s.find('kW') > -1
        def is_vehicle_type(s:str) -> bool:
           first = s.split(' / ')[0]
           return first in vehicle_types
        def is_condition(s:str) -> bool:
           return s in conditions
        def is_fuel(s:str) -> bool:
           return s in fuels
        def is_transmision(s:str) -> bool:
           return s in transmisions
        def is_status(s:str) -> bool:
           return s.startswith('HU')
        def is_doors(s:str) -> bool:
           return s in doorss
        def get_register(s:str) -> str:
            if s in new_car:
                return str(datetime.now().year)
            return s.split('/')[-1]
        def get_mileage(s:str) -> str:
            return s.replace('.', '').replace(' km', '')
        def get_power(s:str) -> str:
            search = re.search(r'\((.+)PS\)', s)
            if search:
                return search.group(1)
        def get_vehicle_type(s:str) -> str:
            return s
        def get_condition(s:str) -> str:
            return s
        def get_fuel(s:str) -> str:
            return s
        def get_transmision(s:str) -> str:
            return s
        def get_status(s:str) -> str:
            return s
        def get_doors(s:str) -> str:
            return s


        info = {}
        variables = {
            0: ('registered', is_register, get_register) ,
            1: ('mileage', is_mileage, get_mileage),
            2: ('power', is_power, get_power),
            3: ('vehicle_type', is_vehicle_type, get_vehicle_type),
            4: ('condition', is_condition, get_condition),
            5: ('fuel', is_fuel, get_fuel),
            6: ('transmision', is_transmision, get_transmision),
            7: ('status', is_status, get_status),
            8: ('doors', is_doors, get_doors),
            # l/100 km, Co2, CO2class
        }
        tmp = re.sub(r'<[^>]+>', '', attrs.replace('</div>', ' • ')).replace('\xa0', ' ').split(' • ')
        var_no = 0
        for found in tmp:
            if not found:
                continue
            next = False
            name, check, geter = variables[var_no]
            while not next:
                if check(found):
                    info[name] = geter(found)
                    var_no += 1
                    next = True
                else:
                    info[name] = None
                    var_no += 1
                    if var_no < len(variables):
                        name, check, geter = variables[var_no]
                    else:
                        next = True
            if var_no >= len(variables):
                info['error'] = attrs
                break
        return info
    