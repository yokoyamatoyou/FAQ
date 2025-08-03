import io
import sys
from pathlib import Path

import fitz
import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))
from qna_generator.data_processor import (
    MAX_UPLOAD_SIZE,
    extract_text_from_uploaded_file,
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
