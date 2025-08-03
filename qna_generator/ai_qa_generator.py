
from openai import OpenAI
import os

class AIQAGenerator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_categories(self, text, temperature=0.0):
        prompt = f"""以下のテキストから、関連性の高いカテゴリを3つ提案してください。カテゴリは簡潔な名詞で、カンマ区切りで出力してください。\n\nテキスト:\n{text}\n\nカテゴリ:"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # GPT-4.1 nanoの代わりにgpt-4o-miniを使用
                messages=[
                    {"role": "system", "content": "あなたはテキストからカテゴリを抽出するAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=50
            )
            categories = response.choices[0].message.content.strip()
            return [c.strip() for c in categories.split(",")]
        except Exception as e:
            return [f"カテゴリ生成エラー: {e}"]

    def generate_qa_for_category(self, text, category, temperature=0.0):
        prompt = f"""以下のテキストとカテゴリに基づいて、ユーザーが最も知りたいであろう質問とそれに対する回答を5つ生成してください。回答は必ず提供されたテキストの内容のみから生成し、引用元を明確にしてください。引用元はテキストの該当箇所を特定できる形で示してください。\n\nカテゴリ: {category}\nテキスト:\n{text}\n\n形式:\n質問1: [質問内容]\n回答1: [回答内容]\n引用元1: [引用元のテキスト]\n\n質問2: [質問内容]\n回答2: [回答内容]\n引用元2: [引用元のテキスト]\n..."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # GPT-4.1 nanoの代わりにgpt-4o-miniを使用
                messages=[
                    {"role": "system", "content": "あなたはテキストから質問と回答を生成するAIアシスタントです。回答は必ず提供されたテキストの内容のみから生成し、引用元を明確にしてください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )
            qa_pairs_raw = response.choices[0].message.content.strip()
            qa_pairs = self._parse_qa_pairs(qa_pairs_raw)
            return qa_pairs
        except Exception as e:
            return [{"error": f"Q&A生成エラー: {e}"}]

    def _parse_qa_pairs(self, qa_text):
        qa_list = []
        lines = qa_text.split("\n")
        current_qa = {}
        for line in lines:
            line = line.strip()
            if line.startswith("質問"):
                if current_qa:
                    qa_list.append(current_qa)
                current_qa = {"question": line.split(": ", 1)[1]}
            elif line.startswith("回答"):
                current_qa["answer"] = line.split(": ", 1)[1]
            elif line.startswith("引用元"):
                current_qa["source"] = line.split(": ", 1)[1]
        if current_qa:
            qa_list.append(current_qa)
        return qa_list



