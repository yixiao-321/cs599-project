from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.api.routes import router
from app.config import config
import uvicorn
import os

app = FastAPI(title="E-commerce Analytics Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(['html', 'xml']),
    cache_size=0
)

app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    template = env.get_template("index.html")
    return HTMLResponse(content=template.render(request=request))

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    template = env.get_template("dashboard.html")
    return HTMLResponse(content=template.render(request=request))

@app.get("/reports", response_class=HTMLResponse)
async def reports(request: Request):
    template = env.get_template("reports.html")
    return HTMLResponse(content=template.render(request=request))

@app.get("/alerts", response_class=HTMLResponse)
async def alerts(request: Request):
    template = env.get_template("alerts.html")
    return HTMLResponse(content=template.render(request=request))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )