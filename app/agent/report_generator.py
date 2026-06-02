from datetime import datetime
from sqlalchemy.orm import Session
from app.llm.client import get_deepseek_client
from app.llm.prompts import REPORT_GENERATION_PROMPT, ALERT_SUMMARIZATION_PROMPT
from app.models.database import AlertRecord
from .sales_analyzer import SalesAnalyzer
from .anomaly_detector import AnomalyDetector

class ReportGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.llm = get_deepseek_client()
        self.sales_analyzer = SalesAnalyzer(db)
        self.anomaly_detector = AnomalyDetector(db)
    
    def _call_llm(self, prompt):
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"LLM调用失败: {str(e)}"
    
    def generate_daily_report(self):
        sales_analysis = self.sales_analyzer.analyze_sales_trend(days=1)
        
        if "error" in sales_analysis:
            return {
                "report": "暂无今日销售数据",
                "generated_at": datetime.utcnow(),
                "sales_summary": {
                    "total_sales": 0,
                    "total_orders": 0,
                    "avg_order_value": 0
                },
                "anomalies": []
            }
        
        anomaly_report = self.anomaly_detector.generate_anomaly_report()
        
        analysis_result = f"""
        【销售分析】
        {sales_analysis.get('llm_analysis', '')}
        
        【异常检测】
        {anomaly_report.get('llm_analysis', '')}
        
        【关键指标】
        - 总销售额: ¥{sales_analysis['summary']['total_sales']:.2f}
        - 订单数: {sales_analysis['summary']['total_orders']}
        - 平均订单价值: ¥{sales_analysis['summary']['avg_order_value']:.2f}
        """
        
        prompt = REPORT_GENERATION_PROMPT.format(analysis_result=analysis_result)
        report = self._call_llm(prompt)
        
        return {
            "report": report,
            "generated_at": datetime.utcnow(),
            "sales_summary": sales_analysis["summary"],
            "anomalies": anomaly_report.get("anomalies", [])
        }
    
    def generate_weekly_report(self):
        sales_analysis = self.sales_analyzer.analyze_sales_trend(days=7)
        
        if "error" in sales_analysis:
            return {
                "report": "暂无本周销售数据",
                "generated_at": datetime.utcnow(),
                "sales_summary": {
                    "total_sales": 0,
                    "total_orders": 0,
                    "avg_order_value": 0
                },
                "anomalies": []
            }
        
        anomaly_report = self.anomaly_detector.generate_anomaly_report()
        
        analysis_result = f"""
        【周销售分析】
        {sales_analysis.get('llm_analysis', '')}
        
        【本周异常检测】
        {anomaly_report.get('llm_analysis', '')}
        
        【周关键指标】
        - 总销售额: ¥{sales_analysis['summary']['total_sales']:.2f}
        - 订单数: {sales_analysis['summary']['total_orders']}
        - 平均订单价值: ¥{sales_analysis['summary']['avg_order_value']:.2f}
        """
        
        prompt = REPORT_GENERATION_PROMPT.format(analysis_result=analysis_result)
        report = self._call_llm(prompt)
        
        return {
            "report": report,
            "generated_at": datetime.utcnow(),
            "sales_summary": sales_analysis["summary"],
            "anomalies": anomaly_report.get("anomalies", [])
        }
    
    def generate_alert_summary(self):
        alerts = self.db.query(AlertRecord).filter(
            AlertRecord.resolved == False
        ).order_by(AlertRecord.created_at.desc()).all()
        
        if not alerts:
            return {"message": "No active alerts", "total_alerts": 0, "alerts": []}
        
        alert_list = "\n".join([
            f"- [{a.severity.upper()}] {a.alert_type}: {a.message}" 
            for a in alerts
        ])
        
        prompt = ALERT_SUMMARIZATION_PROMPT.format(alerts=alert_list)
        summary = self._call_llm(prompt)
        
        return {
            "summary": summary,
            "total_alerts": len(alerts),
            "alerts": [
                {
                    "id": a.id,
                    "type": a.alert_type,
                    "message": a.message,
                    "severity": a.severity,
                    "created_at": a.created_at
                } for a in alerts
            ]
        }