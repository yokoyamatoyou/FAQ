from openai import OpenAI
import logging
import json

logger = logging.getLogger(__name__)


class AIQAGenerator:
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_categories(self, text, temperature=0.0, num_categories=3):
        prompt = f"""以下のテキストから、関連性の高いカテゴリを{num_categories}つ提案してください。カテゴリは簡潔な名詞で、カンマ区切りで出力してください。\n\nテキスト:\n{text}\n\nカテゴリ:"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたはテキストからカテゴリを抽出するAIアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=50
            )
            categories = response.choices[0].message.content.strip()
            return [c.strip() for c in categories.split(",")][:num_categories]
        except Exception as e:
            return [f"カテゴリ生成エラー: {e}"]

    def generate_qa_for_category(self, text, category, temperature=0.0, num_questions=5):
        prompt = (
            f"以下のテキストとカテゴリに基づいて、ユーザーが最も知りたいであろう質問とそれに対する回答を{num_questions}つ生成してください。"
            "回答は必ず提供されたテキストの内容のみから生成し、引用元を明確にしてください。"
            "以下のJSON形式で、余計な説明やマークダウンを含めずに出力してください:\n"
            "{\n"
            '  "qa_pairs": [\n'
            '    {"question": "質問内容", "answer": "回答内容", "source": "引用元のテキスト"}\n'
            "  ]\n"
            "}\n"
            f"カテゴリ: {category}\nテキスト:\n{text}"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたはテキストから質問と回答を生成するAIアシスタントです。回答は必ず提供されたテキストの内容のみから生成し、引用元を明確にしてください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=1000
            )
            qa_pairs_raw = response.choices[0].message.content.strip()
            return json.loads(qa_pairs_raw)
        except Exception as e:
            return {"error": f"Q&A生成エラー: {e}"}
