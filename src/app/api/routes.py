from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db, SalesRecord, InventoryRecord, CustomerRecord, AlertRecord, User, ProductRecord
from datetime import datetime
from app.services.user_service import verify_password, init_default_users
from app.agent.sales_analyzer import SalesAnalyzer
from app.agent.anomaly_detector import AnomalyDetector
from app.agent.report_generator import ReportGenerator
from app.agent.visualization_agent import VisualizationAgent
from app.agent.chat_agent import ChatAgent
from app.workflow.workflow import workflow
from datetime import datetime, timedelta
import random

router = APIRouter()

class ChatRequest(BaseModel):
    question: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: dict = None

@router.post("/api/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        init_default_users(db)
        
        if verify_password(db, request.username, request.password):
            user = db.query(User).filter(User.username == request.username).first()
            return {
                "success": True,
                "message": "登录成功",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "name": user.name,
                    "email": user.email
                }
            }
        else:
            return {"success": False, "message": "用户名或密码错误"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/logout")
def logout():
    return {"success": True, "message": "退出成功"}

@router.get("/api/sales/analysis")
def get_sales_analysis(days: int = 7, db: Session = Depends(get_db)):
    try:
        analyzer = SalesAnalyzer(db)
        result = analyzer.analyze_sales_trend(days=days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/anomalies/detect")
def detect_anomalies(db: Session = Depends(get_db)):
    try:
        detector = AnomalyDetector(db)
        result = detector.generate_anomaly_report()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reports/daily")
def get_daily_report(db: Session = Depends(get_db)):
    try:
        generator = ReportGenerator(db)
        result = generator.generate_daily_report()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reports/weekly")
def get_weekly_report(db: Session = Depends(get_db)):
    try:
        generator = ReportGenerator(db)
        result = generator.generate_weekly_report()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/alerts")
def get_alerts(db: Session = Depends(get_db)):
    try:
        generator = ReportGenerator(db)
        result = generator.generate_alert_summary()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    try:
        alert = db.query(AlertRecord).filter(AlertRecord.id == alert_id).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        alert.resolved = True
        db.commit()
        return {"message": "Alert resolved successfully"}
    except HTTPException as e:
        raise e

@router.delete("/api/alerts")
def clear_all_alerts(db: Session = Depends(get_db)):
    try:
        db.query(AlertRecord).delete()
        db.commit()
        return {"message": "All alerts cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/visualizations/sales-trend")
def get_sales_trend_chart(days: int = 30, db: Session = Depends(get_db)):
    try:
        viz = VisualizationAgent(db)
        result = viz.generate_sales_trend_chart(days=days)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return {"chart_html": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/visualizations/category-sales")
def get_category_sales_chart(db: Session = Depends(get_db)):
    try:
        viz = VisualizationAgent(db)
        result = viz.generate_category_sales_chart()
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return {"chart_html": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/visualizations/inventory")
def get_inventory_chart(db: Session = Depends(get_db)):
    try:
        viz = VisualizationAgent(db)
        result = viz.generate_inventory_chart()
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return {"chart_html": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/workflow/run")
def run_workflow(days: int = 7):
    try:
        result = workflow.run(days=days)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/summary")
def get_summary_stats(days: int = 30, db: Session = Depends(get_db)):
    try:
        viz = VisualizationAgent(db)
        result = viz.generate_sales_summary_stats(days=days)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/chat")
def chat(request: ChatRequest):
    try:
        agent = ChatAgent()
        answer = agent.chat(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        agent = ChatAgent()
        answer = agent.chat(request.question)
        
        import asyncio
        for i in range(0, len(answer), 10):
            chunk = answer[i:i+10]
            yield {"chunk": chunk, "done": False}
            await asyncio.sleep(0.05)
        
        yield {"chunk": "", "done": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class InventoryCreate(BaseModel):
    stock_name: str
    stock_category: str
    stock_quantity: int
    threshold: int = 10

class InventoryUpdate(BaseModel):
    stock_name: str
    stock_category: str
    stock_quantity: int
    threshold: int

class ProductCreate(BaseModel):
    product_name: str
    unit_price: float
    discount_strategy: str
    stock_id: str
    category: str

class ProductUpdate(BaseModel):
    product_name: str
    unit_price: float
    discount_strategy: str

class ProductStatusUpdate(BaseModel):
    status: str

def get_category_prefix(category: str) -> str:
    pinyin_map = {
        '食品': 'SP', '饮料': 'YL', '日用品': 'RY', '电子产品': 'DZ',
        '服装': 'FZ', '其他': 'QT', '水果': 'SG', '蔬菜': 'SC',
        '生鲜': 'SX', '零食': 'LS', '酒水': 'JS', '化妆品': 'HZ'
    }
    return pinyin_map.get(category, 'QT')

@router.get("/api/inventory")
def get_inventory(page: int = 1, name: str = "", category: str = "", db: Session = Depends(get_db)):
    query = db.query(InventoryRecord)
    if name:
        query = query.filter(InventoryRecord.stock_name.like(f"%{name}%"))
    if category:
        query = query.filter(InventoryRecord.stock_category == category)
    
    query = query.order_by(InventoryRecord.last_updated.desc())
    
    total_items = query.count()
    page_size = 10
    total_pages = (total_items + page_size - 1) // page_size
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": [
            {
                "id": item.id,
                "stock_id": item.stock_id,
                "stock_name": item.stock_name,
                "stock_category": item.stock_category,
                "stock_quantity": item.stock_quantity,
                "threshold": item.threshold,
                "last_updated": item.last_updated.isoformat()
            } for item in items
        ],
        "page": page,
        "total_pages": total_pages,
        "total_items": total_items
    }

@router.get("/api/inventory/categories")
def get_inventory_categories(db: Session = Depends(get_db)):
    categories = db.query(InventoryRecord.stock_category).distinct().all()
    return [cat[0] for cat in categories]

@router.get("/api/inventory/names")
def get_inventory_names(db: Session = Depends(get_db)):
    items = db.query(InventoryRecord.stock_id, InventoryRecord.stock_name, InventoryRecord.stock_category).all()
    return [
        {"stock_id": item[0], "stock_name": item[1], "stock_category": item[2]}
        for item in items
    ]

@router.get("/api/inventory/{id}")
def get_inventory_item(id: int, db: Session = Depends(get_db)):
    item = db.query(InventoryRecord).filter(InventoryRecord.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="库存不存在")
    return {
        "id": item.id,
        "stock_id": item.stock_id,
        "stock_name": item.stock_name,
        "stock_category": item.stock_category,
        "stock_quantity": item.stock_quantity,
        "threshold": item.threshold,
        "last_updated": item.last_updated.isoformat()
    }

@router.post("/api/inventory")
def create_inventory(data: InventoryCreate, db: Session = Depends(get_db)):
    if not data.stock_name or not data.stock_category:
        return {"success": False, "message": "库存名称和类别不能为空"}
    
    category_prefix = get_category_prefix(data.stock_category)
    current_month = datetime.now().strftime("%Y%m")
    
    existing_count = db.query(InventoryRecord).filter(
        InventoryRecord.stock_id.like(f"{category_prefix}{current_month}%")
    ).count()
    
    stock_id = f"{category_prefix}{current_month}{str(existing_count).zfill(2)}"
    
    existing_item = db.query(InventoryRecord).filter(InventoryRecord.stock_name == data.stock_name).first()
    if existing_item:
        return {"success": False, "message": "库存名称已存在"}
    
    new_item = InventoryRecord(
        stock_id=stock_id,
        stock_name=data.stock_name,
        stock_category=data.stock_category,
        stock_quantity=data.stock_quantity,
        threshold=data.threshold,
        last_updated=datetime.now()
    )
    
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    return {"success": True, "message": "新增成功", "stock_id": stock_id}

@router.put("/api/inventory/{id}")
def update_inventory(id: int, data: InventoryUpdate, db: Session = Depends(get_db)):
    item = db.query(InventoryRecord).filter(InventoryRecord.id == id).first()
    if not item:
        return {"success": False, "message": "库存不存在"}
    
    item.stock_name = data.stock_name
    item.stock_category = data.stock_category
    item.stock_quantity = data.stock_quantity
    item.threshold = data.threshold
    item.last_updated = datetime.now()
    
    db.commit()
    db.refresh(item)
    
    return {"success": True, "message": "更新成功"}

@router.delete("/api/inventory/{id}")
def delete_inventory(id: int, db: Session = Depends(get_db)):
    item = db.query(InventoryRecord).filter(InventoryRecord.id == id).first()
    if not item:
        return {"success": False, "message": "库存不存在"}
    
    db.delete(item)
    db.commit()
    
    return {"success": True, "message": "删除成功"}

@router.get("/api/products")
def get_products(page: int = 1, name: str = "", category: str = "", db: Session = Depends(get_db)):
    query = db.query(ProductRecord)
    if name:
        query = query.filter(ProductRecord.product_name.like(f"%{name}%"))
    if category:
        query = query.filter(ProductRecord.product_category == category)
    
    query = query.order_by(ProductRecord.last_updated.desc())
    
    total_items = query.count()
    page_size = 10
    total_pages = (total_items + page_size - 1) // page_size
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "product_category": item.product_category,
                "unit_price": item.unit_price,
                "discount_strategy": item.discount_strategy,
                "status": item.status,
                "last_shelf_time": item.last_shelf_time.isoformat() if item.last_shelf_time else None,
                "last_updated": item.last_updated.isoformat()
            } for item in items
        ],
        "page": page,
        "total_pages": total_pages,
        "total_items": total_items
    }

@router.get("/api/products/{id}")
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(ProductRecord).filter(ProductRecord.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    return {
        "id": product.id,
        "product_id": product.product_id,
        "product_name": product.product_name,
        "product_category": product.product_category,
        "unit_price": product.unit_price,
        "discount_strategy": product.discount_strategy,
        "status": product.status,
        "last_shelf_time": product.last_shelf_time.isoformat() if product.last_shelf_time else None,
        "last_updated": product.last_updated.isoformat()
    }

@router.post("/api/products")
def create_product(data: ProductCreate, db: Session = Depends(get_db)):
    if not data.product_name or not data.unit_price:
        return {"success": False, "message": "商品名称和单价不能为空"}
    
    existing_product = db.query(ProductRecord).filter(ProductRecord.product_name == data.product_name).first()
    if existing_product:
        return {"success": False, "message": "商品名称已存在"}
    
    new_product = ProductRecord(
        product_id=data.stock_id,
        product_name=data.product_name,
        product_category=data.category,
        unit_price=data.unit_price,
        discount_strategy=data.discount_strategy,
        status="下架",
        last_shelf_time=None,
        last_updated=datetime.now()
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return {"success": True, "message": "新增成功"}

@router.put("/api/products/{id}")
def update_product(id: int, data: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(ProductRecord).filter(ProductRecord.id == id).first()
    if not product:
        return {"success": False, "message": "商品不存在"}
    
    product.product_name = data.product_name
    product.unit_price = data.unit_price
    product.discount_strategy = data.discount_strategy
    product.last_updated = datetime.now()
    
    db.commit()
    db.refresh(product)
    
    return {"success": True, "message": "更新成功"}

@router.delete("/api/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    product = db.query(ProductRecord).filter(ProductRecord.id == id).first()
    if not product:
        return {"success": False, "message": "商品不存在"}
    
    db.delete(product)
    db.commit()
    
    return {"success": True, "message": "删除成功"}

@router.put("/api/products/{id}/status")
def update_product_status(id: int, data: ProductStatusUpdate, db: Session = Depends(get_db)):
    product = db.query(ProductRecord).filter(ProductRecord.id == id).first()
    if not product:
        return {"success": False, "message": "商品不存在"}
    
    old_status = product.status
    product.status = data.status
    product.last_updated = datetime.now()
    
    if data.status == "上架" and old_status == "下架":
        product.last_shelf_time = datetime.now()
    
    db.commit()
    db.refresh(product)
    
    return {"success": True, "message": "状态更新成功"}

@router.get("/api/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(ProductRecord.product_category).distinct().all()
    return [cat[0] for cat in categories]

@router.post("/api/test/generate-data")
def generate_test_data(db: Session = Depends(get_db)):
    try:
        today = datetime.now()
        categories = ["电子产品", "服装", "食品", "日用品", "饮料"]
        product_names = {
            "电子产品": ["蓝牙耳机", "手机壳", "充电宝", "数据线", "充电器"],
            "服装": ["T恤", "牛仔裤", "运动鞋", "外套", "帽子"],
            "食品": ["薯片", "巧克力", "饼干", "坚果", "糖果"],
            "日用品": ["纸巾", "洗衣液", "洗发水", "牙膏", "毛巾"],
            "饮料": ["可乐", "果汁", "矿泉水", "咖啡", "茶"]
        }
        
        created_count = 0
        
        for category in categories:
            for product_name in product_names[category]:
                for _ in range(3):
                    sale_time = today.replace(
                        hour=random.randint(9, 21),
                        minute=random.randint(0, 59),
                        second=random.randint(0, 59)
                    )
                    unit_price = round(random.uniform(10, 500), 2)
                    quantity = random.randint(1, 10)
                    
                    sale = SalesRecord(
                        order_id=f"ORD{today.strftime('%Y%m%d')}{str(random.randint(1000, 9999))}",
                        sale_date=sale_time,
                        product_name=product_name,
                        category=category,
                        unit_price=unit_price,
                        quantity=quantity,
                        total_amount=unit_price * quantity,
                        customer_id=f"C{random.randint(1000, 9999)}",
                        status="completed"
                    )
                    db.add(sale)
                    created_count += 1
        
        db.commit()
        
        return {"success": True, "message": f"成功生成 {created_count} 条当日销售数据"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/test/generate-inventory")
def generate_test_inventory(db: Session = Depends(get_db)):
    try:
        categories = ["电子产品", "服装", "食品", "日用品", "饮料"]
        product_names = {
            "电子产品": ["蓝牙耳机", "手机壳", "充电宝", "数据线", "充电器"],
            "服装": ["T恤", "牛仔裤", "运动鞋", "外套", "帽子"],
            "食品": ["薯片", "巧克力", "饼干", "坚果", "糖果"],
            "日用品": ["纸巾", "洗衣液", "洗发水", "牙膏", "毛巾"],
            "饮料": ["可乐", "果汁", "矿泉水", "咖啡", "茶"]
        }
        
        created_count = 0
        
        for category in categories:
            for product_name in product_names[category]:
                existing = db.query(InventoryRecord).filter(
                    InventoryRecord.stock_name == product_name
                ).first()
                
                if not existing:
                    category_prefix = get_category_prefix(category)
                    current_month = datetime.now().strftime("%Y%m")
                    existing_count = db.query(InventoryRecord).filter(
                        InventoryRecord.stock_id.like(f"{category_prefix}{current_month}%")
                    ).count()
                    stock_id = f"{category_prefix}{current_month}{str(existing_count).zfill(2)}"
                    
                    inventory = InventoryRecord(
                        stock_id=stock_id,
                        stock_name=product_name,
                        stock_category=category,
                        stock_quantity=random.randint(0, 50),
                        threshold=10,
                        last_updated=datetime.now()
                    )
                    db.add(inventory)
                    created_count += 1
        
        db.commit()
        
        return {"success": True, "message": f"成功生成 {created_count} 条库存数据"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/test/clear-sales")
def clear_test_sales(db: Session = Depends(get_db)):
    try:
        today = datetime.now().date()
        count = db.query(SalesRecord).filter(
            SalesRecord.sale_date >= today
        ).delete()
        db.commit()
        return {"success": True, "message": f"成功删除 {count} 条当日销售数据"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reports/traditional/daily")
def get_traditional_daily_report(db: Session = Depends(get_db)):
    try:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        today_sales = db.query(SalesRecord).filter(
            SalesRecord.sale_date >= today,
            SalesRecord.sale_date < today + timedelta(days=1)
        ).all()
        
        yesterday_sales = db.query(SalesRecord).filter(
            SalesRecord.sale_date >= yesterday,
            SalesRecord.sale_date < today
        ).all()
        
        total_sales = sum(s.total_amount for s in today_sales)
        total_orders = len(today_sales)
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        customers = db.query(CustomerRecord).all()
        total_customers = len(customers)
        new_customers = len([c for c in customers if c.registration_date.date() == today])
        active_customers = len([c for c in customers if c.is_active])
        
        category_sales = {}
        for sale in today_sales:
            category = sale.category
            if category not in category_sales:
                category_sales[category] = {"sales": 0, "orders": 0}
            category_sales[category]["sales"] += sale.total_amount
            category_sales[category]["orders"] += 1
        
        category_data = []
        for cat, data in category_sales.items():
            percentage = (data["sales"] / total_sales * 100) if total_sales > 0 else 0
            category_data.append({
                "category": cat,
                "sales": data["sales"],
                "orders": data["orders"],
                "percentage": round(percentage, 1)
            })
        
        daily_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            day_sales = db.query(SalesRecord).filter(
                SalesRecord.sale_date >= date,
                SalesRecord.sale_date < date + timedelta(days=1)
            ).all()
            daily_data.append({
                "date": date.strftime("%m-%d"),
                "sales": sum(s.total_amount for s in day_sales),
                "orders": len(day_sales)
            })
        
        return {
            "summary": {
                "total_sales": total_sales,
                "total_orders": total_orders,
                "avg_order_value": avg_order_value,
                "total_customers": total_customers,
                "new_customers": new_customers,
                "active_customers": active_customers,
                "conversion_rate": 3.2,
                "repeat_rate": 15.5,
                "return_rate": 2.1,
                "avg_ship_time": 24,
                "satisfaction": 95.3
            },
            "category_data": category_data,
            "daily_data": daily_data,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/reports/traditional/weekly")
def get_traditional_weekly_report(db: Session = Depends(get_db)):
    try:
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        weekly_sales = db.query(SalesRecord).filter(
            SalesRecord.sale_date >= week_start,
            SalesRecord.sale_date <= week_end
        ).all()
        
        total_sales = sum(s.total_amount for s in weekly_sales)
        total_orders = len(weekly_sales)
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        customers = db.query(CustomerRecord).all()
        total_customers = len(customers)
        new_customers = len([c for c in customers if c.registration_date.date() >= week_start])
        active_customers = len([c for c in customers if c.is_active])
        
        category_sales = {}
        for sale in weekly_sales:
            category = sale.category
            if category not in category_sales:
                category_sales[category] = {"sales": 0, "orders": 0}
            category_sales[category]["sales"] += sale.total_amount
            category_sales[category]["orders"] += 1
        
        category_data = []
        for cat, data in category_sales.items():
            percentage = (data["sales"] / total_sales * 100) if total_sales > 0 else 0
            category_data.append({
                "category": cat,
                "sales": data["sales"],
                "orders": data["orders"],
                "percentage": round(percentage, 1)
            })
        
        daily_data = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            day_sales = db.query(SalesRecord).filter(
                SalesRecord.sale_date >= date,
                SalesRecord.sale_date < date + timedelta(days=1)
            ).all()
            daily_data.append({
                "date": date.strftime("%m-%d"),
                "sales": sum(s.total_amount for s in day_sales),
                "orders": len(day_sales)
            })
        
        return {
            "summary": {
                "total_sales": total_sales,
                "total_orders": total_orders,
                "avg_order_value": avg_order_value,
                "total_customers": total_customers,
                "new_customers": new_customers,
                "active_customers": active_customers,
                "conversion_rate": 3.2,
                "repeat_rate": 15.5,
                "return_rate": 2.1,
                "avg_ship_time": 24,
                "satisfaction": 95.3
            },
            "category_data": category_data,
            "daily_data": daily_data,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/alerts/traditional")
def get_traditional_alerts(db: Session = Depends(get_db)):
    try:
        alerts = db.query(AlertRecord).filter(AlertRecord.resolved == False).all()
        alert_list = []
        for alert in alerts:
            alert_list.append({
                "id": alert.id,
                "type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "created_at": alert.created_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return {"alerts": alert_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/anomalies/detect/traditional")
def detect_traditional_anomalies(db: Session = Depends(get_db)):
    try:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        inventory_items = db.query(InventoryRecord).all()
        today_sales = db.query(SalesRecord).filter(
            SalesRecord.sale_date >= today,
            SalesRecord.sale_date < today + timedelta(days=1)
        ).all()
        yesterday_sales = db.query(SalesRecord).filter(
            SalesRecord.sale_date >= yesterday,
            SalesRecord.sale_date < today
        ).all()
        
        anomalies = []
        
        for item in inventory_items:
            if item.stock_quantity == 0:
                message = f"【高优先级】{item.stock_name}商品库存已经为零，请立即补充库存！！！"
                anomalies.append({
                    "id": len(anomalies) + 1,
                    "type": "inventory_empty",
                    "severity": "high",
                    "message": message,
                    "product_name": item.stock_name,
                    "stock": 0,
                    "threshold": item.threshold,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            elif item.stock_quantity < item.threshold:
                message = f"【低优先级】{item.stock_name}商品库存不足，请补充库存！"
                anomalies.append({
                    "id": len(anomalies) + 1,
                    "type": "inventory_low",
                    "severity": "low",
                    "message": message,
                    "product_name": item.stock_name,
                    "stock": item.stock_quantity,
                    "threshold": item.threshold,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        today_total = sum(s.total_amount for s in today_sales)
        yesterday_total = sum(s.total_amount for s in yesterday_sales)
        
        if yesterday_total > 0 and today_total < yesterday_total * 0.5:
            ratio = round((today_total / yesterday_total) * 100, 1)
            message = f"【中优先级】{today.strftime('%Y-%m-%d')}的销售额低于昨日的{ratio}%，请尽快调整销售策略！！"
            anomalies.append({
                "id": len(anomalies) + 1,
                "type": "sales_drop",
                "severity": "medium",
                "message": message,
                "ratio": ratio,
                "date": today.strftime("%Y-%m-%d"),
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        return {"alerts": anomalies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))