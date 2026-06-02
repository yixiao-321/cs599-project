from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import SalesRecord, InventoryRecord, AlertRecord
from app.llm.client import get_deepseek_client
from app.llm.prompts import ANOMALY_DETECTION_PROMPT
import math

class AnomalyDetector:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_deepseek_client()
    
    def _calculate_mean(self, values):
        if not values:
            return 0
        return sum(values) / len(values)
    
    def _calculate_std(self, values, mean):
        if not values or len(values) < 2:
            return 0
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)
    
    def detect_sales_anomalies(self, days: int = 7):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        sales_data = self.db.query(SalesRecord).filter(
            SalesRecord.sale_date >= start_date
        ).all()
        
        anomalies = []
        
        if len(sales_data) >= 3:
            amounts = [sr.total_amount for sr in sales_data]
            mean = self._calculate_mean(amounts)
            std = self._calculate_std(amounts, mean)
            
            for sr in sales_data:
                z_score = abs((sr.total_amount - mean) / std) if std > 0 else 0
                if z_score > 3:
                    anomalies.append({
                        "type": "sales_anomaly",
                        "order_id": sr.order_id,
                        "amount": sr.total_amount,
                        "z_score": z_score,
                        "date": sr.sale_date,
                        "severity": "high" if z_score > 4 else "medium"
                    })
        
        return anomalies
    
    def detect_inventory_anomalies(self):
        inventory = self.db.query(InventoryRecord).all()
        anomalies = []
        
        for item in inventory:
            if item.stock_quantity <= 0:
                anomalies.append({
                    "type": "inventory_empty",
                    "product_name": item.product_name,
                    "stock": item.stock_quantity,
                    "severity": "high"
                })
            elif item.stock_quantity < item.threshold:
                anomalies.append({
                    "type": "inventory_low",
                    "product_name": item.product_name,
                    "stock": item.stock_quantity,
                    "threshold": item.threshold,
                    "severity": "medium"
                })
        
        return anomalies
    
    def generate_anomaly_report(self):
        sales_anomalies = self.detect_sales_anomalies()
        inventory_anomalies = self.detect_inventory_anomalies()
        
        all_anomalies = sales_anomalies + inventory_anomalies
        
        if not all_anomalies:
            return {"message": "No anomalies detected", "anomalies": []}
        
        data = "\n".join([str(a) for a in all_anomalies])
        prompt = ANOMALY_DETECTION_PROMPT.format(data=data)
        try:
            response = self.llm.invoke(prompt)
            llm_response = response.content
        except Exception as e:
            llm_response = f"LLM调用失败: {str(e)}"
        
        for anomaly in all_anomalies:
            alert = AlertRecord(
                alert_type=anomaly["type"],
                message=str(anomaly),
                severity=anomaly.get("severity", "medium")
            )
            self.db.add(alert)
        
        self.db.commit()
        
        return {
            "anomalies": all_anomalies,
            "llm_analysis": llm_response
        }