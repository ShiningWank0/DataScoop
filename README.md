# DataScoop

DataScoopは、yt-dlpを使用して動画や音声データを効率的にダウンロードするためのPythonアプリケーションです。ユーザーフレンドリーな対話型インターフェースを備え、YouTube、ニコニコ動画、Abemaからのコンテンツ取得を簡単に行えます。

## 特徴

- YouTube、ニコニコ動画、Abemaからの動画・音声ダウンロード
- ユーザーフレンドリーな対話型インターフェース
- 高品質な音声抽出
- 字幕のダウンロード対応
- 柔軟な出力形式の選択
- 設定の自動保存と読み込み
- 複数URLの一括処理
- 階層化された設計による拡張性
- **GUIでの出力ディレクトリ選択**
- **オリジナルタイトルの使用/不使用の選択**
- **URLごとのカスタムファイル名設定**
- **デフォルト設定使用時の出力オプションカスタマイズ**

## インストール

1. リポジトリをクローン:
   ```bash
   git clone https://github.com/yourusername/datascoop.git
   cd datascoop
   ```

2. 依存関係のインストール:

   ### pipを使用する場合
   ```bash
   pip install -r requirements.txt
   ```
   
   ### uvを使用する場合 (推奨)
   ```bash
   # uvがインストールされていない場合、まずuvをインストール
   pip install uv
   
   # uvを使って依存関係をインストール
   uv pip install -r requirements.txt
   # または
   uv add -r requirements.txt
   ```

## 使用方法

DataScoopはデフォルトで対話型インターフェースで動作します。コマンドラインから直接URLを指定することもできます。

### 対話モード（推奨）

```bash
# 対話モードで実行（デフォルト）
python -m datascoop

# またはuvを使用する場合
uv run python -m datascoop

# インストール後にコマンドとして実行
datascoop

# または明示的に対話モードを指定
python -m datascoop -i
# uvを使用する場合
uv run python -m datascoop -i
```

対話モードでは、初回実行時に設定を行い、その後は保存された設定を使用できます。また、複数のURLを簡単に入力できます。

対話モードの基本的な流れ：
1. 初回実行時は設定（コンテンツ種類、品質など）を対話形式で行う
2. URLを1行ずつ入力（複数のURLを入力可能、入力終了は空行）
3. 指定されたURLからコンテンツをダウンロード

### コマンドラインモード

```bash
# 動画をダウンロード
python -m datascoop https://www.youtube.com/watch?v=example
# uvを使用する場合
uv run python -m datascoop https://www.youtube.com/watch?v=example

# 音声のみをダウンロード
python -m datascoop https://www.youtube.com/watch?v=example -t audio
# uvを使用する場合
uv run python -m datascoop https://www.youtube.com/watch?v=example -t audio

# 出力ディレクトリとファイル名を指定
python -m datascoop https://www.youtube.com/watch?v=example -o my_downloads -f my_video
# uvを使用する場合
uv run python -m datascoop https://www.youtube.com/watch?v=example -o my_downloads -f my_video

# 字幕付きで動画をダウンロード
python -m datascoop https://www.youtube.com/watch?v=example --subtitles
# uvを使用する場合
uv run python -m datascoop https://www.youtube.com/watch?v=example --subtitles

# 音質を指定して音声をダウンロード
python -m datascoop https://www.youtube.com/watch?v=example -t audio --audio-format mp3
# uvを使用する場合
uv run python -m datascoop https://www.youtube.com/watch?v=example -t audio --audio-format mp3

# 対話モードを強制的に使用
python -m datascoop https://www.youtube.com/watch?v=example -i
# uvを使用する場合
uv run python -m datascoop https://www.youtube.com/watch?v=example -i
```

### Pythonコードとして使用

DataScoopは、Pythonライブラリとしても使用できます。以下は基本的な使用例です：

```python
from datascoop import VideoDownloader, AudioDownloader, YouTubeDownloader
from datascoop.interactive import InteractiveDownloader

# 基本的な動画ダウンロード
video_downloader = VideoDownloader(output_dir="downloads/videos")
video_file = video_downloader.download("https://www.youtube.com/watch?v=example")

# 音声をダウンロード
audio_downloader = AudioDownloader(output_dir="downloads/audio", audio_format="mp3")
audio_file = audio_downloader.download("https://www.youtube.com/watch?v=example")

# YouTube特化機能を使用
youtube_downloader = YouTubeDownloader(output_dir="downloads/youtube")
# プレイリストをダウンロード
playlist_files = youtube_downloader.download_playlist("https://www.youtube.com/playlist?list=example", max_videos=5)
# チャプター情報付き動画をダウンロード
chaptered_video = youtube_downloader.download_with_chapters("https://www.youtube.com/watch?v=example")

# 対話型インターフェースを使用
interactive = InteractiveDownloader()
interactive.start()
```

