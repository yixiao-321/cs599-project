from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.models.database import get_db, SalesRecord, InventoryRecord, CustomerRecord, AlertRecord, User
from app.services.user_service import verify_password, init_default_users
from app.agent.sales_analyzer import SalesAnalyzer
from app.agent.anomaly_detector import AnomalyDetector
from app.agent.report_generator import ReportGenerator
from app.agent.visualization_agent import VisualizationAgent
from app.agent.chat_agent import ChatAgent
from app.workflow.workflow import workflow
from datetime import datetime, timedelta

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