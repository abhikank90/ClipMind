from fastapi import APIRouter, HTTPException, Depends
import logging

from app.schemas.compilation import CompilationCreate, CompilationResponse
from app.services.compilation_service import CompilationService
from app.core.dependencies import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=CompilationResponse)
async def create_compilation(
    compilation: CompilationCreate,
    current_user: dict = Depends(get_current_user)
):
    service = CompilationService()
    result = await service.create_compilation(compilation, current_user["id"])
    return result

@router.get("/{compilation_id}", response_model=CompilationResponse)
async def get_compilation(
    compilation_id: str,
    current_user: dict = Depends(get_current_user)
):
    service = CompilationService()
    compilation = await service.get_compilation(compilation_id, current_user["id"])
    if not compilation:
        raise HTTPException(status_code=404, detail="Compilation not found")
    return compilation

@router.get("/", response_model=list[CompilationResponse])
async def list_compilations(
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    service = CompilationService()
    compilations = await service.list_compilations(current_user["id"], skip, limit)
    return compilations

@router.post("/{compilation_id}/render")
async def render_compilation(
    compilation_id: str,
    current_user: dict = Depends(get_current_user)
):
    service = CompilationService()
    job_id = await service.render_compilation(compilation_id, current_user["id"])
    return {
        "compilation_id": compilation_id,
        "job_id": job_id,
        "status": "rendering"
    }