より詳細な使用例は `examples.py` ファイルを参照してください。

## 設定オプション

### コマンドラインオプション

| オプション | 説明 | デフォルト値 |
|------------|------|------------|
| `url` | ダウンロードするコンテンツのURL（指定するとコマンドラインモード） | - |
| `-i, --interactive` | URLを指定しても強制的に対話モードを使用 | False |
| `-t, --type` | ダウンロードするコンテンツの種類 (video/audio/both) | video |
| `-o, --output-dir` | 出力ディレクトリ | downloads |
| `-f, --filename` | 出力ファイル名（拡張子なし） | (自動生成) |
| `-q, --quality` | 動画/音声の品質 | best |
| `--audio-format` | 音声フォーマット (mp3, m4a, wav, flac) | mp3 |
| `--video-format` | 動画フォーマット (mp4, webm, mkv) | mp4 |
| `--subtitles` | 可能であれば字幕もダウンロード | False |
| `--batch-file` | URLリストを含むファイルからバッチダウンロード | - |
| `--list-formats` | 利用可能なフォーマットを表示 | False |
| `--version` | バージョン情報を表示 | False |
| `-v, --verbose` | 詳細なログを出力 | False |

### 対話モードの設定項目

対話モードでは、以下の設定項目を対話形式で設定できます。設定はユーザーのホームディレクトリ（`~/.datascoop/config.json`）に保存され、次回以降の実行時に自動的に読み込まれます。

| 設定項目 | 説明 | オプション |
|------------|------|------------|
| コンテンツ種類 | ダウンロードするコンテンツの種類 | 動画 / 音声 / 両方 |
| 出力ディレクトリ | ダウンロードファイルの保存先 | 任意のディレクトリパス |
| 動画品質 | ダウンロードする動画の品質 | 最高品質 / 高品質(1080p) / 中品質(720p) / 低品質(480p) / 最低品質(360p) |
| 動画フォーマット | 動画のファイル形式 | MP4 / WebM / MKV |
| 音声品質 | ダウンロードする音声の品質 | 高品質(192kbps) / 中品質(128kbps) / 低品質(96kbps) |
| 音声フォーマット | 音声のファイル形式 | MP3 / M4A / WAV / FLAC |
| 字幕 | 字幕をダウンロードするかどうか | はい / いいえ |
| 詳細ログ | 詳細なログ情報を出力するかどうか | はい / いいえ |
| オリジナルタイトル使用 | コンテンツ元のタイトルをファイル名として使用 | はい / いいえ |

### 新機能

#### GUIディレクトリ選択

出力ディレクトリをグラフィカルに選択できるようになりました。対話モード中にディレクトリのカスタマイズを選択すると、GUIまたはCUIでの入力を選べます。

#### デフォルト設定使用時の出力オプションカスタマイズ

デフォルト設定を使用する場合でも、出力ディレクトリやファイル形式のみを個別にカスタマイズできるようになりました。基本設定を変えずに、出力先のみを変更したい場合に便利です。

#### オリジナルタイトル設定

ダウンロードするコンテンツのオリジナルタイトルをそのままファイル名として使用するか、カスタム名を使用するかを選択できます。

#### URLごとの個別設定

複数のURLをダウンロードする場合、URLごとに個別の設定が可能になりました：

1. **個別ファイル名設定** - 各URLに対して異なるファイル名を指定できます
2. **個別出力ディレクトリ設定** - 各URLのダウンロード先を個別に指定できます
3. **個別タイトル使用設定** - URLごとにオリジナルタイトルを使用するかどうかを選択できます

これにより、例えば音楽は音楽フォルダに、ドキュメンタリーはドキュメントフォルダにと、コンテンツに応じた分類が一度の操作で可能になります。

## プロジェクト構造

DataScoopは階層化された設計を採用しており、機能ごとにモジュールが分割されています。以下はプロジェクトの主要なディレクトリとファイルの構造です：

