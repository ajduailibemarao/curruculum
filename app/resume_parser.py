from __future__ import annotations

import io
import re
from typing import Dict, Iterable, List, Tuple

import pdfplumber
from docx import Document

from .models import ContactInfo, EducationItem, ExperienceItem, ProjectItem, ResumeData

SECTION_KEYWORDS: Dict[str, Tuple[str, ...]] = {
    "experience": (
        "experience",
        "experiência",
        "experiencia",
        "work history",
        "histórico profissional",
        "trajetória",
        "carreira",
    ),
    "education": (
        "education",
        "formação",
        "formacao",
        "formação acadêmica",
        "formacao academica",
        "academic",
        "educação",
        "educacao",
    ),
    "skills": ("skills", "competências", "competencias", "habilidades"),
    "projects": ("projects", "projetos", "realizações"),
    "summary": ("summary", "resumo", "resumo profissional", "perfil", "objetivo"),
}


def _read_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def _read_pdf(file_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        pages_text = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages_text)


def _normalize_lines(text: str) -> List[str]:
    lines = [line.strip() for line in text.splitlines()]
    return [line for line in lines if line]


def _detect_section(line: str) -> str | None:
    normalized = line.lower()
    for section, keywords in SECTION_KEYWORDS.items():
        if any(re.search(rf"\b{re.escape(keyword)}\b", normalized) for keyword in keywords):
            return section
    return None


def _split_sections(lines: Iterable[str]) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {key: [] for key in SECTION_KEYWORDS}
    sections["header"] = []
    current = "header"
    for line in lines:
        detected = _detect_section(line)
        if detected:
            current = detected
            continue
        sections.setdefault(current, []).append(line)
    return sections


def _extract_contact(header_lines: List[str]) -> ContactInfo:
    if not header_lines:
        return ContactInfo(full_name="Nome não identificado")

    full_name = header_lines[0]
    contact_details = " ".join(header_lines[1:]) if len(header_lines) > 1 else ""

    email_match = re.search(r"[\w\.\-+]+@[\w\-]+\.[\w\.-]+", contact_details)
    phone_match = re.search(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,3}\)?[\s-]?)?\d{4,5}[\s-]?\d{4}", contact_details)
    linkedin_match = re.search(r"linkedin\.com/[^\s]+", contact_details, flags=re.IGNORECASE)
    website_match = re.search(r"https?://[^\s]+", contact_details)

    location_match = None
    if "," in contact_details:
        parts = [part.strip() for part in contact_details.split(",") if len(part.strip()) > 2]
        if parts:
            location_match = parts[-1]

    return ContactInfo(
        full_name=full_name,
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
        location=location_match,
        website=website_match.group(0) if website_match else None,
        linkedin=linkedin_match.group(0) if linkedin_match else None,
    )


def _parse_experience(lines: List[str]) -> List[ExperienceItem]:
    experiences: List[ExperienceItem] = []
    buffer: List[str] = []
    for line in lines + [""]:
        if line.strip() == "" and buffer:
            experiences.append(_experience_from_block(buffer))
            buffer = []
        else:
            buffer.append(line)
    return experiences


def _experience_from_block(lines: List[str]) -> ExperienceItem:
    header = lines[0]
    summary_lines = lines[1:]

    company = None
    role = header
    date_pattern = re.compile(r"(\d{4}|\w+\s\d{4}).*(\d{4}|presente|atual)", re.IGNORECASE)
    date_match = date_pattern.search(header)

    if "-" in header:
        parts = [part.strip() for part in header.split("-", maxsplit=1)]
        if len(parts) == 2:
            company = parts[0]
            role = parts[1]

    start_date = end_date = None
    if date_match:
        date_text = date_match.group(0)
        start_end = re.split(r"-|–", date_text)
        if len(start_end) == 2:
            start_date = start_end[0].strip()
            end_date = start_end[1].strip()
        summary_lines = [line for line in summary_lines if date_text not in line]

    highlights = [line.strip("- ") for line in summary_lines if line.strip()]

    return ExperienceItem(
        role=role.strip(),
        company=company,
        start_date=start_date,
        end_date=end_date,
        highlights=highlights,
    )


def _parse_education(lines: List[str]) -> List[EducationItem]:
    educations: List[EducationItem] = []
    for line in lines:
        if not line:
            continue
        parts = [part.strip() for part in re.split(r" - | \u2013 |,", line) if part.strip()]
        degree = parts[0]
        institution = parts[1] if len(parts) > 1 else None
        summary = ", ".join(parts[2:]) if len(parts) > 2 else None
        educations.append(EducationItem(degree=degree, institution=institution, summary=summary))
    return educations


def _parse_skills(lines: List[str]) -> List[str]:
    skills_text = " ".join(lines)
    if ";" in skills_text:
        return [skill.strip() for skill in skills_text.split(";") if skill.strip()]
    if "," in skills_text:
        return [skill.strip() for skill in skills_text.split(",") if skill.strip()]
    return [line.strip("- ") for line in lines if line.strip()]


def _parse_projects(lines: List[str]) -> List[ProjectItem]:
    projects: List[ProjectItem] = []
    for line in lines:
        if not line:
            continue
        parts = [part.strip() for part in re.split(r" - | \u2013 |:|,", line) if part.strip()]
        name = parts[0]
        description = ", ".join(parts[1:]) if len(parts) > 1 else None
        link_match = re.search(r"https?://[^\s]+", line)
        projects.append(ProjectItem(name=name, description=description, link=link_match.group(0) if link_match else None))
    return projects


def parse_resume(file_bytes: bytes, filename: str) -> ResumeData:
    if filename.lower().endswith(".pdf"):
        text = _read_pdf(file_bytes)
    elif filename.lower().endswith((".doc", ".docx")):
        text = _read_docx(file_bytes)
    else:
        raise ValueError("Formato de arquivo não suportado. Utilize PDF ou Word.")

    lines = _normalize_lines(text)
    sections = _split_sections(lines)

    contact = _extract_contact(sections.get("header", []))
    experiences = _parse_experience(sections.get("experience", []))
    educations = _parse_education(sections.get("education", []))
    skills = _parse_skills(sections.get("skills", []))
    projects = _parse_projects(sections.get("projects", []))

    summary_lines = sections.get("summary", [])
    professional_summary = " ".join(summary_lines) if summary_lines else None

    return ResumeData(
        contact=contact,
        professional_summary=professional_summary,
        experiences=experiences,
        educations=educations,
        skills=skills,
        projects=projects,
    )
