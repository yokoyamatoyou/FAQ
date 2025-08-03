import streamlit as st
import json
import os
import requests
from qna_generator.data_processor import extract_text_from_url, extract_text_from_uploaded_file
from qna_generator.ai_qa_generator import AIQAGenerator
from qna_generator.data_exporter import (
    export_to_jsonl,
    export_to_json,
    export_to_csv,
    export_for_rag,
    export_for_finetuning,
)
from qna_generator.utils import calculate_temperature_step, increment_temperature


def _has_error_prefix(value: str) -> bool:
    """Return True if the text looks like an error message."""
    return isinstance(value, str) and value.startswith(("Error", "エラー"))

# ページ設定
st.set_page_config(
    page_title="Q&A自動生成システム",
    page_icon="🤖",
    layout="wide"
)

# セッション状態の初期化
if 'qa_data' not in st.session_state:
    st.session_state.qa_data = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'model' not in st.session_state:
    st.session_state.model = "gpt-4o-mini"

# タイトル
st.title("🤖 Q&A自動生成システム")
st.markdown("URL、PDF、DOCXファイルからQ&Aを自動生成します")

# サイドバー
with st.sidebar:
    st.header("設定")
    
    # OpenAI APIキー入力
    api_key = st.text_input(
        "OpenAI APIキー",
        type="password",
        value=st.session_state.api_key,
        help="OpenAI APIキーを入力してください"
    )
    st.session_state.api_key = api_key

    model = st.selectbox(
        "使用するモデル",
        ["gpt-4o-mini", "gpt-4o"],
        index=["gpt-4o-mini", "gpt-4o"].index(st.session_state.model),
        help="OpenAIのモデルを選択してください",
    )
    st.session_state.model = model

    num_categories = st.number_input(
        "生成するカテゴリ数",
        min_value=1,
        value=3,
        step=1,
        help="生成されるカテゴリの数",
    )

    # 生成する質問数とブロックサイズ
    question_mode = st.radio(
        "質問数の指定方法",
        ["カテゴリごとの質問数", "全カテゴリ合計質問数"],
        help="カテゴリ単位で固定数を生成するか、全カテゴリ合計で生成数を指定します",
    )
    if question_mode == "カテゴリごとの質問数":
        num_questions_input = st.number_input(
            "カテゴリごとの質問数",
            min_value=1,
            value=5,
            step=1,
            help="各カテゴリで生成する質問の総数",
        )
    else:
        num_questions_input = st.number_input(
            "全カテゴリ合計質問数",
            min_value=1,
            value=5,
            step=1,
            help="全カテゴリで生成する質問の総数",
        )
    block_size = st.number_input(
        "1回の生成での質問数",
        min_value=1,
        value=1,
        step=1,
        help="一度に生成する質問数",
    )

# メインコンテンツ
col1, col2 = st.columns([1, 1])

with col1:
    st.header("データ入力")
    
    # データ入力方法の選択
    input_method = st.radio(
        "データ入力方法を選択",
        ["URL", "ファイルアップロード"]
    )
    
    text_content = ""
    source_info = ""
    
    if input_method == "URL":
        url = st.text_input("URLを入力してください")
        if st.button("URLからテキストを抽出"):
            if url:
                with st.spinner("テキストを抽出中..."):
                    try:
                        result = extract_text_from_url(url)
                    except requests.exceptions.RequestException as e:
                        st.error(str(e))
                    else:
                        if _has_error_prefix(result):
                            st.error(result)
                        else:
                            text_content = result
                            source_info = f"URL: {url}"
                            st.success("テキストの抽出が完了しました")
            else:
                st.error("URLを入力してください")
    
    elif input_method == "ファイルアップロード":
        uploaded_file = st.file_uploader(
            "ファイルをアップロード",
            type=['pdf', 'docx'],
            help="PDFまたはDOCXファイルをアップロードしてください"
        )
        
        if uploaded_file is not None:
            file_type = uploaded_file.name.split('.')[-1].lower()
            if st.button("ファイルからテキストを抽出"):
                with st.spinner("テキストを抽出中..."):
                    try:
                        result = extract_text_from_uploaded_file(uploaded_file, file_type)
                    except Exception as e:
                        st.error(str(e))
                    else:
                        if _has_error_prefix(result):
                            st.error(result)
                        else:
                            text_content = result
                            source_info = f"ファイル: {uploaded_file.name}"
                            st.success("テキストの抽出が完了しました")
    
    # 抽出されたテキストの表示
    if text_content:
        st.subheader("抽出されたテキスト")
        st.text_area("", text_content[:1000] + "..." if len(text_content) > 1000 else text_content, height=200)