```
DataScoop/
├── examples.py            # 使用例を示すサンプルスクリプト
├── pyproject.toml         # プロジェクト設定
├── requirements.txt       # 依存パッケージ一覧
├── README.md              # プロジェクト説明
├── setup.py               # セットアップスクリプト
└── datascoop/             # メインパッケージ
    ├── __init__.py        # パッケージ初期化
    ├── __main__.py        # モジュール実行用エントリーポイント
    ├── cli.py             # コマンドラインインターフェース
    ├── interactive.py     # 対話型インターフェース
    ├── downloaders/       # ダウンローダーモジュール
    │   ├── __init__.py
    │   ├── base.py        # 基底クラス
    │   ├── video.py       # 動画ダウンローダー
    │   ├── audio.py       # 音声ダウンローダー
    │   └── youtube.py     # YouTube特化ダウンローダー
    └── utils/             # ユーティリティ
        ├── __init__.py
        ├── config.py      # 設定管理
        └── helpers.py     # ヘルパー関数
```

### 主要なモジュールと役割

#### コアモジュール
- **datascoop/__main__.py**: モジュール実行用のエントリーポイント
- **datascoop/cli.py**: コマンドライン処理とメイン機能の実装
- **datascoop/interactive.py**: 対話型インターフェースの実装

#### ダウンローダー
- **downloaders/base.py**: すべてのダウンローダーの基底クラス `BaseDownloader`
- **downloaders/video.py**: 動画ダウンロード用の `VideoDownloader` クラス
- **downloaders/audio.py**: 音声ダウンロード用の `AudioDownloader` クラス
- **downloaders/youtube.py**: YouTube特化機能を持つ `YouTubeDownloader` クラス

#### ユーティリティ
- **utils/config.py**: 設定の保存・読み込みを管理する `ConfigManager` クラス
- **utils/helpers.py**: URL検証、プラットフォーム検出などのヘルパー関数

## 出力とデータフロー

### 対話モード実行時の出力例

```
DataScoopへようこそ！
前回の設定を読み込みました。

設定:
- コンテンツ種類: 動画
- 出力ディレクトリ: downloads
- 動画品質: 最高品質
- 動画フォーマット: MP4
- 字幕ダウンロード: いいえ
- オリジナルタイトル使用: はい

設定を変更しますか？ [y/N]: n

--- 出力オプション ---
出力ディレクトリまたはファイル形式をカスタマイズしますか？ [y/N]: y
何をカスタマイズしますか？
1. 出力ディレクトリのみ
2. ファイル形式のみ
3. 両方
番号を入力してください [3]: 3
設定はダウンロードするURLごとに個別に行いますか？ [Y/n]: y

ダウンロードURLを入力してください (終了するには 'exit' または 'q' を入力):
複数のURLを入力する場合は、1行に1つずつ入力してください。
入力が終わったら空行を入力してください。

URL: https://www.youtube.com/watch?v=example1
GUIでディレクトリを選択しますか？ [Y/n]: y
出力ディレクトリを設定しました: /Videos
ダウンロードするコンテンツのタイトルをそのままファイル名として使用しますか？ [Y/n]: n
ファイル名を指定してください: custom_video

URL: https://www.youtube.com/watch?v=example2
GUIでディレクトリを選択しますか？ [Y/n]: y
出力ディレクトリを設定しました: /animals
ダウンロードするコンテンツのタイトルをそのままファイル名として使用しますか？ [Y/n]: y

URL: 

2個のURLを受け付けました。ダウンロードを開始します...

[1/2] https://www.youtube.com/watch?v=example1 をダウンロード中...
ダウンロード完了: /Videos/custom_video.mp4

[2/2] https://www.youtube.com/watch?v=example2 をダウンロード中...
ダウンロード完了: /animals/example2.mp4

すべてのダウンロードが完了しました。

DataScoopを終了します。
```

### 出力ディレクトリ構造

コンテンツ種類が「動画」または「音声」の場合：
```
<output_dir>/
└── ダウンロードされたファイル群
```

コンテンツ種類が「両方」の場合：
```
<output_dir>/
├── videos/
│   └── ダウンロードされた動画ファイル群
└── audio/
    └── ダウンロードされた音声ファイル群
```

## ライセンス

MIT License

## 注意事項

このツールは教育目的で提供されています。著作権で保護されたコンテンツをダウンロードする際は、各国の法律および利用規約を遵守してください。

## プログラム内部の拡張性

DataScoopは、拡張性を考慮した設計になっています。`BaseDownloader` クラスを継承することで、新たなプラットフォーム用のダウンローダーを簡単に追加できます。また、`ConfigManager` クラスにより設定の保存と読み込みが自動化されており、ユーザー体験の向上に貢献しています。