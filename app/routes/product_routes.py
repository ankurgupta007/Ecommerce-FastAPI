from fastapi import APIRouter, Query
from app.database import db
from app.models.product_model import ProductCreate,PaginatedProductResponse
from bson import ObjectId
from typing import Optional

router = APIRouter()

@router.post("/products",status_code=201)
def create_product(product: ProductCreate):
    result = db.products.insert_one(product.model_dump())
    return {"id": str(result.inserted_id)}

@router.get("/products", response_model=PaginatedProductResponse)
def list_products(name: Optional[str] = Query(None),
                  size: Optional[str] = Query(None),
                  limit: int = Query(10, gt=0),
                  offset: int = Query(0, ge=0)
                ):
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if size:
        query["sizes.size"] = size

    cursor = db.products.find(query).sort("_id",1).skip(offset).limit(limit)
    total_count = db.products.count_documents(query)

    data = []
    for product in cursor:
        data.append({
            "id": str(product["_id"]),
            "name": product["name"],
            "price": product["price"]
        })
    
    next_offset = offset + limit if (offset + limit) < total_count else offset
    prev_offset = max(0, offset - limit)

    return{
        "data": data,
        "page": {
            "next": next_offset,
            "limit": len(data),
            "previous": prev_offset
        }
    }
    
    