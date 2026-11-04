import asyncio
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile

from app.services.files import safe_filename, save_resume
from app.core.config import settings


def test_safe_filename_is_basename_and_sanitized():
    assert safe_filename("../some file.pdf") == "somefile.pdf"


def test_corrupt_resume_is_rejected_and_removed(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "storage_dir", str(tmp_path))
    uploaded = UploadFile(file=BytesIO(b"not a valid PDF"), filename="resume.pdf")
    uploaded.headers = uploaded.headers  # Uploaded file metadata supplied below
    # Starlette's UploadFile content_type is obtained from its headers.
    from starlette.datastructures import Headers
    uploaded.headers = Headers({"content-type": "application/pdf"})
    with pytest.raises(HTTPException) as exc:
        asyncio.run(save_resume(uploaded))
    assert exc.value.status_code == 400
    assert list(Path(tmp_path).rglob("*.pdf")) == []


def test_oversized_resume_is_rejected(tmp_path, monkeypatch):
    from starlette.datastructures import Headers
    monkeypatch.setattr(settings, "storage_dir", str(tmp_path))
    monkeypatch.setattr(settings, "max_upload_mb", 1)
    uploaded = UploadFile(
        file=BytesIO(b"x" * (1024 * 1024 + 1)),
        filename="resume.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(save_resume(uploaded))
    assert exc.value.status_code == 413
