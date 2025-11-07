from __future__ import annotations

import io
from typing import Dict, List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from .models import RenderRequest, ResumeData, TemplateMetadata
from .resume_parser import parse_resume
from .templates.definitions import TemplateDefinition, build_templates

app = FastAPI(title="Construtor de Currículos API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEMPLATES: Dict[str, TemplateDefinition] = build_templates()


@app.get("/templates", response_model=List[TemplateMetadata])
def list_templates() -> List[TemplateMetadata]:
    """Retorna a lista de layouts disponíveis com metadados em português."""

    return [template.metadata for template in TEMPLATES.values()]


@app.post("/resume/parse", response_model=ResumeData)
async def parse_resume_endpoint(file: UploadFile = File(...)) -> ResumeData:
    """Realiza o upload de um currículo e retorna as informações estruturadas."""

    try:
        contents = await file.read()
        resume = parse_resume(contents, file.filename)
        return resume
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - proteção genérica
        raise HTTPException(status_code=500, detail="Erro ao processar o arquivo") from exc


@app.post("/resume/render")
async def render_resume(request: RenderRequest) -> StreamingResponse:
    """Gera um currículo baseado no layout escolhido e nos dados fornecidos."""

    template = TEMPLATES.get(request.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Layout não encontrado")

    resume = request.resume
    output_format = request.format.lower()

    if output_format == "docx":
        content = template.docx_renderer(resume)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"curriculo-{template.metadata.id}.docx"
    elif output_format == "pdf":
        content = template.pdf_renderer(resume)
        media_type = "application/pdf"
        filename = f"curriculo-{template.metadata.id}.pdf"
    else:
        raise HTTPException(status_code=400, detail="Formato não suportado")

    return StreamingResponse(
        io.BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@app.get("/health")
def healthcheck() -> JSONResponse:
    """Endpoint simples para monitoramento da API."""

    return JSONResponse({"status": "ok"})
