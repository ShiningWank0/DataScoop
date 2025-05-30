"""
ダウンローダー用のユーティリティ関数
"""
import os
import re
import logging
from urllib.parse import urlparse, parse_qs

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
    # YouTubeショートを先に判定
    shorts_regex = r'(https?://)?(www\.)?youtube\.com/shorts/([^&=%\?]{11})'
    shorts_match = re.search(shorts_regex, url) # re.search を使用
    if shorts_match:
        return shorts_match.group(3) # VIDEO_ID は3番目のキャプチャグループ
    
    # 通常のYouTube動画
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    
    youtube_match = re.match(youtube_regex, url)
    if youtube_match:
        return youtube_match.group(6)
    
    # URLからshortsパターンを検出できない場合のフォールバック
    if '/shorts/' in url:
        parts = url.split('/shorts/')
        if len(parts) > 1:
            # パラメータがある場合は除去
            video_id = parts[1].split('?')[0].split('&')[0]
            if len(video_id) == 11:  # YouTubeのIDは11文字
                return video_id
    
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

def get_platform_specific_output_dir(url, base_output_dir, content_type=None, config_manager=None):
    """
    URLのプラットフォームに基づいた出力ディレクトリを取得する
    
    Args:
        url (str): 動画URL
        base_output_dir (str): 基本出力ディレクトリ
        content_type (str, optional): コンテンツタイプ ('video'/'audio')
        config_manager (ConfigManager, optional): 設定管理オブジェクト
        
    Returns:
        str: プラットフォーム特化の出力ディレクトリ
    """
    platform = get_platform_from_url(url)
    
    # 設定マネージャーが提供され、プラットフォーム別ディレクトリの設定がある場合
    if config_manager and content_type:
        platform_dirs = config_manager.get("platform_dirs", {})
        if platform_dirs and platform in platform_dirs and content_type in platform_dirs[platform]:
            output_dir = platform_dirs[platform][content_type]
            verify_output_directory(output_dir)
            return output_dir
    
    # 従来の挙動（フォールバック）
    output_dir = os.path.join(base_output_dir, platform)
    verify_output_directory(output_dir)
    return output_dir


