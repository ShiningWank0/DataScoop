"""
プラットフォーム固有のダウンローダー - YouTube
"""
import os
from .video import VideoDownloader

class YouTubeDownloader(VideoDownloader):
    """
    YouTube専用のダウンローダークラス
    特定のYouTube固有の機能を提供する
    """
    
    def __init__(self, output_dir="downloads/youtube", quality="best"):
        """
        コンストラクタ
        
        Args:
            output_dir (str): ダウンロードした動画の保存先ディレクトリ
            quality (str): ダウンロードする動画の品質
        """
        super().__init__(output_dir, quality)
        self.logger.info("YouTube専用ダウンローダーを初期化しました")
        
    def download_playlist(self, playlist_url, max_videos=None, start_at=1, **kwargs):
        """
        YouTubeプレイリストをダウンロードする
        
        Args:
            playlist_url (str): プレイリストのURL
            max_videos (int, optional): ダウンロードする最大動画数
            start_at (int): プレイリスト内の何番目の動画からダウンロードを開始するか
            **kwargs: その他のダウンロードオプション
            
        Returns:
            list: ダウンロードした動画ファイルパスのリスト
        """
        if not self.validate_url(playlist_url):
            return []
            
        self.logger.info(f"YouTubeプレイリストのダウンロードを開始: {playlist_url}")
        
        # プレイリスト用のオプションを設定
        playlist_opts = {
            'extract_flat': 'in_playlist',
            'playliststart': start_at,
            'noplaylist': False,  # プレイリストを処理する
        }
        
        if max_videos:
            playlist_opts['playlistend'] = start_at + max_videos - 1
            
        # 基本オプションとマージ
        format_spec = kwargs.get('format', f'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/{self.quality}')
        subtitles = kwargs.get('subtitles', False)
        
        output_template = os.path.join(
            self.output_dir, 
            '%(playlist_title)s', 
            '%(playlist_index)s-%(title)s.%(ext)s'
        )
            
        import yt_dlp
        
        ydl_opts = {
            'format': format_spec,
            'outtmpl': output_template,
            'progress_hooks': [self._progress_hook],
            **playlist_opts
        }
        
        if subtitles:
            ydl_opts.update({
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en', 'ja'],
                'subtitlesformat': 'srt',
            })
        
        downloaded_files = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=True)
                
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            video_file = ydl.prepare_filename(entry)
                            downloaded_files.append(video_file)
                            self.logger.info(f"プレイリスト内の動画をダウンロードしました: {video_file}")
                
                self.logger.info(f"プレイリストのダウンロードが完了しました。{len(downloaded_files)}個の動画をダウンロードしました。")
                return downloaded_files
        except Exception as e:
            self.logger.error(f"プレイリストのダウンロード中にエラーが発生しました: {e}")
            return downloaded_files
            
    def download_channel(self, channel_url, max_videos=None, **kwargs):
        """
        YouTubeチャンネルの動画をダウンロードする
        
        Args:
            channel_url (str): チャンネルのURL
            max_videos (int, optional): ダウンロードする最大動画数
            **kwargs: その他のダウンロードオプション
            
        Returns:
            list: ダウンロードした動画ファイルパスのリスト
        """
        # チャンネルのダウンロードはプレイリストのダウンロードと同様に処理できる
        return self.download_playlist(channel_url, max_videos, **kwargs)
        
    def download_with_chapters(self, url, filename=None, **kwargs):
        """
        チャプター情報付きで動画をダウンロードする
        
        Args:
            url (str): 動画URL
            filename (str, optional): 保存するファイル名
            **kwargs: その他のダウンロードオプション
            
        Returns:
            str: ダウンロードした動画ファイルのパス
        """
        if not self.validate_url(url):
            return None
            
        self.logger.info(f"チャプター情報付きで動画のダウンロードを開始: {url}")
        
        # 基本的なダウンロードオプション
        format_spec = kwargs.get('format', f'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/{self.quality}')
        
        output_template = os.path.join(self.output_dir, '%(title)s.%(ext)s')
        if filename:
            output_template = os.path.join(self.output_dir, f"{filename}.%(ext)s")
            
        import yt_dlp
        
        ydl_opts = {
            'format': format_spec,
            'outtmpl': output_template,
            'noplaylist': True,
            'progress_hooks': [self._progress_hook],
            'writeinfojson': True,  # メタデータをJSONとして保存
            'writeannotations': True,  # アノテーション（チャプター情報など）を保存
            'writethumbnail': True,  # サムネイルを保存
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                downloaded_file = ydl.prepare_filename(info)
                
                # チャプター情報を表示
                if 'chapters' in info and info['chapters']:
                    self.logger.info(f"チャプター情報を検出: {len(info['chapters'])}個のチャプター")
                    for i, chapter in enumerate(info['chapters'], 1):
                        start_time = chapter.get('start_time', 0)
                        title = chapter.get('title', f'チャプター {i}')
                        self.logger.info(f"  {i}. {title} - {self._format_time(start_time)}")
                else:
                    self.logger.info("チャプター情報は見つかりませんでした")
                
                self.logger.info(f"動画のダウンロードが完了しました: {downloaded_file}")
                return downloaded_file
        except Exception as e:
            self.logger.error(f"動画のダウンロード中にエラーが発生しました: {e}")
            return None
    
    def _format_time(self, seconds):
        """秒数を時:分:秒形式にフォーマットする"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
