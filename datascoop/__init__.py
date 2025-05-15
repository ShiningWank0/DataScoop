"""
DataScoop パッケージ
yt-dlpを利用した動画・音声ダウンロードライブラリ
"""

import logging
from .downloaders.video import VideoDownloader
from .downloaders.audio import AudioDownloader
from .downloaders.youtube import YouTubeDownloader
from .utils.helpers import setup_logger
from .utils.config import ConfigManager
from .interactive import InteractiveDownloader

# パッケージ全体のロガーをセットアップ
logger = setup_logger()

# バージョン情報
__version__ = '0.1.0'