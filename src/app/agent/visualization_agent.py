import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import SalesRecord, InventoryRecord

class VisualizationAgent:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_sales_trend_chart(self, days: int = 30):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        sales_data = self.db.query(SalesRecord).filter(
            SalesRecord.sale_date >= start_date
        ).all()
        
        if not sales_data:
            return {"error": "No data available"}
        
        dates = [sr.sale_date.date() for sr in sales_data]
        amounts = [sr.total_amount for sr in sales_data]
        
        fig = px.line(
            x=dates,
            y=amounts,
            title=f"Sales Trend (Last {days} Days)",
            labels={"x": "Date", "y": "Amount (¥)"},
            template="plotly_dark"
        )
        
        return fig.to_html(full_html=False)
    
    def generate_category_sales_chart(self):
        sales_data = self.db.query(SalesRecord).all()
        
        if not sales_data:
            return {"error": "No data available"}
        
        category_totals = {}
        for sr in sales_data:
            if sr.category not in category_totals:
                category_totals[sr.category] = 0
            category_totals[sr.category] += sr.total_amount
        
        fig = px.pie(
            values=list(category_totals.values()),
            names=list(category_totals.keys()),
            title="Sales by Category",
            template="plotly_dark"
        )
        
        return fig.to_html(full_html=False)
    
    def generate_inventory_chart(self):
        inventory = self.db.query(InventoryRecord).all()
        
        if not inventory:
            return {"error": "No inventory data available"}
        
        product_names = [item.product_name for item in inventory]
        stock_quantities = [item.stock_quantity for item in inventory]
        thresholds = [item.threshold for item in inventory]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=product_names,
            y=stock_quantities,
            name='Current Stock',
            marker_color='rgb(58, 71, 80)'
        ))
        fig.add_trace(go.Scatter(
            x=product_names,
            y=thresholds,
            name='Threshold',
            mode='lines+markers',
            line=dict(color='red', dash='dash')
        ))
        
        fig.update_layout(
            title='Inventory Status',
            xaxis_title='Product',
            yaxis_title='Quantity',
            template="plotly_dark"
        )
        
        return fig.to_html(full_html=False)
    
    def generate_sales_summary_stats(self, days: int = 30):
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        sales_data = self.db.query(SalesRecord).filter(
            SalesRecord.sale_date >= start_date
        ).all()
        
        if not sales_data:
            return {"error": "No data available"}
        
        total_sales = sum(sr.total_amount for sr in sales_data)
        total_orders = len(sales_data)
        avg_order_value = total_sales / total_orders if total_orders > 0 else 0
        
        return {
            "total_sales": round(total_sales, 2),
            "total_orders": total_orders,
            "avg_order_value": round(avg_order_value, 2),
            "period": f"Last {days} days"
        }