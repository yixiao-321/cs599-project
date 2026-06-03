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
    
    def _format_anomaly_message(self, anomaly):
        """将异常字典转换为自然语言描述"""
        anomaly_type = anomaly.get("type")
        
        if anomaly_type == "inventory_empty":
            product_name = anomaly.get("product_name", "未知商品")
            return f"{product_name}商品库存已经为零，请立即补充库存！！！"
        
        elif anomaly_type == "inventory_low":
            product_name = anomaly.get("product_name", "未知商品")
            return f"{product_name}商品库存不足，请补充库存！"
        
        elif anomaly_type == "sales_drop":
            date_str = anomaly.get("date", datetime.utcnow().date().isoformat())
            ratio = anomaly.get("ratio", 0)
            return f"{date_str}的销售额低于昨日的{ratio}%，请尽快调整销售策略！！"
        
        else:
            return str(anomaly)
    
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
        anomalies = []
        
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        
        today_sales = self.db.query(SalesRecord).filter(
            SalesRecord.sale_date >= datetime.combine(today, datetime.min.time()),
            SalesRecord.sale_date < datetime.combine(today + timedelta(days=1), datetime.min.time())
        ).all()
        
        yesterday_sales = self.db.query(SalesRecord).filter(
            SalesRecord.sale_date >= datetime.combine(yesterday, datetime.min.time()),
            SalesRecord.sale_date < datetime.combine(today, datetime.min.time())
        ).all()
        
        today_total = sum(sr.total_amount for sr in today_sales)
        yesterday_total = sum(sr.total_amount for sr in yesterday_sales)
        
        if yesterday_total > 0 and today_total < yesterday_total * 0.5:
            anomalies.append({
                "type": "sales_drop",
                "today_sales": today_total,
                "yesterday_sales": yesterday_total,
                "ratio": round(today_total / yesterday_total * 100, 2),
                "date": today.isoformat(),
                "severity": "medium"
            })
        
        return anomalies
    
    def detect_inventory_anomalies(self):
        inventory = self.db.query(InventoryRecord).all()
        anomalies = []
        
        for item in inventory:
            if item.stock_quantity == 0:
                anomalies.append({
                    "type": "inventory_empty",
                    "product_name": item.stock_name,
                    "stock": item.stock_quantity,
                    "threshold": item.threshold,
                    "severity": "high"
                })
            elif item.stock_quantity < item.threshold:
                anomalies.append({
                    "type": "inventory_low",
                    "product_name": item.stock_name,
                    "stock": item.stock_quantity,
                    "threshold": item.threshold,
                    "severity": "low"
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
        
        suggestions = self._parse_llm_suggestions(llm_response)
        
        for anomaly in all_anomalies:
            existing_alert = self.db.query(AlertRecord).filter(
                AlertRecord.alert_type == anomaly["type"],
                AlertRecord.message.like(f"%{anomaly.get('product_name', '')}%"),
                AlertRecord.resolved == False
            ).first()
            if not existing_alert:
                base_message = self._format_anomaly_message(anomaly)
                product_name = anomaly.get("product_name", "")
                anomaly_suggestions = self._find_suggestions_for_anomaly(suggestions, anomaly, product_name)
                full_message = base_message + "\n\n处理建议：\n" + "\n".join(anomaly_suggestions) if anomaly_suggestions else base_message
                
                alert = AlertRecord(
                    alert_type=anomaly["type"],
                    message=full_message,
                    severity=anomaly.get("severity", "medium")
                )
                self.db.add(alert)
        
        self.db.commit()
        
        return {
            "anomalies": all_anomalies,
            "llm_analysis": llm_response
        }
    
    def _parse_llm_suggestions(self, llm_response):
        """解析LLM返回的处理建议"""
        suggestions = []
        lines = llm_response.strip().split('\n')
        
        current_item = None
        current_suggestions = []
        
        for line in lines:
            line = line.strip()
            if line.startswith("【") and "】" in line:
                if current_item and current_suggestions:
                    suggestions.append({
                        "item": current_item,
                        "suggestions": current_suggestions
                    })
                current_item = line
                current_suggestions = []
            elif line.startswith(("1.", "2.", "3.", "- ")):
                if current_item:
                    suggestion = line[2:].strip() if line[1] == '.' else line[2:].strip()
                    current_suggestions.append(suggestion)
        
        if current_item and current_suggestions:
            suggestions.append({
                "item": current_item,
                "suggestions": current_suggestions
            })
        
        return suggestions
    
    def _find_suggestions_for_anomaly(self, suggestions, anomaly, product_name):
        """根据异常类型和商品名称查找对应的处理建议"""
        anomaly_type = anomaly.get("type")
        
        for item in suggestions:
            item_text = item["item"]
            
            if anomaly_type == "inventory_empty":
                if "库存为空" in item_text or ("库存为零" in item_text):
                    if not product_name or product_name in item_text or "??" in item_text:
                        return [f"{i+1}. {s}" for i, s in enumerate(item["suggestions"])]
            
            elif anomaly_type == "inventory_low":
                if "库存不足" in item_text:
                    if product_name and product_name in item_text:
                        return [f"{i+1}. {s}" for i, s in enumerate(item["suggestions"])]
                    elif not product_name:
                        return [f"{i+1}. {s}" for i, s in enumerate(item["suggestions"])]
            
            elif anomaly_type == "sales_drop":
                if "销量骤降" in item_text or "销售额" in item_text:
                    return [f"{i+1}. {s}" for i, s in enumerate(item["suggestions"])]
        
        return None