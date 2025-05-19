"""
設定の管理モジュール
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """設定の保存・読み込みを管理するクラス"""
    
    DEFAULT_CONFIG = {
        "content_type": "video",  # video, audio, both
        "output_dir": "downloads",
        "video_quality": "best",   # best, high, medium, low, lowest
        "video_format": "mp4",     # mp4, webm, mkv
        "audio_quality": "high",   # high, medium, low
        "audio_format": "mp3",     # mp3, m4a, wav, flac
        "subtitles": False,
        "verbose": False,
        "use_original_title": True, # コンテンツ元のタイトルをそのまま使用するか
        "file_organization": "none", # none, platform, format, both
        "use_platform_subdirs": False, # プラットフォームごとのサブディレクトリを使用するか
        "use_format_subdirs": False, # ファイル形式ごとのサブディレクトリを使用するか
        "platform_dirs": {         # プラットフォームごとのディレクトリ設定
            "youtube": {
                "video": "downloads/youtube/videos", 
                "audio": "downloads/youtube/audio"
            },
            "niconico": {
                "video": "downloads/niconico/videos", 
                "audio": "downloads/niconico/audio"
            },
            "abema": {
                "video": "downloads/abema/videos", 
                "audio": "downloads/abema/audio"
            },
            "unknown": {
                "video": "downloads/others/videos", 
                "audio": "downloads/others/audio"
            }
        }
    }
    
    # 品質オプションの対応表
    QUALITY_MAP = {
        "video": {
            "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "high": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]",
            "medium": "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]",
            "low": "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]",
            "lowest": "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best[height<=360]"
        },
        "audio": {
            "high": "192K",
            "medium": "128K",
            "low": "96K"
        }
    }
    
    def __init__(self):
        """初期化"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, "config.json")
        
    def _get_config_dir(self):
        """設定ディレクトリを取得（なければ作成）"""
        # ホームディレクトリ配下の .datascoop ディレクトリ
        config_dir = os.path.join(str(Path.home()), ".datascoop")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
        
    def load_config(self):
        """設定ファイルからロード"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # デフォルト設定をロードしたもので上書き
                    self.config.update(loaded_config)
                logger.debug(f"設定を読み込みました: {self.config_file}")
                return True
            else:
                logger.debug("設定ファイルが見つかりません。デフォルト設定を使用します。")
                return False
        except Exception as e:
            logger.error(f"設定ファイルの読み込み中にエラーが発生しました: {e}")
            logger.debug("デフォルト設定を使用します。")
            return False
            
    def save_config(self):
        """設定ファイルへ保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            logger.debug(f"設定を保存しました: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"設定ファイルの保存中にエラーが発生しました: {e}")
            return False
            
    def get(self, key, default=None):
        """設定値を取得"""
        return self.config.get(key, default)
        
    def set(self, key, value):
        """設定値を設定"""
        self.config[key] = value
        
    def get_format_spec(self, content_type="video"):
        """フォーマット指定を取得"""
        if content_type == "video":
            quality = self.config.get("video_quality", "best")
            return self.QUALITY_MAP["video"].get(quality, "best")
        elif content_type == "audio":
            quality = self.config.get("audio_quality", "high")
            return self.QUALITY_MAP["audio"].get(quality, "192K")
        return "best"
        
    def print_current_config(self):
        """現在の設定を表示"""
        print("\n設定:")
        print(f"- コンテンツ種類: {self._format_content_type()}")
        print(f"- 出力ディレクトリ: {self.config['output_dir']}")
        
        if self.config['content_type'] in ['video', 'both']:
            print(f"- 動画品質: {self._format_video_quality()}")
            print(f"- 動画フォーマット: {self.config['video_format'].upper()}")
            
        if self.config['content_type'] in ['audio', 'both']:
            print(f"- 音声品質: {self._format_audio_quality()}")
            print(f"- 音声フォーマット: {self.config['audio_format'].upper()}")
            
        print(f"- 字幕ダウンロード: {'はい' if self.config['subtitles'] else 'いいえ'}")
        print(f"- オリジナルタイトル使用: {'はい' if self.config.get('use_original_title', True) else 'いいえ'}")
        
        # ファイル整理方法の表示
        file_organization = self.config.get('file_organization', 'none')
        organization_names = {
            'none': '整理しない（すべて同じフォルダに保存）',
            'platform': 'プラットフォームごとに分ける',
            'format': 'ファイル形式ごとに分ける',
            'both': 'プラットフォームとファイル形式の両方で分ける'
        }
        print(f"- ファイル整理方法: {organization_names.get(file_organization, file_organization)}")
        
    def _format_content_type(self):
        """コンテンツタイプを日本語で整形"""
        types = {
            "video": "動画", 
            "audio": "音声", 
            "both": "動画と音声"
        }
        return types.get(self.config['content_type'], self.config['content_type'])
        
    def _format_video_quality(self):
        """動画品質を日本語で整形"""
        quality = {
            "best": "最高品質",
            "high": "高品質 (1080p)",
            "medium": "中品質 (720p)",
            "low": "低品質 (480p)",
            "lowest": "最低品質 (360p)"
        }
        return quality.get(self.config['video_quality'], self.config['video_quality'])
        
    def _format_audio_quality(self):
        """音声品質を日本語で整形"""
        quality = {
            "high": "高品質 (192kbps)",
            "medium": "中品質 (128kbps)",
            "low": "低品質 (96kbps)"
        }
        return quality.get(self.config['audio_quality'], self.config['audio_quality'])
