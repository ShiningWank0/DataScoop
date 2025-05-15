"""
ダウンローダー用のユーティリティ関数
"""
import os
import re
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def setup_logger():
    """
    ロガーの設定
    
    Returns:
        logging.Logger: 設定されたロガー
    """
    logger = logging.getLogger('datascoop')
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def sanitize_filename(filename):
    """
    ファイル名から無効な文字を削除する
    
    Args:
        filename (str): 元のファイル名
        
    Returns:
        str: 有効なファイル名
    """
    # ファイルシステムで無効な文字を削除または置換
    s = re.sub(r'[\\/*?:"<>|]', "", filename)
    s = re.sub(r'\s+', '_', s)  # スペースをアンダースコアに置換
    return s

def extract_video_id(url):
    """
    URLから動画IDを抽出する（YouTubeの場合）
    
    Args:
        url (str): 動画URL
        
    Returns:
        str: 動画ID、または抽出できない場合はNone
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    youtube_match = re.match(youtube_regex, url)
    if youtube_match:
        return youtube_match.group(6)
    
    # YouTubeショートの場合
    shorts_regex = r'(https?://)?(www\.)?youtube\.com/shorts/([^&=%\?]{11})'
    shorts_match = re.match(shorts_regex, url)
    if shorts_match:
        return shorts_match.group(3)
    
    return None

def get_platform_from_url(url):
    """
    URLからプラットフォーム名を推測する
    
    Args:
        url (str): 動画URL
        
    Returns:
        str: プラットフォーム名 (例: 'youtube', 'twitter', 'unknown')
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    if 'youtube' in domain or 'youtu.be' in domain:
        return 'youtube'
    elif 'twitter' in domain or 'x.com' in domain:
        return 'twitter'
    elif 'instagram' in domain:
        return 'instagram'
    elif 'facebook' in domain or 'fb.com' in domain:
        return 'facebook'
    elif 'tiktok' in domain:
        return 'tiktok'
    elif 'vimeo' in domain:
        return 'vimeo'
    elif 'dailymotion' in domain:
        return 'dailymotion'
    else:
        return 'unknown'

def check_available_formats(url):
    """
    利用可能なフォーマット一覧を取得する
    
    Args:
        url (str): 動画URL
        
    Returns:
        list: 利用可能なフォーマット情報のリスト
    """
    import yt_dlp
    
    ydl_opts = {
        'listformats': True,
        'quiet': True,
        'skip_download': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'formats' in info:
                return info['formats']
            return []
    except Exception as e:
        logger.error(f"フォーマット一覧の取得中にエラーが発生しました: {e}")
        return []
