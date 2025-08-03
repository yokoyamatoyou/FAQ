
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from docx import Document
import io

def extract_text_from_url(url):
    """Fetch and clean text content from the given URL.

    Raises:
        requests.exceptions.RequestException: ネットワーク関連のエラーが発生した場合。
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTPエラーをチェック
        soup = BeautifulSoup(response.text, 'html.parser')
        # スクリプトやスタイルタグを除去
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        # 複数の空白や改行を一つにまとめる
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        return text
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"URLからのテキスト抽出エラー: {e}"
        ) from e

def extract_text_from_pdf(file_path):
    """Extract text from a PDF file."""
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        raise RuntimeError(f"PDFからのテキスト抽出エラー: {e}") from e

def extract_text_from_docx(file_path):
    """Extract text from a DOCX file."""
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        raise RuntimeError(f"DOCXからのテキスト抽出エラー: {e}") from e

# Streamlitのfile_uploaderでアップロードされたファイルオブジェクトを処理するための関数
def extract_text_from_uploaded_file(uploaded_file, file_type):
    """Handle text extraction for Streamlit-uploaded files."""
    if file_type == "pdf":
        try:
            # アップロードされたファイルのバイトデータを直接使用
            doc = fitz.open(stream=uploaded_file.getvalue(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            raise RuntimeError(f"PDFからのテキスト抽出エラー: {e}") from e
    elif file_type == "docx":
        try:
            # アップロードされたファイルのバイトデータを直接使用
            doc = Document(io.BytesIO(uploaded_file.getvalue()))
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            raise RuntimeError(f"DOCXからのテキスト抽出エラー: {e}") from e
    else:
        raise ValueError("サポートされていないファイル形式です。")



