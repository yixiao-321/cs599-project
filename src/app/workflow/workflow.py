from langgraph.graph import StateGraph, END
from app.agent.sales_analyzer import SalesAnalyzer
from app.agent.anomaly_detector import AnomalyDetector
from app.agent.report_generator import ReportGenerator
from app.agent.visualization_agent import VisualizationAgent
from app.models.database import get_db
from typing import TypedDict, Any

class ReportState(TypedDict):
    days: int
    sales_analysis: Any
    anomaly_report: Any
    visualizations: Any
    final_report: Any

class ReportWorkflow:
    def __init__(self):
        self.graph = StateGraph(ReportState)
        self._build_graph()
    
    def _build_graph(self):
        self.graph.add_node("analyze_sales", self._analyze_sales)
        self.graph.add_node("detect_anomalies", self._detect_anomalies)
        self.graph.add_node("generate_report", self._generate_report)
        self.graph.add_node("generate_visualizations", self._generate_visualizations)
        
        self.graph.add_edge("analyze_sales", "detect_anomalies")
        self.graph.add_edge("detect_anomalies", "generate_visualizations")
        self.graph.add_edge("generate_visualizations", "generate_report")
        self.graph.add_edge("generate_report", END)
        
        self.graph.set_entry_point("analyze_sales")
    
    def _analyze_sales(self, state):
        db = next(get_db())
        analyzer = SalesAnalyzer(db)
        result = analyzer.analyze_sales_trend(days=state.get("days", 7))
        state["sales_analysis"] = result
        return state
    
    def _detect_anomalies(self, state):
        db = next(get_db())
        detector = AnomalyDetector(db)
        result = detector.generate_anomaly_report()
        state["anomaly_report"] = result
        return state
    
    def _generate_visualizations(self, state):
        db = next(get_db())
        viz_agent = VisualizationAgent(db)
        
        sales_trend = viz_agent.generate_sales_trend_chart(days=state.get("days", 7))
        category_chart = viz_agent.generate_category_sales_chart()
        inventory_chart = viz_agent.generate_inventory_chart()
        
        state["visualizations"] = {
            "sales_trend": sales_trend,
            "category_chart": category_chart,
            "inventory_chart": inventory_chart
        }
        return state
    
    def _generate_report(self, state):
        db = next(get_db())
        generator = ReportGenerator(db)
        
        if state.get("days", 7) == 1:
            report = generator.generate_daily_report()
        else:
            report = generator.generate_weekly_report()
        
        state["final_report"] = report
        return state
    
    def run(self, days: int = 7):
        initial_state = {"days": days}
        app = self.graph.compile()
        return app.invoke(initial_state)

workflow = ReportWorkflow()