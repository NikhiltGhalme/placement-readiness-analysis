import os
from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from webapp.services.data_generator import generate_dataset
from webapp.config import GENERATED_DIR

router = APIRouter()
templates = Jinja2Templates(directory="webapp/templates")


class GenerateRequest(BaseModel):
    n_records: int = Field(default=1000, ge=100, le=10000)
    seed: int = Field(default=42)


@router.get("/generator")
async def generator_page(request: Request):
    return templates.TemplateResponse("generator/generate.html", {"request": request})


@router.post("/api/generator/generate")
async def generate_data(req: GenerateRequest):
    filepath, summary = generate_dataset(req.n_records, req.seed, GENERATED_DIR)
    return summary


@router.get("/api/generator/download/{filename}")
async def download_file(filename: str):
    filepath = os.path.join(GENERATED_DIR, filename)
    if not os.path.exists(filepath):
        return {"error": "File not found"}
    return FileResponse(filepath, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        filename=filename)
