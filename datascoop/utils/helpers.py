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
        str: プラットフォーム名 (例: 'youtube', 'niconico', 'unknown')
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    if 'youtube' in domain or 'youtu.be' in domain:
        return 'youtube'
    elif 'nicovideo' in domain or 'nico.ms' in domain:
        return 'niconico'
    elif 'abema' in domain:
        return 'abema'
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

def verify_output_directory(output_dir):
    """
    出力ディレクトリが存在するか確認し、存在しなければ作成する
    
    Args:
        output_dir (str): 出力ディレクトリパス
        
    Returns:
        bool: ディレクトリが存在または作成された場合はTrue
    """
    if not output_dir:
        return False
        
    try:
        os.makedirs(output_dir, exist_ok=True)
        return os.path.isdir(output_dir)
    except Exception as e:
        logger.error(f"出力ディレクトリの作成中にエラーが発生しました: {e}")
        return False

def get_platform_specific_output_dir(url, base_output_dir):
    """
    URLのプラットフォームに基づいた出力ディレクトリを取得する
    
    Args:
        url (str): 動画URL
        base_output_dir (str): 基本出力ディレクトリ
        
    Returns:
        str: プラットフォーム特化の出力ディレクトリ
    """
    platform = get_platform_from_url(url)
    output_dir = os.path.join(base_output_dir, platform)
    verify_output_directory(output_dir)
    return output_dir


