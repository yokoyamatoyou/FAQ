
from openai import OpenAI
import os
import re
import logging

logger = logging.getLogger(__name__)

class AIQAGenerator:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def generate_categories(self, text, temperature=0.0, num_categories=3):
        prompt = f"""以下のテキストから、関連性の高いカテゴリを{num_categories}つ提案してください。カテゴリは簡潔な名詞で、カンマ区切りで出力してください。\n\nテキスト:\n{text}\n\nカテゴリ:"""
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
            return [c.strip() for c in categories.split(",")][:num_categories]
        except Exception as e:
            return [f"カテゴリ生成エラー: {e}"]

    def generate_qa_for_category(self, text, category, temperature=0.0, num_questions=5):
        format_lines = []
        for i in range(1, num_questions + 1):
            format_lines.extend([
                f"質問{i}: [質問内容]",
                f"回答{i}: [回答内容]",
                f"引用元{i}: [引用元のテキスト]",
                "",
            ])
        format_example = "\n".join(format_lines).strip()
        prompt = (
            f"以下のテキストとカテゴリに基づいて、ユーザーが最も知りたいであろう質問とそれに対する回答を{num_questions}つ生成してください。"
            "回答は必ず提供されたテキストの内容のみから生成し、引用元を明確にしてください。引用元はテキストの該当箇所を特定できる形で示してください。"
            f"\n\nカテゴリ: {category}\nテキスト:\n{text}\n\n形式:\n{format_example}"
        )
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
        key_pattern = re.compile(r"^(質問|回答|引用元)\s*\d*$")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            segments = [seg.strip() for seg in line.split(":", 1)]
            if len(segments) != 2:
                logger.warning("Skipping malformed line: %s", line)
                continue
            key_part, value_part = segments
            if not key_part or not value_part:
                logger.warning("Skipping malformed line: %s", line)
                continue
            key_match = key_pattern.match(key_part)
            if not key_match:
                logger.warning("Skipping malformed line: %s", line)
                continue
            key_jp = key_match.group(1)
            value = value_part
            if key_jp == "質問":
                if current_qa:
                    if all(k in current_qa for k in ("question", "answer", "source")):
                        qa_list.append(current_qa)
                    else:
                        logger.warning("Incomplete QA pair skipped: %s", current_qa)
                current_qa = {"question": value}
            elif key_jp == "回答":
                if current_qa:
                    current_qa["answer"] = value
                else:
                    logger.warning("Answer without question: %s", line)
            elif key_jp == "引用元":
                if current_qa:
                    current_qa["source"] = value
                else:
                    logger.warning("Source without question: %s", line)
        if current_qa:
            if all(k in current_qa for k in ("question", "answer", "source")):
                qa_list.append(current_qa)
            else:
                logger.warning("Incomplete QA pair skipped: %s", current_qa)
        return qa_list



