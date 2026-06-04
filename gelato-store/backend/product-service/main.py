from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List
import os

from shared.models import Product as ProductModel, Flavor, DatabaseConfig

app = FastAPI(title="Product Service", port=8001)

# Database setup
config = DatabaseConfig()
engine = create_engine(config.database_url.replace('gelato_db', 'product_db'))
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# SQLAlchemy Model
class ProductDB(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    flavor = Column(String, nullable=False, unique=True)
    price = Column(Float, nullable=False)
    description = Column(String)
    stock = Column(Integer, default=100)
    image_url = Column(String)

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Repository (Dependency Inversion Principle)
class ProductRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self) -> List[ProductDB]:
        return self.db.query(ProductDB).all()
    
    def get_by_id(self, product_id: int) -> ProductDB:
        return self.db.query(ProductDB).filter(ProductDB.id == product_id).first()
    
    def get_by_flavor(self, flavor: Flavor) -> ProductDB:
        return self.db.query(ProductDB).filter(ProductDB.flavor == flavor.value).first()
    
    def update_stock(self, product_id: int, quantity: int) -> bool:
        product = self.get_by_id(product_id)
        if product and product.stock >= quantity:
            product.stock -= quantity
            self.db.commit()
            return True
        return False

# Service (Single Responsibility Principle)
class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository
    
    def get_all_products(self) -> List[ProductModel]:
        products = self.repository.get_all()
        return [self._to_pydantic(p) for p in products]
    
    def get_product_by_flavor(self, flavor: Flavor) -> ProductModel:
        product = self.repository.get_by_flavor(flavor)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return self._to_pydantic(product)
    
    def check_stock(self, product_id: int, quantity: int) -> bool:
        product = self.repository.get_by_id(product_id)
        return product and product.stock >= quantity
    
    def reserve_stock(self, product_id: int, quantity: int) -> bool:
        return self.repository.update_stock(product_id, quantity)
    
    def _to_pydantic(self, product: ProductDB) -> ProductModel:
        return ProductModel(
            id=product.id,
            name=product.name,
            flavor=Flavor(product.flavor),
            price=product.price,
            description=product.description,
            stock=product.stock,
            image_url=product.image_url
        )

# API Endpoints (Interface Segregation Principle)
@app.get("/products", response_model=List[ProductModel])
async def get_products(db: Session = Depends(get_db)):
    repository = ProductRepository(db)
    service = ProductService(repository)
    return service.get_all_products()

@app.get("/products/{flavor}", response_model=ProductModel)
async def get_product(flavor: Flavor, db: Session = Depends(get_db)):
    repository = ProductRepository(db)
    service = ProductService(repository)
    return service.get_product_by_flavor(flavor)

@app.post("/products/{product_id}/check-stock")
async def check_stock(product_id: int, quantity: int, db: Session = Depends(get_db)):
    repository = ProductRepository(db)
    service = ProductService(repository)
    available = service.check_stock(product_id, quantity)
    return {"available": available, "product_id": product_id, "quantity": quantity}

# Initialize products (6 flavors)
@app.on_event("startup")
async def init_products():
    db = SessionLocal()
    try:
        existing = db.query(ProductDB).first()
        if not existing:
            products = [
                ProductDB(
                    name="Dark Chocolate Gelato",
                    flavor="chocolate",
                    price=4.50,
                    description="Rich and intense dark chocolate gelato",
                    stock=100,
                    image_url="/images/chocolate.jpg"
                ),
                ProductDB(
                    name="Madagascar Vanilla",
                    flavor="vanilla",
                    price=4.00,
                    description="Premium vanilla bean gelato",
                    stock=100,
                    image_url="/images/vanilla.jpg"
                ),
                ProductDB(
                    name="Fresh Strawberry",
                    flavor="strawberry",
                    price=4.50,
                    description="Made with real strawberries",
                    stock=100,
                    image_url="/images/strawberry.jpg"
                ),
                ProductDB(
                    name="Sicilian Pistachio",
                    flavor="pistachio",
                    price=5.50,
                    description="Premium pistachios from Sicily",
                    stock=100,
                    image_url="/images/pistachio.jpg"
                ),
                ProductDB(
                    name="Cool Mint",
                    flavor="mint",
                    price=4.00,
                    description="Refreshing mint with dark chocolate chips",
                    stock=100,
                    image_url="/images/mint.jpg"
                ),
                ProductDB(
                    name="Italian Coffee",
                    flavor="coffee",
                    price=4.50,
                    description="Bold espresso flavor",
                    stock=100,
                    image_url="/images/coffee.jpg"
                ),
            ]
            for product in products:
                db.add(product)
            db.commit()
    finally:
        db.close()