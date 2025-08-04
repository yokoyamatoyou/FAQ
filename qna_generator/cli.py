import argparse
import os
from typing import List

from qna_generator.ai_qa_generator import AIQAGenerator
from qna_generator.data_processor import (
    extract_text_from_url,
    extract_text_from_pdf,
    extract_text_from_docx,
)
from qna_generator.data_exporter import export_to_jsonl


def _read_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def _extract_text_from_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    if ext == ".docx":
        return extract_text_from_docx(path)
    raise ValueError(f"Unsupported file type: {path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Q&A pairs from URLs or local files."
    )
    parser.add_argument("--url-list", help="Text file containing URLs (one per line).")
    parser.add_argument(
        "--file-list", help="Text file containing file paths to PDF or DOCX files."
    )
    parser.add_argument(
        "--output", required=True, help="Output path for generated Q&A JSONL file."
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="OpenAI API key. Defaults to OPENAI_API_KEY environment variable.",
    )
    parser.add_argument(
        "--model", default="gpt-4o-mini", help="OpenAI model name to use."
    )
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        parser.error(
            "OpenAI API key must be provided via --api-key or OPENAI_API_KEY environment variable."
        )

    generator = AIQAGenerator(api_key=api_key, model=args.model)
    qa_data = []

    if args.url_list:
        for url in _read_lines(args.url_list):
            text = extract_text_from_url(url)
            categories = generator.generate_categories(text)
            for category in categories:
                result = generator.generate_qa_for_category(text, category)
                for qa in result.get("qa_pairs", []):
                    qa_data.append(
                        {
                            "question": qa.get("question", ""),
                            "answer": qa.get("answer", ""),
                            "category": category,
                            "source": qa.get("source", ""),
                            "source_info": f"URL: {url}",
                            "temperature": 0.0,
                        }
                    )

    if args.file_list:
        for path in _read_lines(args.file_list):
            text = _extract_text_from_file(path)
            categories = generator.generate_categories(text)
            for category in categories:
                result = generator.generate_qa_for_category(text, category)
                for qa in result.get("qa_pairs", []):
                    qa_data.append(
                        {
                            "question": qa.get("question", ""),
                            "answer": qa.get("answer", ""),
                            "category": category,
                            "source": qa.get("source", ""),
                            "source_info": f"File: {path}",
                            "temperature": 0.0,
                        }
                    )

    export_to_jsonl(qa_data, args.output)


if __name__ == "__main__":
    main()
