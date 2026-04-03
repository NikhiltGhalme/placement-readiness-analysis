import uuid
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from webapp.services.readiness_checker import StudentInput, analyze_student, compare_with_dataset
from webapp.services.pdf_report import generate_readiness_pdf
from webapp.config import DATA_PATH, REPORTS_DIR

router = APIRouter()
templates = Jinja2Templates(directory="webapp/templates")

# In-memory store for PDF downloads
_session_store = {}


@router.get("/readiness")
async def readiness_page(request: Request):
    return templates.TemplateResponse("readiness/checker.html", {"request": request})


@router.post("/api/readiness/check")
async def check_readiness(input_data: StudentInput):
    student = input_data.model_dump()
    analysis = analyze_student(student)
    comparison = compare_with_dataset(student, DATA_PATH)

    session_id = uuid.uuid4().hex
    _session_store[session_id] = {
        'student': student,
        'analysis': analysis,
        'comparison': comparison,
    }

    return {
        'session_id': session_id,
        'student': student,
        'analysis': analysis,
        'comparison': comparison,
    }


@router.get("/api/readiness/pdf/{session_id}")
async def download_readiness_pdf(session_id: str):
    data = _session_store.get(session_id)
    if not data:
        return {"error": "Session not found. Please run the check again."}

    pdf_path = generate_readiness_pdf(
        data['student'], data['analysis'], data['comparison'], REPORTS_DIR
    )
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f'readiness_report_{data["student"]["name"].replace(" ", "_")}.pdf'
    )
