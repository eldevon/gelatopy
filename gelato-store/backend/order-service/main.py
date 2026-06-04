from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List
import aio_pika
import json
import asyncio

from shared.models import Order, OrderItem, OrderStatus, DatabaseConfig, RabbitMQConfig

app = FastAPI(title="Order Service", port=8002)

# Database setup
config = DatabaseConfig()
engine = create_engine(config.database_url.replace('gelato_db', 'order_db'))
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class OrderDB(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    items = Column(JSON, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default=OrderStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# Repository (Dependency Inversion)
class OrderRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, order_data: dict) -> OrderDB:
        order = OrderDB(**order_data)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order
    
    def get_by_id(self, order_id: int) -> OrderDB:
        return self.db.query(OrderDB).filter(OrderDB.id == order_id).first()
    
    def update_status(self, order_id: int, status: OrderStatus) -> OrderDB:
        order = self.get_by_id(order_id)
        if order:
            order.status = status.value
            order.updated_at = datetime.utcnow()
            self.db.commit()
        return order

# Service (Single Responsibility)
class OrderService:
    def __init__(self, repository: OrderRepository, rabbitmq_url: str):
        self.repository = repository
        self.rabbitmq_url = rabbitmq_url
    
    async def create_order(self, customer_name: str, customer_email: str, items: List[dict]) -> Order:
        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in items)
        
        # Create order
        order_data = {
            "customer_name": customer_name,
            "customer_email": customer_email,
            "items": items,
            "total_amount": total,
            "status": OrderStatus.PENDING.value
        }
        
        order_db = self.repository.create(order_data)
        order = self._to_pydantic(order_db)
        
        # Publish to queue for processing
        await self.publish_order_created(order)
        
        return order
    
    async def publish_order_created(self, order: Order):
        connection = await aio_pika.connect_robust(self.rabbitmq_url)
        async with connection:
            channel = await connection.channel()
            await channel.default_exchange.publish(
                aio_pika.Message(body=order.json().encode()),
                routing_key="order_created"
            )
    
    def get_order(self, order_id: int) -> Order:
        order = self.repository.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return self._to_pydantic(order)
    
    def update_order_status(self, order_id: int, status: OrderStatus) -> Order:
        order = self.repository.update_status(order_id, status)
        return self._to_pydantic(order)
    
    def _to_pydantic(self, order_db: OrderDB) -> Order:
        return Order(
            id=order_db.id,
            customer_name=order_db.customer_name,
            customer_email=order_db.customer_email,
            items=[OrderItem(**item) for item in order_db.items],
            total_amount=order_db.total_amount,
            status=OrderStatus(order_db.status),
            created_at=order_db.created_at,
            updated_at=order_db.updated_at
        )

# API Endpoints (Interface Segregation)
@app.post("/orders", response_model=Order)
async def create_order(
    customer_name: str,
    customer_email: str,
    items: List[dict],
    db: Session = Depends(SessionLocal)
):
    repository = OrderRepository(db)
    config = RabbitMQConfig()
    service = OrderService(repository, config.rabbitmq_url)
    return await service.create_order(customer_name, customer_email, items)

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int, db: Session = Depends(SessionLocal)):
    repository = OrderRepository(db)
    config = RabbitMQConfig()
    service = OrderService(repository, config.rabbitmq_url)
    return service.get_order(order_id)

@app.put("/orders/{order_id}/status")
async def update_order_status(order_id: int, status: OrderStatus, db: Session = Depends(SessionLocal)):
    repository = OrderRepository(db)
    config = RabbitMQConfig()
    service = OrderService(repository, config.rabbitmq_url)
    order = service.update_order_status(order_id, status)
    return {"message": "Status updated", "order": order}