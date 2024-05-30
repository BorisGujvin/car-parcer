from typing import Optional
from model import Advertisement, UpdateAdRequest
from datetime import datetime


class AdvertisementStore:
    def __init__(self, connection) -> None:
        self.connection = connection

    def create(self, a: Advertisement):   
        template = ("""INSERT INTO ads (
                    provider_name, 
                    provider_id,
                    provider_lead_url,
                    brand,
                    car_name,
                    country,
                    price,
                    currency,
                    mileage_km,
                    images,
                    year,
                    engine,
                    created_at,
                    active_at
                ) VALUES (
                    %(provider_name)s,
                    %(provider_id)s,
                    %(provider_lead_url)s,
                    %(brand)s,
                    %(car_name)s,
                    %(country)s,
                    %(price_with_vat)s,
                    %(currency)s,
                    %(mileage)s,
                    %(images)s,
                    %(year)s,
                    %(engine)s,
                    %(created_at)s,
                    %(active_at)s
                )""")
        values = {'provider_name':a.provider_name, 
                'provider_id': str(a.provider_id),
                'provider_lead_url': a.provider_link_url,
                'brand': a.brand,
                'car_name': a.car_name,
                'country': a.country,
                'price_with_vat': a.price_with_vat,
                'currency': a.currency,
                'mileage': a.mileage,
                'images': a.images,
                'year': a.year,
                'engine': a.engine,
                'created_at': datetime.now(),
                'active_at': datetime.now()}
        with self.connection.cursor() as cursor:
            cursor.execute(template, values)
            self.connection.commit()

    def search(self, a: Advertisement):
        template = f"SELECT id FROM ads WHERE provider_name ='{a.provider_name}' AND provider_id = '{a.provider_id}'"
        with self.connection.cursor() as cursor:
            cursor.execute(template)
            result = cursor.fetchone()
            return result[0] if result else None

    def mark_active(self, a: Advertisement):
        template = f"UPDATE ads SET active_at = '{datetime.now()}' WHERE provider_name ='{a.provider_name}' AND provider_id = '{a.provider_id}'"
        with self.connection.cursor() as cursor:
            cursor.execute(template)
            self.connection.commit()

    def get_tasks(self):
        template1 = "SELECT provider_lead_url FROM ads WHERE images IS NULL LIMIT 10"
        with self.connection.cursor() as cursor:
            cursor.execute(template1)
            result = cursor.fetchall()
            result = [r[0] for r in result] if result else None
            if not result or len(result) < 10:
                return
            template2 = f"UPDATE ads SET images = '[]' WHERE provider_lead_url IN ('{'\', \''.join(result)}')"        
            cursor.execute(template2)
            self.connection.commit()
        return result
        

    def get_old_tasks(self):
        template1 = "SELECT provider_lead_url FROM ads WHERE status = 'active' order by active_at LIMIT 10"
        with self.connection.cursor() as cursor:
            cursor.execute(template1)
            result = cursor.fetchall()
            result = [r[0] for r in result] if result else None
            if not result or len(result) < 10:
                return
            template2 = f"UPDATE ads SET status = 'checking' WHERE provider_lead_url IN ('{'\', \''.join(result)}')"        
            cursor.execute(template2)
            self.connection.commit()
        return result

    def update_lead(self, request: list[UpdateAdRequest]):
        with self.connection.cursor() as cursor:
            for row in request:
                data = ''
                if row.status:
                    data += f"status = '{row.status}', "
                if row.images:
                    data += f"images = '{row.images}', "
                data += f"is_dealer = {1 if row.is_dealer else 0 }, "
                if row.transmission:
                    data += f"transmission = '{row.transmission}', "
                if row.fuel:
                    data += f"fuel = '{row.fuel}', "
                if row.first_reg:
                    data += f"first_reg = '{row.first_reg}', "
                if row.color:
                    data += f"color = '{row.color}', "

                template = f"UPDATE ads SET {data}active_at = '{datetime.now()}' WHERE provider_lead_url ='{row.url}'"
            
                cursor.execute(template)
        self.connection.commit()
