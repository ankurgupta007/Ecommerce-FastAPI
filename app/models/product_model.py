from pydantic import BaseModel
from typing import List

class SizeQuantity(BaseModel):
    size : str
    quantity: int

class ProductCreate(BaseModel):
    name: str
    price: float
    sizes: List[SizeQuantity]

class ProductResponse(BaseModel):
    id: str
    name: str
    price: float

class PageInfo(BaseModel):
    next: int
    limit: int
    previous: int

class PaginatedProductResponse(BaseModel):
    data: List[ProductResponse]
    page: PageInfo