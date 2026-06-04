from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import List, Dict
from pydantic import BaseModel

app = FastAPI(title="API Gateway", port=8000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PRODUCT_SERVICE_URL = "http://product-service:8001"
ORDER_SERVICE_URL = "http://order-service:8002"

class OrderRequest(BaseModel):
    customer_name: str
    customer_email: str
    items: List[Dict]

@app.get("/api/products")
async def get_products():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PRODUCT_SERVICE_URL}/products")
        return response.json()

@app.get("/api/products/{flavor}")
async def get_product(flavor: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{PRODUCT_SERVICE_URL}/products/{flavor}")
        return response.json()

@app.post("/api/orders")
async def create_order(order: OrderRequest):
    async with httpx.AsyncClient() as client:
        # Check stock for each item
        for item in order.items:
            stock_response = await client.post(
                f"{PRODUCT_SERVICE_URL}/products/{item['product_id']}/check-stock",
                params={"quantity": item['quantity']}
            )
            stock_data = stock_response.json()
            if not stock_data['available']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {item['product_id']}"
                )
        
        # Create order
        response = await client.post(
            f"{ORDER_SERVICE_URL}/orders",
            params={
                "customer_name": order.customer_name,
                "customer_email": order.customer_email
            },
            json=order.items
        )
        return response.json()

@app.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ORDER_SERVICE_URL}/orders/{order_id}")
        return response.json()