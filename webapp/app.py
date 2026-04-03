from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from webapp.routes import readiness, analysis, generator

app = FastAPI(title="Placement Readiness Analysis System")

app.mount("/static", StaticFiles(directory="webapp/static"), name="static")
app.mount("/output", StaticFiles(directory="webapp/output"), name="output")

templates = Jinja2Templates(directory="webapp/templates")

app.include_router(readiness.router)
app.include_router(analysis.router)
app.include_router(generator.router)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
