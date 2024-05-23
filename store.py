from model import Advertisement
from datetime import datetime


class AdvertisementStore:
    def __init__(self, connection) -> None:
        self.connection = connection

    def create(self, a: Advertisement):   
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

    def search(self, a: Advertisement):
        template = f"SELECT id FROM leads WHERE provider_name ='{a.provider_name}' AND provider_id = '{a.provider_id}'"
        with self.connection.cursor() as cursor:
            cursor.execute(template)
            result = cursor.fetchone()
            return result[0] if result else None

    def mark_active(self, a: Advertisement):
        template = f"UPDATE leads SET active_at = '{datetime.now()}' WHERE provider_name ='{a.provider_name}' AND provider_id = '{a.provider_id}'"
        with self.connection.cursor() as cursor:
            cursor.execute(template)
            self.connection.commit()
