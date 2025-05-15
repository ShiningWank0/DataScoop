"""
DataScoop パッケージ
yt-dlpを利用した動画・音声ダウンロードライブラリ
"""

import logging
import importlib.metadata

try:
    # pyproject.tomlからバージョン情報を取得
    __version__ = importlib.metadata.version("datascoop")
except importlib.metadata.PackageNotFoundError:
    # インストールされていない場合は不明とする
    __version__ = "unknown"

__author__ = 'ShiningWank0'

from .downloaders.video import VideoDownloader
from .downloaders.audio import AudioDownloader
from .downloaders.youtube import YouTubeDownloader
from .utils.helpers import setup_logger
from .utils.config import ConfigManager

# バージョン情報をエクスポート
__all__ = [
    'VideoDownloader',
    'AudioDownloader', 
    'YouTubeDownloader',
    'ConfigManager',
    '__version__',
]
from .interactive import InteractiveDownloader

# パッケージ全体のロガーをセットアップ
logger = setup_logger()