with col2:
    st.header("Q&A生成")
    
    if text_content and st.session_state.api_key:
        generator = AIQAGenerator(st.session_state.api_key, model=st.session_state.model)
        
        if st.button("カテゴリとQ&Aを生成"):
            with st.spinner("カテゴリを生成中..."):
                categories = generator.generate_categories(text_content, 0.0, num_categories)
            
            if categories and not any("エラー" in str(cat) for cat in categories):
                st.success(f"カテゴリが生成されました: {', '.join(categories)}")

                # 各カテゴリでQ&Aを生成
                if question_mode == "全カテゴリ合計質問数":
                    total_questions = num_questions_input
                    generated_category_count = len(categories)
                    base = total_questions // generated_category_count
                    remainder = total_questions % generated_category_count
                    per_category_counts = [base + (1 if i < remainder else 0) for i in range(generated_category_count)]
                else:
                    per_category_counts = [num_questions_input] * len(categories)

                all_success = True
                for category, target_count in zip(categories, per_category_counts):
                    current_temp = 0.0
                    generated = 0
                    step = calculate_temperature_step(target_count)
                    next_step = step
                    while generated < target_count:
                        num_to_generate = min(block_size, target_count - generated)
                        with st.spinner(f"カテゴリ「{category}」のQ&Aを生成中..."):
                            qa_pairs = generator.generate_qa_for_category(text_content, category, current_temp, num_questions=num_to_generate)

                        if qa_pairs and not any("error" in qa for qa in qa_pairs):
                            for qa in qa_pairs:
                                qa_data = {
                                    "category": category,
                                    "question": qa.get("question", ""),
                                    "answer": qa.get("answer", ""),
                                    "source": qa.get("source", ""),
                                    "source_info": source_info,
                                    "temperature": current_temp,
                                }
                                st.session_state.qa_data.append(qa_data)
                            generated += len(qa_pairs)

                            while generated >= next_step:
                                current_temp = increment_temperature(current_temp)
                                next_step += step
                        else:
                            error_messages = []
                            if qa_pairs:
                                for qa in qa_pairs:
                                    if isinstance(qa, dict) and "error" in qa:
                                        error_messages.append(qa.get("error", str(qa)))
                                    elif isinstance(qa, str):
                                        error_messages.append(qa)
                            if not error_messages:
                                error_messages = ["Q&Aの生成中に不明なエラーが発生しました"]
                            for msg in error_messages:
                                st.error(f"カテゴリ「{category}」でエラーが発生しました: {msg}")
                            st.info("問題が解消したら再度お試しください。")
                            all_success = False
                            break

                if all_success:
                    st.success("Q&Aの生成が完了しました")
            else:
                st.error(f"カテゴリ生成エラー: {categories}")
                st.info("設定を確認して再度お試しください。")
    
    elif not st.session_state.api_key:
        st.warning("OpenAI APIキーを入力してください")
    elif not text_content:
        st.warning("まずテキストを抽出してください")

# 生成されたQ&Aの表示
if st.session_state.qa_data:
    st.header("生成されたQ&A")
    
    # カテゴリ別に表示
    categories = list(set([qa["category"] for qa in st.session_state.qa_data]))
    
    for category in categories:
        st.subheader(f"カテゴリ: {category}")
        category_qa = [qa for qa in st.session_state.qa_data if qa["category"] == category]
        
        for i, qa in enumerate(category_qa):
            with st.expander(f"Q{i+1}: {qa['question'][:50]}..."):
                st.write(f"**質問:** {qa['question']}")
                st.write(f"**回答:** {qa['answer']}")
                
                # 引用元を折りたたみ表示
                with st.expander("引用元を表示"):
                    st.write(f"**引用元:** {qa['source']}")
                    st.write(f"**ソース:** {qa['source_info']}")
                    st.write(f"**温度設定:** {qa['temperature']}")
    
    # データクリア
    if st.button("Q&Aデータをクリア"):
        st.session_state.qa_data = []
        st.rerun()
    
    # データエクスポート機能
    st.header("データエクスポート")
    
    if st.session_state.qa_data:
        st.write(f"現在のQ&Aデータ数: {len(st.session_state.qa_data)}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("JSON形式でダウンロード"):
                filename = export_to_json(st.session_state.qa_data)
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="JSONファイルをダウンロード",
                        data=f.read(),
                        file_name=filename,
                        mime="application/json"
                    )
        
        with col2:
            if st.button("CSV形式でダウンロード"):
                filename = export_to_csv(st.session_state.qa_data)
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="CSVファイルをダウンロード",
                        data=f.read(),
                        file_name=filename,
                        mime="text/csv"
                    )
        
        with col3:
            if st.button("JSONL形式でダウンロード"):
                filename = export_to_jsonl(st.session_state.qa_data)
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="JSONLファイルをダウンロード",
                        data=f.read(),
                        file_name=filename,
                        mime="application/json"
                    )
        
        st.subheader("AI開発用エクスポート")
        
        col4, col5 = st.columns(2)
        
        with col4:
            if st.button("RAG用データでダウンロード"):
                filename = export_for_rag(st.session_state.qa_data)
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="RAG用データをダウンロード",
                        data=f.read(),
                        file_name=filename,
                        mime="application/json"
                    )
        
        with col5:
            if st.button("ファインチューニング用データでダウンロード"):
                filename = export_for_finetuning(st.session_state.qa_data)
                with open(filename, 'rb') as f:
                    st.download_button(
                        label="ファインチューニング用データをダウンロード",
                        data=f.read(),
                        file_name=filename,
                        mime="application/json"
                    )
    else:
        st.info("エクスポートするQ&Aデータがありません。まずQ&Aを生成してください。")


