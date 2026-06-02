from sqlalchemy.orm import Session
from app.models.database import SessionLocal, SalesRecord, InventoryRecord, CustomerRecord
from datetime import datetime, timedelta
import random
import uuid

def init_sample_data():
    db = SessionLocal()
    
    categories = ["电子产品", "服装鞋帽", "食品饮料", "家居用品", "美妆护肤"]
    products = {
        "电子产品": ["智能手机", "笔记本电脑", "平板", "耳机", "智能手表"],
        "服装鞋帽": ["T恤", "牛仔裤", "运动鞋", "外套", "帽子"],
        "食品饮料": ["零食", "饮料", "方便面", "坚果", "巧克力"],
        "家居用品": ["毛巾", "牙刷", "床上用品", "厨房用品", "清洁用品"],
        "美妆护肤": ["洗面奶", "面霜", "口红", "眼影", "香水"]
    }
    
    try:
        if db.query(CustomerRecord).count() == 0:
            for i in range(100):
                customer = CustomerRecord(
                    customer_id=f"C{i+1:04d}",
                    name=f"用户{i+1}",
                    email=f"user{i+1}@example.com",
                    phone=f"13800138{i+1:04d}",
                    registration_date=datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                    total_purchases=random.uniform(100, 5000),
                    is_active=random.choice([True, True, True, False])
                )
                db.add(customer)
        db.commit()
        print("Customer data initialized")
    except Exception as e:
        print(f"Error initializing customers: {e}")
        db.rollback()
    
    try:
        if db.query(InventoryRecord).count() == 0:
            for category, product_list in products.items():
                for product in product_list:
                    inventory = InventoryRecord(
                        product_id=f"P{random.randint(1000, 9999)}",
                        product_name=product,
                        category=category,
                        stock_quantity=random.randint(10, 500),
                        threshold=50
                    )
                    db.add(inventory)
        db.commit()
        print("Inventory data initialized")
    except Exception as e:
        print(f"Error initializing inventory: {e}")
        db.rollback()
    
    try:
        if db.query(SalesRecord).count() == 0:
            customers = db.query(CustomerRecord).all()
            inventory = db.query(InventoryRecord).all()
            
            for day in range(30):
                num_sales = random.randint(5, 30)
                for _ in range(num_sales):
                    product = random.choice(inventory)
                    customer = random.choice(customers)
                    quantity = random.randint(1, 5)
                    unit_price = random.uniform(20, 2000)
                    
                    sale = SalesRecord(
                        order_id=f"ORD{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4())[:8]}",
                        product_name=product.product_name,
                        category=product.category,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_amount=quantity * unit_price,
                        customer_id=customer.customer_id,
                        sale_date=datetime.utcnow() - timedelta(days=day, hours=random.randint(0, 23)),
                        status="completed"
                    )
                    db.add(sale)
        db.commit()
        print("Sales data initialized")
    except Exception as e:
        print(f"Error initializing sales: {e}")
        db.rollback()
    
    db.close()
    print("Sample data initialization complete")

if __name__ == "__main__":
    init_sample_data()