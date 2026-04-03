import uuid
import os
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from webapp.services.ml_analysis import PlacementAnalysisPipeline
from webapp.config import DATA_PATH, CHARTS_DIR

router = APIRouter()
templates = Jinja2Templates(directory="webapp/templates")

executor = ThreadPoolExecutor(max_workers=2)
task_store = {}


@router.get("/analysis")
async def analysis_page(request: Request):
    return templates.TemplateResponse("analysis/dashboard.html", {"request": request})


def _run_pipeline(task_id: str):
    progress = task_store[task_id]['progress']
    output_dir = os.path.join(CHARTS_DIR, task_id)
    try:
        pipeline = PlacementAnalysisPipeline(DATA_PATH, output_dir, progress)
        results = pipeline.run_all()
        task_store[task_id]['results'] = results
    except Exception as e:
        progress.update(phase=0, total=7, message=f"Error: {str(e)}", done=True, error=True)


@router.post("/api/analysis/run")
async def run_analysis():
    task_id = uuid.uuid4().hex[:12]
    task_store[task_id] = {
        'progress': {'phase': 0, 'total': 7, 'message': 'Starting...', 'done': False, 'error': False},
        'results': None,
    }
    executor.submit(_run_pipeline, task_id)
    return {'task_id': task_id}


@router.get("/api/analysis/status/{task_id}")
async def get_status(task_id: str):
    task = task_store.get(task_id)
    if not task:
        return {"error": "Task not found"}
    return task['progress']


@router.get("/api/analysis/results/{task_id}")
async def get_results(task_id: str):
    task = task_store.get(task_id)
    if not task or not task['results']:
        return {"error": "Results not ready"}
    return task['results']


@router.get("/api/analysis/chart/{task_id}/{chart_name}")
async def get_chart(task_id: str, chart_name: str):
    chart_path = os.path.join(CHARTS_DIR, task_id, chart_name)
    if not os.path.exists(chart_path):
        return {"error": "Chart not found"}
    return FileResponse(chart_path, media_type='image/png')


@router.get("/api/analysis/pdf/{task_id}")
async def download_pdf(task_id: str):
    task = task_store.get(task_id)
    if not task or not task['results']:
        return {"error": "Results not ready"}
    pdf_path = task['results']['pdf_path']
    if not os.path.exists(pdf_path):
        return {"error": "PDF not found"}
    return FileResponse(pdf_path, media_type='application/pdf',
                        filename='Placement_Analysis_Report.pdf')
