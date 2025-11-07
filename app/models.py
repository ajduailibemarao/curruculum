from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ModeloPortugues(BaseModel):
    class Config:
        allow_population_by_field_name = True
        allow_population_by_alias = True


class ContactInfo(ModeloPortugues):
    full_name: str = Field(..., alias="nome_completo", description="Nome completo do candidato")
    email: Optional[str] = Field(None, alias="email", description="Endereço de e-mail")
    phone: Optional[str] = Field(None, alias="telefone", description="Número de telefone")
    location: Optional[str] = Field(None, alias="localizacao", description="Cidade/país")
    website: Optional[str] = Field(None, alias="site", description="Site pessoal ou portfólio")
    linkedin: Optional[str] = Field(None, alias="linkedin", description="Perfil do LinkedIn")


class ExperienceItem(ModeloPortugues):
    role: str = Field(..., alias="cargo", description="Cargo do profissional")
    company: Optional[str] = Field(None, alias="empresa", description="Empresa onde trabalhou")
    start_date: Optional[str] = Field(None, alias="data_inicio", description="Data de início (texto livre)")
    end_date: Optional[str] = Field(None, alias="data_fim", description="Data de término (texto livre)")
    summary: Optional[str] = Field(None, alias="resumo", description="Resumo das responsabilidades")
    highlights: List[str] = Field(default_factory=list, alias="conquistas", description="Principais conquistas")


class EducationItem(ModeloPortugues):
    degree: str = Field(..., alias="curso", description="Nome do curso ou grau acadêmico")
    institution: Optional[str] = Field(None, alias="instituicao", description="Instituição de ensino")
    start_date: Optional[str] = Field(None, alias="data_inicio", description="Data de início (texto livre)")
    end_date: Optional[str] = Field(None, alias="data_fim", description="Data de conclusão (texto livre)")
    summary: Optional[str] = Field(None, alias="detalhes", description="Informações adicionais sobre o curso")


class ProjectItem(ModeloPortugues):
    name: str = Field(..., alias="nome", description="Nome do projeto")
    description: Optional[str] = Field(None, alias="descricao", description="Descrição do projeto")
    link: Optional[str] = Field(None, alias="link", description="URL relacionada ao projeto")


class ResumeData(ModeloPortugues):
    contact: ContactInfo = Field(..., alias="contato")
    professional_summary: Optional[str] = Field(None, alias="resumo_profissional", description="Resumo profissional em texto livre")
    experiences: List[ExperienceItem] = Field(default_factory=list, alias="experiencias")
    educations: List[EducationItem] = Field(default_factory=list, alias="formacoes")
    skills: List[str] = Field(default_factory=list, alias="competencias", description="Lista de habilidades")
    projects: List[ProjectItem] = Field(default_factory=list, alias="projetos")


class RenderRequest(ModeloPortugues):
    template_id: str = Field(..., alias="layout_id", description="Identificador do layout escolhido")
    format: str = Field(..., alias="formato", pattern="^(pdf|docx)$", description="Formato de saída desejado")
    resume: ResumeData = Field(..., alias="curriculo")


class TemplateMetadata(ModeloPortugues):
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="nome")
    description: str = Field(..., alias="descricao")
    tags: List[str] = Field(default_factory=list, alias="etiquetas")
