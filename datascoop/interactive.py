"""
対話型インターフェースモジュール
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import filedialog
from .utils.config import ConfigManager
from .downloaders import VideoDownloader, AudioDownloader, YouTubeDownloader, AbemaDownloader
from .utils.helpers import setup_logger, get_platform_from_url, get_platform_specific_output_dir, verify_output_directory

logger = setup_logger()

class InteractiveDownloader:
    """
    対話形式でユーザーとやり取りしながらダウンロードを行うクラス
    """
    
    def __init__(self):
        """初期化"""
        self.config_manager = ConfigManager()
        self.first_run = not self.config_manager.load_config()
        
    def start(self):
        """対話セッションを開始"""
        self._print_welcome()
        
        # 基本設定の取得
        if self.first_run:
            self._setup_initial_config()
        else:
            self.config_manager.print_current_config()
            if self._ask_yes_no("設定を変更しますか？", False):
                self._setup_config()
            else:
                # デフォルト設定を使用する場合でも、一部カスタマイズできるオプションを提供
                self._setup_custom_output_options()
        
        # URLごとの設定を行わない場合のみ、共通のタイトル設定を行う
        if not hasattr(self, 'per_url_config') or not self.per_url_config:
            # ファイル名の設定方法を設定
            self.use_original_title = self._ask_yes_no(
                "ダウンロードするコンテンツのタイトルをそのままファイル名として使用しますか？", 
                True
            )
            self.config_manager.set("use_original_title", self.use_original_title)
        
        # URLの取得
        urls = self._get_download_urls()
        if not urls:
            print("ダウンロードするURLが指定されていません。終了します。")
            return
        
        # URL毎の設定
        self.per_url_settings = {}
        if hasattr(self, 'per_url_config') and self.per_url_config:
            # URLごとに個別設定（出力ディレクトリ、ファイル名）
            self._configure_per_url_settings(urls)
        elif not self.use_original_title:
            # 従来の個別ファイル名設定のみ
            if self._ask_yes_no("ダウンロードするURLごとに個別のファイル名を設定しますか？", True):
                self._configure_per_url_settings(urls)
                
        self._download_contents(urls)
        self._print_goodbye()
        
    def _print_welcome(self):
        """ウェルカムメッセージ"""
        print("\nDataScoopへようこそ！")
        if self.first_run:
            print("初回実行のため、設定を行います。")
        else:
            print("前回の設定を読み込みました。")
            
    def _print_goodbye(self):
        """終了メッセージ"""
        print("\nDataScoopを終了します。")
        
    def _setup_initial_config(self):
        """初期設定"""
        self._setup_config()
        if self._ask_yes_no("これらの設定をデフォルトとして保存しますか？", True):
            if self.config_manager.save_config():
                print("設定を保存しました。")
            else:
                print("設定の保存に失敗しました。")
                
    def _setup_config(self):
        """詳細設定"""
        print("\n--- 設定 ---")
        
        # コンテンツタイプ
        content_type = self._ask_choice(
            "ダウンロードするコンテンツの種類を選択してください:",
            ["動画", "音声", "両方"],
            ["video", "audio", "both"],
            self.config_manager.get("content_type", "video")
        )
        self.config_manager.set("content_type", content_type)
        
        # 出力ディレクトリ
        output_dir = self._ask_input(
            "出力ディレクトリを入力してください",
            self.config_manager.get("output_dir", "downloads")
        )
        self.config_manager.set("output_dir", output_dir)
        
        # 動画の設定
        if content_type in ["video", "both"]:
            # 動画品質
            video_quality = self._ask_choice(
                "動画の品質を選択してください:",
                ["最高品質", "高品質 (1080p)", "中品質 (720p)", "低品質 (480p)", "最低品質 (360p)"],
                ["best", "high", "medium", "low", "lowest"],
                self.config_manager.get("video_quality", "best")
            )
            self.config_manager.set("video_quality", video_quality)
            
            # 動画フォーマット
            video_format = self._ask_choice(
                "動画フォーマットを選択してください:",
                ["MP4", "WebM", "MKV"],
                ["mp4", "webm", "mkv"],
                self.config_manager.get("video_format", "mp4")
            )
            self.config_manager.set("video_format", video_format)
        
        # 音声の設定
        if content_type in ["audio", "both"]:
            # 音声品質
            audio_quality = self._ask_choice(
                "音声の品質を選択してください:",
                ["高品質 (192kbps)", "中品質 (128kbps)", "低品質 (96kbps)"],
                ["high", "medium", "low"],
                self.config_manager.get("audio_quality", "high")
            )
            self.config_manager.set("audio_quality", audio_quality)
            
            # 音声フォーマット
            audio_format = self._ask_choice(
                "音声フォーマットを選択してください:",
                ["MP3", "M4A", "WAV", "FLAC"],
                ["mp3", "m4a", "wav", "flac"],
                self.config_manager.get("audio_format", "mp3")
            )
            self.config_manager.set("audio_format", audio_format)
            
        # 字幕
        subtitles = self._ask_yes_no(
            "字幕をダウンロードしますか？",
            self.config_manager.get("subtitles", False)
        )
        self.config_manager.set("subtitles", subtitles)
        
        # 詳細ログ
        verbose = self._ask_yes_no(
            "詳細なログを出力しますか？",
            self.config_manager.get("verbose", False)
        )
        self.config_manager.set("verbose", verbose)
        if verbose:
            logger.setLevel(logging.DEBUG)
        
        # ファイル整理方法の設定
        file_organization = self._ask_choice(
            "ダウンロードしたファイルの整理方法を選択してください:",
            [
                "整理しない（すべて同じフォルダに保存）", 
                "プラットフォームごとに分ける", 
                "ファイル形式ごとに分ける", 
                "プラットフォームとファイル形式の両方で分ける"
            ],
            ["none", "platform", "format", "both"],
            self.config_manager.get("file_organization", "none")
        )
        self.config_manager.set("file_organization", file_organization)
        
        # プラットフォームごとのサブディレクトリが必要な場合
        use_platform_subdirs = file_organization in ["platform", "both"]
        self.config_manager.set("use_platform_subdirs", use_platform_subdirs)
        
        # ファイル形式ごとのサブディレクトリが必要な場合
        use_format_subdirs = file_organization in ["format", "both"]
        self.config_manager.set("use_format_subdirs", use_format_subdirs)
        
        # プラットフォーム別の詳細設定
        if use_platform_subdirs:
            customize_platform_dirs = self._ask_yes_no(
                "各プラットフォームごとの保存先を個別にカスタマイズしますか？",
                False
            )
            
            if customize_platform_dirs:
                self._setup_platform_dirs(content_type)
            
        print("\n設定が完了しました。")
        
    def _setup_custom_output_options(self):
        """一部の出力設定のみカスタマイズする"""
        print("\n--- 出力オプション ---")
        customize = self._ask_yes_no("出力ディレクトリまたはファイル形式をカスタマイズしますか？", False)
        
        if not customize:
            return
            
        customize_options = self._ask_choice(
            "何をカスタマイズしますか？",
            ["出力ディレクトリのみ", "ファイル形式のみ", "両方"],
            ["dir", "format", "both"],
            "both"
        )
        
        # URLごとに個別設定を行うかどうかのフラグ
        self.per_url_config = False
        if customize_options in ["dir", "both"]:
            self.per_url_config = self._ask_yes_no("設定はダウンロードするURLごとに個別に行いますか？", True)
            
            # 共通設定の場合
            if not self.per_url_config:
                # 出力ディレクトリのカスタマイズ
                use_gui = self._ask_yes_no("GUIでディレクトリを選択しますか？", False)
                
                if use_gui:
                    dir_path = self._select_directory_gui()
                    if dir_path:
                        self.config_manager.set("output_dir", dir_path)
                        print(f"出力ディレクトリを設定しました: {dir_path}")
                else:
                    output_dir = self._ask_input(
                        "出力ディレクトリを入力してください",
                        self.config_manager.get("output_dir", "downloads")
                    )
                    self.config_manager.set("output_dir", output_dir)
        
        content_type = self.config_manager.get("content_type", "video")
        
        if customize_options in ["format", "both"] and not self.per_url_config:
            # ファイル形式のカスタマイズ（共通設定の場合）
            if content_type in ["video", "both"]:
                video_format = self._ask_choice(
                    "動画フォーマットを選択してください:",
                    ["MP4", "WebM", "MKV"],
                    ["mp4", "webm", "mkv"],
                    self.config_manager.get("video_format", "mp4")
                )
                self.config_manager.set("video_format", video_format)
                
            if content_type in ["audio", "both"]:
                audio_format = self._ask_choice(
                    "音声フォーマットを選択してください:",
                    ["MP3", "M4A", "WAV", "FLAC"],
                    ["mp3", "m4a", "wav", "flac"],
                    self.config_manager.get("audio_format", "mp3")
                )
                self.config_manager.set("audio_format", audio_format)
                
    def _select_directory_gui(self):
        """GUIでディレクトリを選択する"""
        try:
            # GUIウィンドウを非表示にする
            root = tk.Tk()
            root.withdraw()
            
            # ダイアログでディレクトリを選択
            dir_path = filedialog.askdirectory(
                title="出力ディレクトリを選択",
                initialdir=self.config_manager.get("output_dir", os.path.expanduser("~"))
            )
            
            # 選択後にGUIを閉じる
            root.destroy()
            
            return dir_path if dir_path else None
        except Exception as e:
            print(f"GUIディレクトリ選択中にエラーが発生しました: {e}")
            print("CUIでの入力に切り替えます。")
            return None
            
    def _configure_per_url_settings(self, urls):
        """URLごとの設定を行う"""
        print("\n--- URLごとの設定 ---")
        print("各URLに対してファイル名を指定します。空のままにするとコンテンツタイトルが使用されます。")
        
        # URLごとにカスタム設定
        for url in urls:
            settings = {}
            # URLごとの出力ディレクトリ設定（per_url_configがTrueの場合）
            if hasattr(self, 'per_url_config') and self.per_url_config:
                use_gui = self._ask_yes_no("GUIでディレクトリを選択しますか？", True)
                if use_gui:
                    dir_path = self._select_directory_gui()
                    if dir_path:
                        settings["output_dir"] = dir_path
                        print(f"出力ディレクトリを設定しました: {dir_path}")
                else:
                    output_dir = self._ask_input("出力ディレクトリを入力してください", 
                                               self.config_manager.get("output_dir", "downloads"))
                    settings["output_dir"] = output_dir
                    
                use_original_title = self._ask_yes_no(
                    "ダウンロードするコンテンツのタイトルをそのままファイル名として使用しますか？", 
                    True
                )
                
                if not use_original_title:
                    custom_filename = self._ask_input("ファイル名を指定してください", "")
                    if custom_filename:
                        settings["filename"] = custom_filename
            else:
                # 従来のファイル名のみのカスタム設定
                custom_filename = self._ask_input(f"URL: {url} のファイル名", "")
                if custom_filename:
                    settings["filename"] = custom_filename
                    
            if settings:
                self.per_url_settings[url] = settings
                
    def _ask_input(self, prompt, default=None):
        """入力を受け付ける"""
        default_display = f" [{default}]" if default else ""
        while True:
            try:
                value = input(f"{prompt}{default_display}: ").strip()
                if not value and default is not None:
                    return default
                if value:
                    return value
                print("値を入力してください。")
            except KeyboardInterrupt:
                print("\n中断されました。")
                sys.exit(1)
                
    def _ask_yes_no(self, prompt, default=True):
        """はい/いいえの質問をする"""
        default_value = "y" if default else "n"
        default_display = "[y/n]" if default is None else ("[Y/n]" if default else "[y/N]")
        
        while True:
            try:
                value = input(f"{prompt} {default_display}: ").strip().lower()
                if not value and default is not None:
                    return default
                if value in ["y", "yes", "はい"]:
                    return True
                if value in ["n", "no", "いいえ"]:
                    return False
                print("'y'または'n'で回答してください。")
            except KeyboardInterrupt:
                print("\n中断されました。")
                sys.exit(1)
                
    def _ask_choice(self, prompt, choices, values, default=None):
        """選択肢から選ばせる"""
        default_index = None
        if default in values:
            default_index = values.index(default) + 1
        
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"{i}. {choice}")
            
        default_display = f" [{default_index}]" if default_index else ""
        
        while True:
            try:
                value = input(f"番号を入力してください{default_display}: ").strip()
                if not value and default_index:
                    return values[default_index - 1]
                    
                try:
                    index = int(value) - 1
                    if 0 <= index < len(values):
                        return values[index]
                    print(f"1～{len(choices)}の番号を入力してください。")
                except ValueError:
                    print("有効な番号を入力してください。")
            except KeyboardInterrupt:
                print("\n中断されました。")
                sys.exit(1)
                
    def _get_download_urls(self):
        """ダウンロードするURLを取得"""
        print("\nダウンロードURLを入力してください (終了するには 'exit' または 'q' を入力):")
        print("複数のURLを入力する場合は、1行に1つずつ入力してください。")
        print("入力が終わったら空行を入力してください。")
        print()
        
        urls = []
        while True:
            try:
                url = input("URL: ").strip()
                if not url:
                    break  # 空行で終了
                if url.lower() in ["exit", "q", "quit"]:
                    break  # 明示的に終了
                    
                if url.startswith(('http://', 'https://', 'www.')):
                    urls.append(url)
                else:
                    print("有効なURLを入力してください。")
            except KeyboardInterrupt:
                print("\n中断されました。")
                return []
                
        if urls:
            print(f"\n{len(urls)}個のURLを受け付けました。ダウンロードを開始します...")
        return urls
        
    def _download_contents(self, urls):
        """コンテンツをダウンロード"""
        content_type = self.config_manager.get("content_type", "video")
        default_output_dir = self.config_manager.get("output_dir", "downloads")
        use_original_title = self.config_manager.get("use_original_title", True)
        
        # デフォルト出力ディレクトリが存在しなければ作成
        from .utils.helpers import verify_output_directory, get_platform_from_url, get_platform_specific_output_dir
        verify_output_directory(default_output_dir)
        
        # URLごとにダウンロード
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url} をダウンロード中...")
            platform = get_platform_from_url(url)
            print(f"検出されたプラットフォーム: {platform}")
            
            # URLごとの個別設定を取得
            custom_filename = None
            custom_output_dir = None
            
            if url in self.per_url_settings:
                url_settings = self.per_url_settings[url]
                
                if 'filename' in url_settings:
                    custom_filename = url_settings['filename']
                    
                if 'output_dir' in url_settings:
                    custom_output_dir = url_settings['output_dir']
                    # URLごとの出力ディレクトリが存在しなければ作成
                    verify_output_directory(custom_output_dir)
            
            # このURLで使用する出力ディレクトリ
            output_dir = custom_output_dir or default_output_dir
            
            # ファイル整理方法の設定を取得
            file_organization = self.config_manager.get("file_organization", "none")
            use_platform_subdirs = self.config_manager.get("use_platform_subdirs", False) 
            use_format_subdirs = self.config_manager.get("use_format_subdirs", False)
            platform_dirs = self.config_manager.get("platform_dirs", {})
            
            # URLごとの個別設定がない場合、全体設定に基づいて出力ディレクトリを決定
            if not custom_output_dir:
                # プラットフォーム別設定がある場合はそちらを優先
                if platform in platform_dirs:
                    for_video = content_type in ["video", "both"]
                    for_audio = content_type in ["audio", "both"]
                    
                    # プラットフォームごとの設定がある場合は使用
                    if use_platform_subdirs:
                        if for_video and for_audio:
                            # bothの場合は後でそれぞれ処理
                            pass
                        elif for_video and "video" in platform_dirs[platform]:
                            output_dir = platform_dirs[platform]["video"]
                        elif for_audio and "audio" in platform_dirs[platform]:
                            output_dir = platform_dirs[platform]["audio"]
                    # なければヘルパー関数を使用
                    else:
                        output_dir = get_platform_specific_output_dir(
                            url, 
                            output_dir, 
                            content_type="video" if content_type in ["video", "both"] else "audio",
                            config_manager=self.config_manager
                        )
            
            # コンテンツタイプに応じたダウンローダーを準備
            downloaders = {}
            
            if content_type in ["video", "both"]:
                # output_dirを適切に調整
                video_dir = output_dir
                
                # ファイル整理方法に応じて調整
                if content_type == "both" or use_format_subdirs:
                    video_dir = os.path.join(output_dir, "videos")
                
                # 出力ディレクトリ作成
                verify_output_directory(video_dir)
                
                video_quality = self.config_manager.get("video_quality", "best")
                video_format = self.config_manager.get("video_format", "mp4")
                
                # プラットフォームに応じたダウンローダーを選択
                if platform == 'youtube':
                    downloaders["video"] = YouTubeDownloader(
                        output_dir=video_dir,
                        quality=video_quality
                    )
                elif platform == 'abema':
                    downloaders["video"] = AbemaDownloader(
                        output_dir=video_dir,
                        quality=video_quality
                    )
                else:
                    # その他のプラットフォームは一般的なVideoDownloaderを使用
                    downloaders["video"] = VideoDownloader(
                        output_dir=video_dir,
                        quality=video_quality
                    )
                
            if content_type in ["audio", "both"]:
                # output_dirを適切に調整
                audio_dir = output_dir
                
                # ファイル整理方法に応じて調整
                if content_type == "both" or use_format_subdirs:
                    audio_dir = os.path.join(output_dir, "audio")
                
                # 出力ディレクトリ作成
                verify_output_directory(audio_dir)
                
                audio_quality = self.config_manager.get("audio_quality", "high")
                audio_format = self.config_manager.get("audio_format", "mp3")
                
                downloaders["audio"] = AudioDownloader(
                    output_dir=audio_dir,
                    audio_format=audio_format,
                    quality=audio_quality
                )
            
            try:
                if content_type in ["video", "both"]:
                    # 動画ダウンロード
                    format_spec = self.config_manager.get_format_spec("video")
                    subtitles = self.config_manager.get("subtitles", False)
                    
                    # オリジナルタイトルを使用しない場合、またはURL毎の設定がある場合はファイル名を指定
                    filename = None
                    # URLごとの設定がある場合は、そのURLの設定を優先する
                    url_use_original = use_original_title
                    if url in self.per_url_settings and 'output_dir' in self.per_url_settings[url]:
                        url_use_original = not custom_filename
                        
                    if not url_use_original or custom_filename:
                        filename = custom_filename or f"video_{i}"
                    
                    result = downloaders["video"].download(
                        url,
                        filename=filename,
                        format=format_spec,
                        subtitles=subtitles
                    )
                    
                    if not result:
                        print(f"動画「{url}」のダウンロードに失敗しました。")
                
                if content_type in ["audio", "both"]:
                    # 音声ダウンロード
                    bitrate = self.config_manager.get_format_spec("audio")
                    
                    # オリジナルタイトルを使用しない場合、またはURL毎の設定がある場合はファイル名を指定
                    filename = None
                    url_use_original = use_original_title
                    if url in self.per_url_settings and 'output_dir' in self.per_url_settings[url]:
                        url_use_original = not custom_filename
                        
                    if not url_use_original or custom_filename:
                        filename = custom_filename or f"audio_{i}"
                    
                    result = downloaders["audio"].download(
                        url,
                        filename=filename,
                        bitrate=bitrate
                    )
                    
                    if not result:
                        print(f"音声「{url}」のダウンロードに失敗しました。")
                        
            except Exception as e:
                logger.error(f"ダウンロード中にエラーが発生しました: {e}")
                print(f"{url} のダウンロード中にエラーが発生しました。")
                
        print("\nすべてのダウンロードが完了しました。")
        
    def _setup_platform_dirs(self, content_type):
        """各プラットフォームごとの保存先を設定する"""
        print("\n--- プラットフォーム別設定 ---")
        
        # 整理方法を取得
        file_organization = self.config_manager.get("file_organization", "none")
        use_platform_subdirs = self.config_manager.get("use_platform_subdirs", False)
        use_format_subdirs = self.config_manager.get("use_format_subdirs", False)
        base_dir = self.config_manager.get("output_dir", "downloads")
        
        # 設定から現在のプラットフォームディレクトリ設定を取得
        platform_dirs = self.config_manager.get("platform_dirs", {})
        if not platform_dirs:
            platform_dirs = {
                "youtube": {"video": f"{base_dir}/youtube/videos", "audio": f"{base_dir}/youtube/audio"},
                "niconico": {"video": f"{base_dir}/niconico/videos", "audio": f"{base_dir}/niconico/audio"},
                "abema": {"video": f"{base_dir}/abema/videos", "audio": f"{base_dir}/abema/audio"},
                "unknown": {"video": f"{base_dir}/others/videos", "audio": f"{base_dir}/others/audio"}
            }
        
        platforms = ["youtube", "niconico", "abema", "unknown"]
        platform_names = {
            "youtube": "YouTube",
            "niconico": "ニコニコ動画",
            "abema": "Abema",
            "unknown": "その他のプラットフォーム"
        }
        
        # GUIで設定するかどうか
        use_gui = self._ask_yes_no("GUIでディレクトリを選択しますか？", False)
        
        # 各プラットフォームの保存先を設定
        for platform in platforms:
            print(f"\n{platform_names[platform]}の設定:")
            
            # 動画の出力先
            if content_type in ["video", "both"]:
                # 適切なデフォルト値を構築
                if file_organization == "none":
                    default_video_dir = base_dir
                elif file_organization == "platform":
                    default_video_dir = f"{base_dir}/{platform}"
                elif file_organization == "format":
                    default_video_dir = f"{base_dir}/videos"
                else:  # both
                    default_video_dir = f"{base_dir}/{platform}/videos"
                
                # 現在の設定があればそれを使用
                default_video_dir = platform_dirs.get(platform, {}).get("video", default_video_dir)
                
                if use_gui:
                    print(f"{platform_names[platform]}の動画保存先ディレクトリを選択してください")
                    video_dir = self._select_directory_gui() or default_video_dir
                else:
                    video_dir = self._ask_input(
                        f"{platform_names[platform]}の動画保存先ディレクトリ", 
                        default_video_dir
                    )
                
                # プラットフォーム設定を確保
                if platform not in platform_dirs:
                    platform_dirs[platform] = {}
                    
                platform_dirs[platform]["video"] = video_dir
                print(f"{platform_names[platform]}の動画は {video_dir} に保存されます")
            
            # 音声の出力先
            if content_type in ["audio", "both"]:
                # 適切なデフォルト値を構築
                if file_organization == "none":
                    default_audio_dir = base_dir
                elif file_organization == "platform":
                    default_audio_dir = f"{base_dir}/{platform}"
                elif file_organization == "format":
                    default_audio_dir = f"{base_dir}/audio"
                else:  # both
                    default_audio_dir = f"{base_dir}/{platform}/audio"
                
                # 現在の設定があればそれを使用
                default_audio_dir = platform_dirs.get(platform, {}).get("audio", default_audio_dir)
                
                if use_gui:
                    print(f"{platform_names[platform]}の音声保存先ディレクトリを選択してください")
                    audio_dir = self._select_directory_gui() or default_audio_dir
                else:
                    audio_dir = self._ask_input(
                        f"{platform_names[platform]}の音声保存先ディレクトリ", 
                        default_audio_dir
                    )
                
                # プラットフォーム設定を確保
                if platform not in platform_dirs:
                    platform_dirs[platform] = {}
                    
                platform_dirs[platform]["audio"] = audio_dir
                print(f"{platform_names[platform]}の音声は {audio_dir} に保存されます")
        
        # 設定に保存
        self.config_manager.set("platform_dirs", platform_dirs)
        print("\nプラットフォーム別設定を保存しました。")
