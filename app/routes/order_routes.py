from fastapi import APIRouter,FastAPI, HTTPException, Path, Query
from bson import ObjectId
from fastapi.responses import JSONResponse
from app.database import db
from starlette.status import HTTP_201_CREATED
import datetime
from app.models.order_model import OrderCreate,OrderResponse

router = APIRouter()

@router.post("/orders", status_code=HTTP_201_CREATED, response_model=OrderResponse)
def create_order(order: OrderCreate):
    new_order = {
        "userId": order.userId,
        "items": [item.model_dump() for item in order.items]
    }

    inserted = db.orders.insert_one(new_order)

    return {
        "orderId": str(inserted.inserted_id)
    }

def serialize_order(order):
    items_with_details = []
    total_price = 0.0

    for item in order["items"]:
        product = db.products.find_one({"_id": ObjectId(item["productId"])})
        if product:
            name = product["name"]
            price = product["price"]
            item_total = price * item["qty"]
            total_price += item_total
        else:
            name = "Unknown Product"
            price = 0.0

        items_with_details.append({
            "productDetails": {
                "name": name,
                "id": item["productId"]
            },
            "qty": item["qty"]
        })

    return {
        "id": str(order["_id"]),
        "items": items_with_details,
        "total": round(total_price, 2)
    }

@router.get("/orders/{user_id}", status_code=200)
def list_orders(
    user_id: str = Path(..., description="User ID"),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    cursor = db.orders.find({"userId": user_id}).skip(offset).limit(limit)

    orders = [serialize_order(order) for order in cursor]

    pagination = {
        "next": offset + limit,
        "limit": limit,
        "previous": max(offset - limit, 0)
    }

    return JSONResponse(content={"data": orders, "page": pagination})