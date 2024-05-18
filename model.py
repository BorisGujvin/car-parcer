from typing import NamedTuple, Optional

class Advertisement(NamedTuple):
    id: str
    provider: str
    brand: Optional[str] = None
    model: Optional[str] = None
    name: Optional[str] = None
    photo_link: Optional[str] = None
    year: Optional[str] = None
    volume: Optional[str] = None
    mileage: Optional[int] = None
    price: Optional[str] = None
    is_dealer: Optional[bool] = None
    city: Optional[str] = None
    link: Optional[str] = None