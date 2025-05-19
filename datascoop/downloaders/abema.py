"""
プラットフォーム固有のダウンローダー - Abema
"""
import os
import re
import yt_dlp
from .video import VideoDownloader
from ..utils.helpers import verify_output_directory

class AbemaDownloader(VideoDownloader):
    """
    Abema専用のダウンローダークラス
    Abema固有の機能を提供する
    """
    
    def __init__(self, output_dir="downloads/abema", quality="best"):
        """
        コンストラクタ
        
        Args:
            output_dir (str): ダウンロードした動画の保存先ディレクトリ
            quality (str): ダウンロードする動画の品質
        """
        super().__init__(output_dir, quality)
        self.logger.info("Abema専用ダウンローダーを初期化しました")
        
    def download(self, url, filename=None, **kwargs):
        """
        URLから動画をダウンロードする
        Abema特有の処理を行う
        
        Args:
            url (str): ダウンロード対象の動画URL
            filename (str, optional): 保存するファイル名
            **kwargs: 追加のパラメータ
                - format (str): 動画フォーマット
                - subtitles (bool): 字幕もダウンロードするかどうか
                
        Returns:
            str: ダウンロードした動画ファイルのパス
        """
        if not self.validate_url(url):
            return None
        
        self.logger.info(f"Abema動画のダウンロードを開始: {url}")
        
        # 作品タイトルURLかエピソードURLかを判定
        is_series_url = self._is_series_url(url)
        
        if is_series_url:
            return self._handle_series_url(url, filename, **kwargs)
        else:
            # 通常のエピソードURLの場合は親クラスの処理を利用
            return super().download(url, filename, **kwargs)
    
    def _is_series_url(self, url):
        """
        URLが作品タイトルURLかどうかを判定する
        
        Args:
            url (str): 判定するURL
            
        Returns:
            bool: 作品タイトルURLの場合はTrue、エピソードURLの場合はFalse
        """
        # 作品タイトルURLのパターン (例: https://abema.tv/video/title/...)
        title_pattern = r'https?://(?:www\.)?abema\.tv/video/title/'
        # エピソードURLのパターン (例: https://abema.tv/video/episode/...)
        episode_pattern = r'https?://(?:www\.)?abema\.tv/video/episode/'
        
        if re.search(title_pattern, url):
            return True
        elif re.search(episode_pattern, url):
            return False
        else:
            # その他のAbema URLの場合は標準の処理を使用
            return False
    
    def _handle_series_url(self, url, filename=None, **kwargs):
        """
        作品タイトルURLの処理
        シリーズ名のフォルダを作成し、その中に各エピソードをダウンロード
        
        Args:
            url (str): 作品タイトルURL
            filename (str, optional): 保存するファイル名のベース
            **kwargs: 追加のパラメータ
                
        Returns:
            list: ダウンロードした動画ファイルパスのリスト
        """
        self.logger.info(f"Abema作品タイトルURLを処理します: {url}")
        
        # yt-dlpでメタデータを取得
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # シリーズ名を取得
                series_title = info.get('title', 'abema_series')
                sanitized_title = self._sanitize_filename(series_title)
                
                # シリーズ用のサブディレクトリを作成
                series_dir = os.path.join(self.output_dir, sanitized_title)
                verify_output_directory(series_dir)
                
                self.logger.info(f"作品タイトル「{series_title}」用のディレクトリを作成しました: {series_dir}")
                
                # 各エピソードのダウンロード
                downloaded_files = []
                
                # yt-dlpでのダウンロードオプション設定
                format_spec = kwargs.get('format', f'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/{self.quality}')
                download_subtitles = kwargs.get('subtitles', False)
                
                output_template = os.path.join(series_dir, '%(title)s.%(ext)s')
                if filename:
                    output_template = os.path.join(series_dir, f"{filename}_%(episode_number)s.%(ext)s")
                    
                ydl_opts = {
                    'format': format_spec,
                    'outtmpl': output_template,
                    'progress_hooks': [self._progress_hook],
                }
                
                if download_subtitles:
                    ydl_opts.update({
                        'writesubtitles': True,
                        'writeautomaticsub': True,
                        'subtitleslangs': ['en', 'ja'],
                        'subtitlesformat': 'srt',
                    })
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    result = ydl.download([url])
                    
                    # yt-dlpの仕様上、複数エピソードが自動的にダウンロードされる
                    self.logger.info(f"作品タイトル「{series_title}」のダウンロードが完了しました")
                    
                    # 実際にダウンロードされたファイルのパスはログから確認する必要がある
                    return [series_dir]  # ダウンロード先ディレクトリを返す
                    
        except Exception as e:
            self.logger.error(f"Abema作品タイトルのダウンロード中にエラーが発生しました: {e}")
            return None
    
    def _sanitize_filename(self, filename):
        """ファイル名に使用できない文字を削除する"""
        # ファイルシステムで無効な文字を削除または置換
        s = re.sub(r'[\\/*?:"<>|]', "", filename)
        s = re.sub(r'\s+', '_', s)  # スペースをアンダースコアに置換
        return s
