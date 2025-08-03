# Q&A Generator Module

This package provides utilities for generating question–answer datasets. It extracts text from URLs or uploaded files, uses OpenAI models to create categorized Q&A pairs, and exports results to several formats.

## Components

- **`ai_qa_generator.py`** – defines `AIQAGenerator` for proposing categories and generating Q&A pairs through the OpenAI API.
- **`data_processor.py`** – functions like `extract_text_from_url` and `extract_text_from_uploaded_file` to pull plain text from web pages or uploaded PDF/DOCX files.
- **`data_exporter.py`** – utilities (`export_to_jsonl`, `export_to_json`, `export_to_csv`, `export_for_rag`, `export_for_finetuning`) for saving generated data in multiple formats.

## Basic usage

```python
from qna_generator import (
    AIQAGenerator,
    extract_text_from_url,
    export_to_jsonl,
)

# Extract text from a web page
text = extract_text_from_url("https://example.com")

# Generate categories and Q&A pairs
generator = AIQAGenerator(api_key="YOUR_API_KEY")
categories = generator.generate_categories(text)
qa_pairs = generator.generate_qa_for_category(text, categories[0])

# Export Q&A data
export_to_jsonl(qa_pairs, "qa_data.jsonl")
```

These utilities are designed to be used by the Streamlit app in the repository root but can also be integrated into other Python projects.

