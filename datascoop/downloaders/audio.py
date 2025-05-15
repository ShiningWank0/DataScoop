"""
yt-dlpを利用した音声ダウンローダー
"""
import os
import yt_dlp
from .base import BaseDownloader

class AudioDownloader(BaseDownloader):
    """
    音声ダウンローダークラス
    BaseDownloaderを継承し、yt-dlpを使用して音声をダウンロードする
    """
    
    def __init__(self, output_dir="downloads/audio", quality="best", audio_format="mp3"):
        """
        コンストラクタ
        
        Args:
            output_dir (str): ダウンロードした音声の保存先ディレクトリ
            quality (str): ダウンロードする音声の品質
            audio_format (str): 音声ファイルのフォーマット
        """
        super().__init__(output_dir)
        self.quality = quality
        self.audio_format = audio_format
        self.logger.info(f"音声ダウンローダーを初期化: 品質={self.quality}, フォーマット={self.audio_format}")
        
    def download(self, url, filename=None, **kwargs):
        """
        URLから音声をダウンロードする
        
        Args:
            url (str): ダウンロード対象の音声URL
            filename (str, optional): 保存するファイル名
            **kwargs: 追加のパラメータ
                - bitrate (str): 音声のビットレート (例: '128K')
                
        Returns:
            str: ダウンロードした音声ファイルのパス
        """
        if not self.validate_url(url):
            return None
            
        self.logger.info(f"音声のダウンロードを開始: {url}")
        
        # yt-dlpのオプションを設定
        bitrate = kwargs.get('bitrate', '192K')
        output_template = os.path.join(self.output_dir, '%(title)s.%(ext)s')
        if filename:
            output_template = os.path.join(self.output_dir, f"{filename}.{self.audio_format}")
            
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_format,
                'preferredquality': bitrate,
            }],
            'progress_hooks': [self._progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # 出力ファイル名の拡張子を変更（yt-dlpがファイル変換後の拡張子を更新するため）
                downloaded_file = ydl.prepare_filename(info)
                downloaded_file = os.path.splitext(downloaded_file)[0] + f".{self.audio_format}"
                self.logger.info(f"音声のダウンロードが完了しました: {downloaded_file}")
                return downloaded_file
        except Exception as e:
            self.logger.error(f"音声のダウンロード中にエラーが発生しました: {e}")
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
            self.logger.info("音声変換処理を開始...")
            
    def extract_audio(self, video_path, output_format="mp3", bitrate="192K"):
        """
        動画ファイルから音声を抽出する
        
        Args:
            video_path (str): 音声を抽出する動画ファイルのパス
            output_format (str): 出力音声のフォーマット
            bitrate (str): 音声のビットレート
            
        Returns:
            str: 抽出した音声ファイルのパス
        """
        if not os.path.exists(video_path):
            self.logger.error(f"指定されたファイルが見つかりません: {video_path}")
            return None
            
        self.logger.info(f"音声抽出開始: {video_path}")
        
        filename = os.path.splitext(os.path.basename(video_path))[0]
        output_path = os.path.join(self.output_dir, f"{filename}.{output_format}")
        
        ydl_opts = {
            'outtmpl': os.path.join(self.output_dir, filename),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format,
                'preferredquality': bitrate,
            }],
            'progress_hooks': [self._progress_hook],
        }
        
        try:
            # yt-dlpのFFmpegPostProcessorを使って変換
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # ここではダウンロードではなく、既存ファイルに後処理を適用
                ydl.download([f"file://{video_path}"])
                
            self.logger.info(f"音声抽出が完了しました: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"音声抽出中にエラーが発生しました: {e}")
            return None
