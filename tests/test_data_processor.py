import io
import sys
from pathlib import Path

import fitz
import pytest
import requests
from docx import Document

sys.path.append(str(Path(__file__).resolve().parent.parent))
from qna_generator.data_processor import (
    MAX_UPLOAD_SIZE,
    extract_text_from_uploaded_file,
    extract_text_from_url,
    extract_text_from_pdf,
    extract_text_from_docx,
)


class DummyUpload:
    def __init__(self, data: bytes):
        self._file = io.BytesIO(data)
        self.size = len(data)

    def read(self, *args):
        return self._file.read(*args)

    def seek(self, *args):
        return self._file.seek(*args)


def create_pdf_bytes(text: str) -> bytes:
    buf = io.BytesIO()
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    doc.save(buf)
    return buf.getvalue()


def create_pdf_file(tmp_path, text: str) -> Path:
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(create_pdf_bytes(text))
    return pdf_path


def create_docx_file(tmp_path, text: str) -> Path:
    docx_path = tmp_path / "sample.docx"
    doc = Document()
    doc.add_paragraph(text)
    doc.save(docx_path)
    return docx_path


def test_extract_text_from_url_success(monkeypatch):
    class DummyResponse:
        text = "<html><body><p>Hello</p></body></html>"

        def raise_for_status(self):
            pass

    def mock_get(url, timeout, headers):  # pragma: no cover - simple mock
        return DummyResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    text = extract_text_from_url("http://example.com")
    assert "Hello" in text


def test_extract_text_from_url_error(monkeypatch):
    def mock_get(url, timeout, headers):  # pragma: no cover - simple mock
        raise requests.exceptions.RequestException("error")

    monkeypatch.setattr(requests, "get", mock_get)
    with pytest.raises(requests.exceptions.RequestException):
        extract_text_from_url("http://example.com")


def test_extract_text_from_pdf(tmp_path):
    pdf_path = create_pdf_file(tmp_path, "PDF Test")
    text = extract_text_from_pdf(str(pdf_path))
    assert "PDF Test" in text


def test_extract_text_from_pdf_error():
    with pytest.raises(RuntimeError):
        extract_text_from_pdf("missing.pdf")


def test_extract_text_from_docx(tmp_path):
    docx_path = create_docx_file(tmp_path, "DOCX Test")
    text = extract_text_from_docx(str(docx_path))
    assert "DOCX Test" in text


def test_extract_text_from_docx_error():
    with pytest.raises(RuntimeError):
        extract_text_from_docx("missing.docx")


def test_extract_text_from_uploaded_pdf():
    pdf_bytes = create_pdf_bytes("Test")
    upload = DummyUpload(pdf_bytes)
    result = extract_text_from_uploaded_file(upload, "pdf")
    assert "Test" in result


def test_extract_text_file_size_limit():
    large_data = b"0" * (MAX_UPLOAD_SIZE + 1)
    upload = DummyUpload(large_data)
    with pytest.raises(ValueError):
        extract_text_from_uploaded_file(upload, "pdf")
