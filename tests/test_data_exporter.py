import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))
from qna_generator.data_exporter import (
    export_to_jsonl,
    export_to_json,
    export_to_csv,
    export_for_rag,
    export_for_finetuning,
)

SAMPLE_QA = [
    {
        "question": "Q1",
        "answer": "A1",
        "category": "cat",
        "source": "src",
        "source_info": "info",
        "temperature": 0.5,
    }
]


def test_export_to_jsonl(tmp_path):
    filename = tmp_path / "data.jsonl"
    returned = export_to_jsonl(SAMPLE_QA, str(filename))
    assert returned == str(filename)
    assert filename.exists()
    with open(filename, encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    assert lines == SAMPLE_QA


def test_export_to_json(tmp_path):
    filename = tmp_path / "data.json"
    returned = export_to_json(SAMPLE_QA, str(filename))
    assert returned == str(filename)
    assert filename.exists()
    with open(filename, encoding="utf-8") as f:
        content = json.load(f)
    assert content == SAMPLE_QA


def test_export_to_csv(tmp_path):
    filename = tmp_path / "data.csv"
    returned = export_to_csv(SAMPLE_QA, str(filename))
    assert returned == str(filename)
    assert filename.exists()
    with open(filename, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows == [
        {
            "question": "Q1",
            "answer": "A1",
            "category": "cat",
            "source": "src",
            "source_info": "info",
            "temperature": "0.5",
        }
    ]


def test_export_for_rag(tmp_path):
    filename = tmp_path / "rag.jsonl"
    returned = export_for_rag(SAMPLE_QA, str(filename))
    assert returned == str(filename)
    assert filename.exists()
    with open(filename, encoding="utf-8") as f:
        items = [json.loads(line) for line in f]
    expected = [
        {
            "id": "cat_0",
            "text": "質問: Q1\n回答: A1",
            "metadata": {
                "category": "cat",
                "source": "src",
                "source_info": "info",
                "temperature": 0.5,
            },
        }
    ]
    assert items == expected


def test_export_for_finetuning(tmp_path):
    filename = tmp_path / "finetuning.jsonl"
    returned = export_for_finetuning(SAMPLE_QA, str(filename))
    assert returned == str(filename)
    assert filename.exists()
    with open(filename, encoding="utf-8") as f:
        items = [json.loads(line) for line in f]
    expected = [
        {
            "messages": [
                {
                    "role": "system",
                    "content": "あなたはcatに関する質問に答えるアシスタントです。",
                },
                {"role": "user", "content": "Q1"},
                {"role": "assistant", "content": "A1"},
            ]
        }
    ]
    assert items == expected
