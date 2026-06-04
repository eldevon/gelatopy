from pydantic import BaseModel, BaseSettings
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Flavor(str, Enum):
    CHOCOLATE = "chocolate"
    VANILLA = "vanilla"
    STRAWBERRY = "strawberry"
    PISTACHIO = "pistachio"
    MINT = "mint"
    COFFEE = "coffee"

class Product(BaseModel):
    id: int
    name: str
    flavor: Flavor
    price: float
    description: str
    stock: int
    image_url: str

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItem(BaseModel):
    product_id: int
    flavor: Flavor
    quantity: int
    price: float

class Order(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime]

class DatabaseConfig(BaseSettings):
    database_url: str
    
    class Config:
        env_file = ".env"

class RabbitMQConfig(BaseSettings):
    rabbitmq_url: str
    
    class Config:
        env_file = ".env"