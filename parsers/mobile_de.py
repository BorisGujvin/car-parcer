from .abstract import AbstractParcer
from exporter import Writer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from model import Advertisement
import time
from bs4 import BeautifulSoup
import re


class MobileDeParcer(AbstractParcer):

    def parce(self, exporter: Writer):
        print('mobile.de')
        cService = webdriver.ChromeService(executable_path='chromedriver.exe')
        options = Options()
        options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(service=cService, options=options)
        self.exporter = exporter
        self.run()


    def run(self):
        url = 'https://suchen.mobile.de'
        html = self.get_selenium(url)
        button_element = self.driver.find_element(By.CLASS_NAME, 'mde-consent-accept-btn')
        button_element.click()
        root = BeautifulSoup(html, "html.parser")
        groups = root.find_all('div', class_='D5nyu')
        for group in groups:
            group_name = group.contents[0].contents[0]
            print(group_name)
            for brand in group.find_all('a'):
                brand_name = brand.next
                url = brand.attrs['href']
                print('     ' + brand_name)
                self.get_branch(url)

    def get_selenium(self, href):
        self.driver.get(href)
        time.sleep(1)
        return self.driver.execute_script("return document.documentElement.outerHTML")
    
    def get_branch(self, url: str):
        print(url)
        html = self.get_selenium(url)
        root = BeautifulSoup(html, "html.parser")
        list = root.find('article', attrs={'data-testid': 'result-list-container'})
        results = list.find_all('span')
        self.index_window = self.driver.current_window_handle
        for result in results:
            a = self.normalize(result)
            if a:
                self.exporter.write(a)

    def get_advertisement(self, result) -> Advertisement:
        try:
            if not result.attrs['data-testid'].startswith('result-listing'):
                return
        except Exception as e:
            return
        name = result.find('h2').contents[0]
        attributes = str(result.find('div', attrs={'data-testid':'listing-details-attributes'}))
        list = self.parce_attr(attributes)
        year = list['registered']
        mileage = int(list['mileage'])
        engine = 'power ' + list['power'] + 'HP'
        price = int(result.find('span', attrs={'data-testid': 'price-label'}).contents[0][:-2].replace('.', ''))

        xpath = f"//h2[text()=\"{name}\"]"
        icon_element = self.driver.find_element(By.XPATH, xpath)
        parent = icon_element.find_element(By.XPATH, '../../..')
        self.driver.execute_script("arguments[0].scrollIntoView();", parent)
        parent.click()
        windows = self.driver.window_handles
        new_window = windows[-1]
        self.driver.switch_to.window(new_window)
        link = self.driver.execute_script('return window.location.href')
        self.driver.close()
        self.driver.switch_to.window(self.index_window)

        return Advertisement(
            provider_name='mobile.de',
            provider_id=self.get_id(link),
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
            images='{}',
            year=year,
            engine=engine,
            is_dealer=False,
            city='unknown'
        )
    
    def get_id(self, link: str) -> str:
        return link.split('?')[-1].split('&')[0].split('=')[-1]
    
    @classmethod
    def parce_attr(cls, attrs):

        vehicle_types = ['SUV', 'Geländewagen', 'Pickup', 'Kombi',
                         'Jahreswagen', 'Vorführfahrzeug', 'Limousine']
        conditions = ['Reparierter Unfallschaden','Unfallfrei',
                      'Beschädigt']
        fuels = ['Benzin', 'Diesel']
        transmisions = ['Automatik', 'Schaltgetriebe']
        doorss = ['2/3 Türen','4/5 Türen']

        def is_register(s: str) -> bool:
           return s.startswith('EZ') or s == 'Tageszulassung'
       
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
            if var_no >= len(variables):
                info['error'] = attrs
                break
        return info
        