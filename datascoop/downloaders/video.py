"""
yt-dlpを利用した動画ダウンローダー
"""
import os
import yt_dlp
from .base import BaseDownloader

class VideoDownloader(BaseDownloader):
    """
    動画ダウンローダークラス
    BaseDownloaderを継承し、yt-dlpを使用して動画をダウンロードする
    """
    
    def __init__(self, output_dir="downloads/videos", quality="best"):
        """
        コンストラクタ
        
        Args:
            output_dir (str): ダウンロードした動画の保存先ディレクトリ
            quality (str): ダウンロードする動画の品質
        """
        super().__init__(output_dir)
        self.quality = quality
        self.logger.info(f"動画ダウンローダーを初期化: 品質={self.quality}")
        
    def download(self, url, filename=None, **kwargs):
        """
        URLから動画をダウンロードする
        
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
        
        self.logger.info(f"動画のダウンロードを開始: {url}")
        
        # yt-dlpのオプションを設定
        format_spec = kwargs.get('format', f'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/{self.quality}')
        download_subtitles = kwargs.get('subtitles', False)
        
        output_template = os.path.join(self.output_dir, '%(title)s.%(ext)s')
        if filename:
            output_template = os.path.join(self.output_dir, f"{filename}.%(ext)s")
            
        ydl_opts = {
            'format': format_spec,
            'outtmpl': output_template,
            'noplaylist': True,
            'progress_hooks': [self._progress_hook],
        }
        
        if download_subtitles:
            ydl_opts.update({
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'ja'],
                'subtitlesformat': 'srt',
            })
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                self.logger.info(f"動画のダウンロードが完了しました: {downloaded_file}")
                return downloaded_file
        except Exception as e:
            self.logger.error(f"動画のダウンロード中にエラーが発生しました: {e}")
            return None
            
    def _progress_hook(self, d):
        """
        ダウンロード進捗を表示するフック関数
        
        Args:
            d (dict): 進捗情報
        """
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            self.logger.info(f"ダウンロード進捗: {percent} 速度: {speed} 残り時間: {eta}")
        elif d['status'] == 'finished':
            self.logger.info(f"ダウンロード完了: {d['filename']}")
            self.logger.info("後処理を開始...")
            
    def get_video_info(self, url):
        """
        動画の情報を取得する
        
        Args:
            url (str): 情報を取得する動画のURL
            
        Returns:
            dict: 動画情報
        """
        if not self.validate_url(url):
            return None
            
        self.logger.info(f"動画情報の取得: {url}")
        
        ydl_opts = {
            'noplaylist': True,
            'skip_download': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            self.logger.error(f"動画情報の取得中にエラーが発生しました: {e}")
            return None
