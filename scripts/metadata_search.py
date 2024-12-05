import os
import json
import pandas as pd
import gradio as gr
from PIL import Image
from PIL.ExifTags import TAGS
from modules import script_callbacks
import html
import re

# 設定ファイルの保存場所
EXTENSION_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # 一つ上のフォルダ
SETTING_FILE = os.path.join(EXTENSION_DIR, "setting.json")

# 設定ファイルを読み込む
def load_settings():
    if os.path.exists(SETTING_FILE):
        with open(SETTING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"remembered_folder": "", "common_words": []}

# 設定ファイルを保存する
def save_settings(settings):
    with open(SETTING_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

# よく使う単語の登録
def add_common_word(word, description):
    settings = load_settings()
    settings["common_words"].append({"word": word, "description": description})
    save_settings(settings)
    return [
        f"{cw['word']} ({cw['description']})" if cw["description"] else cw["word"]
        for cw in settings["common_words"]
    ]

def extract_metadata_from_png(folder_path):
    metadata_list = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                file_path = os.path.join(root, file)
                try:
                    with Image.open(file_path) as img:
                        metadata = img.info
                        # Extract Exif data for JPEG and WEBP
                        if img.format in ["JPEG", "WEBP"]:
                            exif_data = img._getexif()
                            if exif_data:
                                exif_metadata = {}
                                for tag, value in exif_data.items():
                                    decoded_tag = TAGS.get(tag, tag)
                                    # Exclude the 'exif' tag
                                    if decoded_tag == "exif":
                                        continue
                                    # Handle UserComment field
                                    if decoded_tag == "UserComment" and isinstance(value, bytes):
                                        try:
                                            # Remove UNICODE header and null bytes
                                            if value.startswith(b'UNICODE\x00\x00'):
                                                value = value[9:]  # Remove 'UNICODE\x00\x00'
                                            value = value.replace(b'\x00', b'')  # Remove null bytes
                                            value = value.decode('utf-8')  # Decode bytes to string
                                        except Exception as e:
                                            print(f"Error decoding UserComment: {e}")
                                    exif_metadata[decoded_tag] = value
                                metadata.update(exif_metadata)
                        metadata_list.append({
                            "ImagePath": file_path.replace("\\", "/"),
                            "FolderPath": os.path.dirname(file_path).replace("\\", "/"),
                            "Metadata": "\n".join([f"{k}: {v}" for k, v in metadata.items() if k != "exif"]),
                        })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return pd.DataFrame(metadata_list)

# ページネーション
def paginate_results(results, page, items_per_page):
    start = (page - 1) * items_per_page
    end = start + items_per_page
    return results[start:end]

# キーワードの強調表示
def highlight_keywords(text, keywords):
    sanitized_text = html.escape(text)  # サニタイズ
    for keyword in keywords:
        if keyword:
            sanitized_text = sanitized_text.replace(
                html.escape(keyword),
                f"<b>{html.escape(keyword)}</b>"
            )
    return sanitized_text

def parse_keywords(keywords):
    # 正規表現でダブルクオーテーションで囲まれたフレーズを抽出
    phrases = re.findall(r'"(.*?)"', keywords)
    # ダブルクオーテーション部分を除いてスペース区切りの単語を抽出
    remaining_keywords = re.sub(r'"(.*?)"', '', keywords).split()
    # 抽出したフレーズと単語を結合してリストを返す
    return phrases + remaining_keywords

# メタデータ検索処理
def search_metadata_with_images(folder_path, keywords, page, items_per_page):
    if not folder_path or not os.path.exists(folder_path):
        return "<p>フォルダが存在しません。</p>", "1/1"

    # 設定を保存
    settings = load_settings()
    settings["remembered_folder"] = folder_path  # 検索に使用したフォルダを保存
    save_settings(settings)

    # items_per_page が None の場合のデフォルト値を設定
    if not items_per_page:
        items_per_page = 20  # デフォルト値を設定

    df = extract_metadata_from_png(folder_path)
    if df.empty:
        return "<p>指定されたフォルダにはメタデータを持つPNGファイルがありません。</p>", "1/1"

    # キーワード解析と検索
    keyword_list = parse_keywords(keywords)
    results = df[df.apply(
        lambda row: all(kw.lower() in row["Metadata"].lower() or kw.lower() in row["FolderPath"].lower() for kw in keyword_list),
        axis=1
    )]
    if results.empty:
        return "<p>該当するメタデータが見つかりませんでした。</p>", "1/1"

    # ページネーション
    total_pages = (len(results) + items_per_page - 1) // items_per_page
    paginated_results = paginate_results(results.to_dict(orient="records"), page, items_per_page)

    # 表形式のHTMLを作成
    html_content = """
    <style>
        .metadata-table {
            width: 100%;
            border-collapse: collapse;
        }
        .metadata-table th, .metadata-table td {
            border: 1px solid black;
            padding: 5px;
            text-align: left;
            vertical-align: top;
        }
        .metadata-table .image-cell img {
            width: 300px;
        }
        .metadata-table .metadata-cell pre {
            max-width: 600px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
    <table class="metadata-table">
        <tr>
            <th>画像</th>
            <th>メタデータ</th>
        </tr>
    """
    for result in paginated_results:
        image_html = f"<img src='http://127.0.0.1:7860/file={html.escape(result['ImagePath'])}' />"
        metadata_highlighted = highlight_keywords(result["Metadata"], keyword_list)
        folder_highlighted = highlight_keywords(result["FolderPath"], keyword_list)

        html_content += f"""
        <tr>
            <td class="image-cell">{image_html}</td>
            <td class="metadata-cell">
                <pre>フォルダ: {folder_highlighted}\n{metadata_highlighted}</pre>
            </td>
        </tr>
        """
    html_content += "</table>"

    # 現在ページ/総ページ数
    current_page_info = f"{page}/{total_pages}"

    return html_content, current_page_info

def on_page_change(folder_path, keyword, page, items_per_page):
    if not items_per_page:  # items_per_pageがNoneの場合はエラー防止のため20を設定
        items_per_page = 20
    return search_metadata_with_images(folder_path, keyword, int(page), int(items_per_page))

# Gradio UIの作成
def create_ui():
    settings = load_settings()

    with gr.Blocks(analytics_enabled=False) as interface:
        # 検索対象フォルダの指定
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    folder_path_input = gr.Textbox(
                        label="Search Folder",
                        value=settings["remembered_folder"],
                        placeholder="Enter the full path of the folder",
                        interactive=True
                    )
                    load_button = gr.Button("Use Last Folder")
                    load_button.click(
                        lambda: settings["remembered_folder"],
                        inputs=[],
                        outputs=folder_path_input
                    )

                # キーワード入力とよく使う単語リスト
                keyword_input = gr.Textbox(label="Search Keywords", placeholder="Enter keywords separated by spaces. Use double quotes for phrases")
                with gr.Row():
                    common_word_dropdown = gr.Dropdown(
                        label="Frequently Used Words",
                        choices=[f"{cw['word']} ({cw['description']})" if cw["description"] else cw["word"] for cw in settings["common_words"]],
                        interactive=True
                    )

                    # 表示件数
                    items_per_page_input = gr.Dropdown(
                        choices=["10", "20", "50", "100"],
                        value="20",
                        label="Items Per Page"
                    )

                    def update_keyword(selected, current_keywords):
                        if isinstance(selected, list):  # リストの場合は最初の要素を取得
                            selected = selected[0]

                        if not selected:
                            return current_keywords

                        # 選択された単語を抽出（"単語 (説明)" の場合は "単語" のみ取得）
                        if " (" in selected:
                            selected = selected.split(" (")[0]

                        # 選択された単語が半角スペースを含むかチェック
                        if " " in selected and not (selected.startswith('"') and selected.endswith('"')):
                            selected = f'"{selected}"'  # ダブルクオーテーションで囲む

                        # キーワード欄が空でない場合、スペースを挿入
                        if current_keywords:
                            return f"{current_keywords} {selected}"
                        else:
                            return selected

                    common_word_dropdown.change(
                        fn=update_keyword,
                        inputs=[common_word_dropdown, keyword_input],  # 現在のキーワードも渡す
                        outputs=[keyword_input]
                    )

                    search_button = gr.Button("Search")

        # 単語管理タブ
            with gr.Column():
                with gr.Tab("Add Word"):
                    word_input = gr.Textbox(label="Word", placeholder="Enter a word to register")
                    description_input = gr.Textbox(label="Description", placeholder="Description of the word (optional)")
                    save_word_button = gr.Button("Save")

                    def add_word(word, description):
                        settings = load_settings()
                        settings["common_words"].append({"word": word, "description": description})
                        save_settings(settings)
                        updated_list = [
                            f"{cw['word']} ({cw['description']})" if cw["description"] else cw["word"]
                            for cw in settings["common_words"]
                        ]
                        return updated_list

                    save_word_button.click(
                        fn=add_word,
                        inputs=[word_input, description_input],
                        outputs=[common_word_dropdown]
                    )

                with gr.Tab("Delete Word"):
                    delete_word_dropdown = gr.Dropdown(
                        label="Select a Word to Delete",
                        choices=[f"{cw['word']} ({cw['description']})" if cw["description"] else cw["word"] for cw in settings["common_words"]]
                    )
                    delete_word_button = gr.Button("Delete")

                    def delete_word(selected_word):
                        settings = load_settings()
                        target_word = selected_word.split(" (")[0]
                        settings["common_words"] = [cw for cw in settings["common_words"] if cw["word"] != target_word]
                        save_settings(settings)
                        updated_list = [
                            f"{cw['word']} ({cw['description']})" if cw["description"] else cw["word"]
                            for cw in settings["common_words"]
                        ]
                        return updated_list

                    delete_word_button.click(
                        fn=delete_word,
                        inputs=[delete_word_dropdown],
                        outputs=[common_word_dropdown, delete_word_dropdown]
                    )
        with gr.Row():
            prev_page_button = gr.Button("◀")
            page_input = gr.Textbox(label="Page", value="1")
            next_page_button = gr.Button("▶")
        page_info_output = gr.Textbox(label="Current Page/Total Pages", interactive=False)
        results_gallery = gr.HTML(label="Search Results")



        # 次のページボタン
        next_page_button.click(
            lambda page: str(int(page) + 1),
            inputs=[page_input],
            outputs=[page_input]
        )

        # 前のページボタン
        prev_page_button.click(
            lambda page: str(max(int(page) - 1, 1)),
            inputs=[page_input],
            outputs=[page_input]
        )


        with gr.Row():
            results_gallery = gr.HTML(label="検索結果")
            # 検索ボタンのクリックイベント
            search_button.click(
                fn=lambda folder_path, keyword, items_per_page: search_metadata_with_images(
                    folder_path, keyword, 1, int(items_per_page)
                ),
                inputs=[folder_path_input, keyword_input, items_per_page_input],
                outputs=[results_gallery, page_info_output]
            ).then(
                lambda _: 1,
                inputs=[],
                outputs=page_input
            )
        # ページ変更時に再検索
        page_input.change(
            fn=on_page_change,
            inputs=[folder_path_input, keyword_input, page_input, items_per_page_input],
            outputs=[results_gallery, page_info_output]
        )
    return interface

# UIタブに登録
def on_ui_tabs():
    return [(create_ui(), "Image Metadata Search", "metadata_search_tab")]

script_callbacks.on_ui_tabs(on_ui_tabs)
