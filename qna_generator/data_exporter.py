import json
import csv
from datetime import datetime

def export_to_jsonl(qa_data, filename=None):
    """Q&AデータをJSONL形式でエクスポート"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qa_data_{timestamp}.jsonl"
    
    with open(filename, 'w', encoding='utf-8') as f:
        for qa in qa_data:
            json.dump(qa, f, ensure_ascii=False)
            f.write('\n')
    
    return filename

def export_to_json(qa_data, filename=None):
    """Q&AデータをJSON形式でエクスポート"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qa_data_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(qa_data, f, ensure_ascii=False, indent=2)
    
    return filename

def export_to_csv(qa_data, filename=None):
    """Q&AデータをCSV形式でエクスポート"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qa_data_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        if qa_data:
            fieldnames = qa_data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(qa_data)
    
    return filename

def export_for_rag(qa_data, filename=None):
    """RAG用のフォーマットでエクスポート"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rag_data_{timestamp}.jsonl"
    
    rag_data = []
    for qa in qa_data:
        rag_item = {
            "id": f"{qa['category']}_{len(rag_data)}",
            "text": f"質問: {qa['question']}\n回答: {qa['answer']}",
            "metadata": {
                "category": qa['category'],
                "source": qa['source'],
                "source_info": qa['source_info'],
                "temperature": qa['temperature']
            }
        }
        rag_data.append(rag_item)
    
    with open(filename, 'w', encoding='utf-8') as f:
        for item in rag_data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
    
    return filename

def export_for_finetuning(qa_data, filename=None):
    """ファインチューニング用のフォーマットでエクスポート"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"finetuning_data_{timestamp}.jsonl"
    
    finetuning_data = []
    for qa in qa_data:
        finetuning_item = {
            "messages": [
                {"role": "system", "content": f"あなたは{qa['category']}に関する質問に答えるアシスタントです。"},
                {"role": "user", "content": qa['question']},
                {"role": "assistant", "content": qa['answer']}
            ]
        }
        finetuning_data.append(finetuning_item)
    
    with open(filename, 'w', encoding='utf-8') as f:
        for item in finetuning_data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
    
    return filename

