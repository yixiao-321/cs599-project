from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import SalesRecord, CustomerRecord
from app.llm.client import get_deepseek_client
from app.llm.prompts import SALES_ANALYSIS_PROMPT

class SalesAnalyzer:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_deepseek_client()
    
    def get_sales_data(self, days: int = 30):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        return self.db.query(SalesRecord).filter(
            SalesRecord.sale_date >= start_date
        ).all()
    
    def get_customer_data(self):
        return self.db.query(CustomerRecord).all()
    
    def analyze_sales_trend(self, days: int = 30):
        sales_data = self.get_sales_data(days)
        
        if not sales_data:
            return {"error": "No sales data available"}
        
        total_sales = sum(sr.total_amount for sr in sales_data)
        total_orders = len(sales_data)
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        category_sales = {}
        for sr in sales_data:
            category = sr.category
            if category not in category_sales:
                category_sales[category] = {"total": 0, "count": 0}
            category_sales[category]["total"] += sr.total_amount
            category_sales[category]["count"] += sr.quantity
        
        data_summary = f"""
        时间范围：最近{days}天
        总销售额：¥{total_sales:.2f}
        订单总数：{total_orders}
        平均订单价值：¥{avg_order_value:.2f}
        
        分类销售情况：
        {chr(10).join([f"- {cat}: ¥{data['total']:.2f} ({data['count']}件)" for cat, data in category_sales.items()])}
        """
        
        prompt = SALES_ANALYSIS_PROMPT.format(data_summary=data_summary)
        try:
            response = self.llm.invoke(prompt)
            llm_analysis = response.content
        except Exception as e:
            llm_analysis = f"LLM调用失败: {str(e)}"
        
        return {
            "summary": {
                "total_sales": total_sales,
                "total_orders": total_orders,
                "avg_order_value": avg_order_value,
                "category_sales": category_sales
            },
            "llm_analysis": llm_analysis
        }