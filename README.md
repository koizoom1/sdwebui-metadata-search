# Metadata Search Extension for Stable Diffusion WebUI

This project is an extension for Stable Diffusion WebUI that allows you to search and manage metadata in PNG files. With this extension, you can search metadata in PNG files within a specified folder and extract necessary information easily.

## Features

- Search metadata in PNG files within a specified folder
- Flexible search functionality using keywords or folder names
- Efficient display of search results with pagination
- Register and delete frequently used words
- Support for keywords containing spaces or enclosed in double quotes

## Installation

1. **Install the extension**
   - Open the "Extensions" tab in Stable Diffusion WebUI.
   - Enter the following URL in the "Install from URL" input field:
     - `https://github.com/koizoom1/sdwebui-metadata-search.git`
   - Click the "Install" button.

2. **Restart WebUI**
   - After the extension is installed, restart the WebUI.

## Usage

1. **Specify a folder**
   - In the main screen, specify the folder to be searched.
   - Use the "Use Last Folder" button to reuse the previously selected folder.

2. **Enter keywords**
   - Enter the keywords to search in the keyword input field.
   - Use the dropdown for frequently used words to easily add registered words.

3. **Search**
   - Click the "Search" button to search for metadata in PNG files within the specified folder.
   - The search results will be displayed in an HTML table format, showing image previews and metadata.

4. **Navigate pages**
   - If the results span multiple pages, use the "Previous Page" and "Next Page" buttons to navigate.

5. **Manage frequently used words**
   - Use the "Add Word" tab to register new words, and the "Delete Word" tab to remove unnecessary words.

## Contributing

1. **Fork this repository**
   - Fork this repository to your GitHub account.

2. **Make changes**
   - Clone the forked repository to your local machine and make changes.

3. **Submit a pull request**
   - Push your changes to the repository and create a pull request.

## Notes

- The PNG files must have appropriate metadata embedded for this extension to work.
- Python version 3.8 or higher is required.

## License

This project is released under the MIT License. For more details, see the `LICENSE` file.

このプロジェクトは、Stable Diffusion WebUI向けの拡張機能で、PNGファイルのメタデータを検索および管理するためのツールです。この拡張機能を使用することで、指定したフォルダ内のPNGファイルからメタデータを検索し、簡単に必要な情報を抽出できます。

## 機能

- 指定したフォルダ内のPNGファイルのメタデータを検索
- キーワードやフォルダ名を使った柔軟な検索機能
- ページネーションによる検索結果の効率的な表示
- よく使う単語の登録・削除機能
- 半角スペースを含むキーワードやダブルクオーテーション対応

## インストール方法

1. **拡張機能のインストール**
   - Stable Diffusion WebUIの「Extensions」タブを開きます。
   - 「Install from URL」の入力欄に以下のURLを入力します:
     - `https://github.com/koizoom1/sdwebui-metadata-search.git`
   - 「Install」ボタンを押します。

2. **WebUIの再起動**
   - 拡張機能のインストールが完了したら、WebUIを再起動してください。

## 使用方法

1. **フォルダの指定**
   - メイン画面で、検索対象となるフォルダを指定します。
   - 以前のフォルダを利用する場合は「前回のフォルダを用いる」ボタンを使用できます。

2. **キーワード入力**
   - キーワード入力欄に検索したい単語を入力します。
   - よく使う単語のドロップダウンを利用して、登録された単語を簡単に追加できます。

3. **検索**
   - 「検索」ボタンをクリックすると、指定されたフォルダ内のPNGファイルのメタデータが検索されます。
   - 検索結果はHTMLテーブル形式で表示され、画像プレビューやメタデータを確認できます。

4. **ページ移動**
   - 結果が複数ページにわたる場合は、「前のページ」や「次のページ」ボタンを使用して移動します。

5. **よく使う単語の管理**
   - 「単語登録」タブで新しい単語を登録し、「単語削除」タブで不要な単語を削除できます。

## 開発・貢献方法

1. **このリポジトリをフォーク**
   - あなたのGitHubアカウントにフォークしてください。

2. **変更を行う**
   - フォークしたリポジトリをローカルにクローンして変更を加えます。

3. **プルリクエストを送信**
   - 変更内容をリポジトリにプッシュし、プルリクエストを作成してください。

## 注意事項

- 対応するPNGファイルには、適切なメタデータが埋め込まれている必要があります。
- サポートされるPythonバージョンは、3.8以上です。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細については`LICENSE`ファイルをご確認ください。
