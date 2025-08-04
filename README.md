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
pip install -r requirements.txt
```

## Running the Streamlit app

1. Optionally set your OpenAI API key as an environment variable:
    ```bash
    export OPENAI_API_KEY=your_api_key  # On Windows use `setx OPENAI_API_KEY your_api_key`
    ```
2. Launch the app:
    ```bash
    streamlit run app.py
    ```
3. A browser window will open. Enter an API key if you didn't set one, choose an OpenAI model in the sidebar (defaults to `gpt-4o-mini`), then provide a URL or upload a PDF/DOCX file to generate Q&A pairs.

## Export formats

After generating Q&A data, the app can export files suitable for different workflows.

**Streamlit UI**

1. In the export section, choose either **RAG用データでダウンロード** or **ファインチューニング用データでダウンロード**.
2. A new download button appears. Click **RAG用データをダウンロード** or **ファインチューニング用データをダウンロード** to save the generated file.

**Python API**

```python
from qna_generator.data_exporter import export_for_rag, export_for_finetuning

rag_file = export_for_rag(qa_data)          # -> rag_data_YYYYMMDD_HHMMSS.jsonl
finetune_file = export_for_finetuning(qa_data)  # -> finetuning_data_YYYYMMDD_HHMMSS.jsonl
```

Both functions generate [JSON Lines](https://jsonlines.org/) files containing one record per line.

## Model configuration

The "Settings" sidebar includes a **model** selector. The chosen model is used for both category and Q&A generation.
Supported options include `gpt-4o-mini` and `gpt-4o`.

When using the generator programmatically, pass the model name to `AIQAGenerator`:

```python
from qna_generator.ai_qa_generator import AIQAGenerator
generator = AIQAGenerator(api_key="YOUR_API_KEY", model="gpt-4o")
```

## Documentation

Further details about the Q&A generation process and data formats are available in the module's own documentation: [`qna_generator/README.md`](qna_generator/README.md).

## Advanced Settings

The application exposes several helper functions that tune how questions are produced and how source text is handled.

### Temperature control

- **`calculate_temperature_step(question_count, max_temp=0.8, increment=0.1)`** –
  decides how many questions are generated before the temperature is raised. The
  step size is derived from the total number of questions and the temperature range.
- **`increment_temperature(current_temp, increment=0.1, max_temp=0.8)`** – raises
  the temperature by `increment` without exceeding `max_temp`.

**Example:** If the sidebar is set to **カテゴリごとの質問数 = 10** and
**1回の生成での質問数 = 2**, then `calculate_temperature_step(10)` returns `2`.
During generation the temperature starts at `0.0` and `increment_temperature`
raises it to `0.1`, `0.2`, and so on after every two questions.

### Text chunking

- **`split_text_into_chunks(text, max_tokens)`** – divides the extracted text into
  chunks of up to `max_tokens` words (the app uses `max_tokens=3000`). Adjusting
  `max_tokens` allows processing smaller or larger chunks. This value can be
  exposed in the sidebar as an advanced option if you need to tune chunk size.

