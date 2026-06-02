from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import config

engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SalesRecord(Base):
    __tablename__ = "sales_records"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String, unique=True, index=True)
    product_name = Column(String, index=True)
    category = Column(String, index=True)
    quantity = Column(Integer)
    unit_price = Column(Float)
    total_amount = Column(Float)
    customer_id = Column(String, index=True)
    sale_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")

class InventoryRecord(Base):
    __tablename__ = "inventory_records"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, unique=True, index=True)
    product_name = Column(String, index=True)
    category = Column(String, index=True)
    stock_quantity = Column(Integer)
    threshold = Column(Integer)
    last_updated = Column(DateTime, default=datetime.utcnow)

class CustomerRecord(Base):
    __tablename__ = "customer_records"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    registration_date = Column(DateTime, default=datetime.utcnow)
    total_purchases = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

class AlertRecord(Base):
    __tablename__ = "alert_records"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, index=True)
    message = Column(String)
    severity = Column(String, default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()