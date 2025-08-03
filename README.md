# FAQ Streamlit App

This repository contains a Streamlit application for generating question–answer pairs from URLs or uploaded documents. The app extracts text, lets you create categorized Q&A using OpenAI models, and provides multiple export options.

## Installation

### Prerequisites
- Python 3.9 or later
- [OpenAI API key](https://platform.openai.com/)

### Setup
```bash
git clone <repository-url>
cd FAQ
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
pip install streamlit openai requests beautifulsoup4 python-docx pymupdf
```
*If a `requirements.txt` file becomes available, you can install dependencies with `pip install -r requirements.txt` instead.*

## Running the Streamlit app

1. Optionally set your OpenAI API key as an environment variable:
    ```bash
    export OPENAI_API_KEY=your_api_key  # On Windows use `setx OPENAI_API_KEY your_api_key`
    ```
2. Launch the app:
    ```bash
    streamlit run app.py
    ```
3. A browser window will open. Enter an API key if you didn't set one, then provide a URL or upload a PDF/DOCX file to generate Q&A pairs.

## Documentation

Further details about the Q&A generation process and data formats are available in the module's own documentation: [`qna_generator/qna_generator/README.md`](qna_generator/qna_generator/README.md).

