from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .api.routes import router
from .config import config
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

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

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

@app.get("/products", response_class=HTMLResponse)
async def products(request: Request):
    template = env.get_template("products.html")
    return HTMLResponse(content=template.render(request=request))

@app.get("/inventory", response_class=HTMLResponse)
async def inventory(request: Request):
    template = env.get_template("inventory.html")
    return HTMLResponse(content=template.render(request=request))

@app.get("/reports-traditional", response_class=HTMLResponse)
async def reports_traditional(request: Request):
    template = env.get_template("reports_traditional.html")
    return HTMLResponse(content=template.render(request=request))

@app.get("/alerts-traditional", response_class=HTMLResponse)
async def alerts_traditional(request: Request):
    template = env.get_template("alerts_traditional.html")
    return HTMLResponse(content=template.render(request=request))

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )