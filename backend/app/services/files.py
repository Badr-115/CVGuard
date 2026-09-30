from pathlib import Path
from uuid import uuid4

from docx import Document
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader

from ..core.config import settings

ALLOWED = {
    ".pdf": {"application/pdf", "application/octet-stream"},
    ".docx": {
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/octet-stream",
    },
}


def safe_filename(filename: str) -> str:
    name = Path(filename or "upload").name
    cleaned = "".join(c for c in name if c.isalnum() or c in "._-")[:120]
    return cleaned or "upload"


async def save_resume(upload: UploadFile) -> tuple[str, str]:
    filename = safe_filename(upload.filename or "upload")
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED:
        raise HTTPException(400, "Unsupported file type. Use PDF or DOCX.")
    if upload.content_type not in ALLOWED[suffix]:
        raise HTTPException(400, "Invalid MIME type for the selected file type.")

    max_bytes = settings.max_upload_mb * 1024 * 1024
    data = await upload.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(413, f"File too large. Maximum size is {settings.max_upload_mb} MB.")
    if not data:
        raise HTTPException(400, "Uploaded file is empty.")

    base = Path(settings.storage_dir).resolve() / "resumes"
    base.mkdir(parents=True, exist_ok=True)
    path = base / f"{uuid4().hex}{suffix}"
    path.write_bytes(data)

    try:
        if suffix == ".pdf":
            reader = PdfReader(str(path))
            if reader.is_encrypted:
                raise HTTPException(400, "Encrypted PDF files are not supported.")
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            doc = Document(str(path))
            text = "\n".join(p.text for p in doc.paragraphs)
    except HTTPException:
        path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise HTTPException(400, "The resume could not be parsed as a valid PDF or DOCX file.") from exc

    return str(path), text[:1_000_000]
