class AdvertisementTable:

    NAME = 'advertisements'

    class Columns:
        ID = 'id'
        PROVIDER = 'provider'
        BRAND = 'brand'
        MODEL = 'model'
        NAME = 'name'
        PHOTO_LINK = 'photo_link'
        YEAR = 'year'
        VOLUME = 'volume'
        MILEAGE = 'mileage'
        PRICE = 'price'
        IS_DEALER = 'is_dealer'
        CITY = 'city'
        LINK = 'link'

    COLUMN_KEYS = [v for n, v in vars(Columns).items() if not n.startswith('_')]
    