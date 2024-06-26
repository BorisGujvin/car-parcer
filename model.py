from typing import NamedTuple, Optional

class Advertisement(NamedTuple):
    provider_name: str
    provider_id: str
    id: Optional[str] = None
    provider_link_url: Optional[str] = None
    brand: Optional[str] = None
    car_name: Optional[str] = None
    country: Optional[str] = None
    vat_rate: Optional[int] = None
    price_with_vat: Optional[float] = None
    price_without_vat: Optional[float] = None
    vat: Optional[float] = None
    currency: Optional[str] = None
    mileage: Optional[int] = None
    images: Optional[str] = None
    year: Optional[str] = None
    engine: Optional[str] = None
    seller_is_private: Optional[bool] = None
    seller: Optional[str] = None
    is_dealer: Optional[bool] = None
    city: Optional[str] = None


class UpdateAdRequest(NamedTuple):
    url: Optional[str] = None
    status: Optional[str] = None
    images: Optional[str] = None
    is_dealer: Optional[str] = None
    transmission: Optional[str] = None
    fuel: Optional[str] = None
    first_reg: Optional[str] = None
    color: Optional[str] = None
