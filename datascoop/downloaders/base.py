"""
ダウンローダーの基底クラスを定義するモジュール
"""
import os
import logging
from abc import ABC, abstractmethod

class BaseDownloader(ABC):
    """
    ダウンローダーの基底クラス
    全てのダウンローダーはこのクラスを継承する
    """
    
    def __init__(self, output_dir="downloads"):
        """
        コンストラクタ
        
        Args:
            output_dir (str): ダウンロードしたファイルの保存先ディレクトリ
        """
        self.output_dir = output_dir
        self._setup_output_dir()
        self._setup_logger()
        
    def _setup_output_dir(self):
        """出力ディレクトリを作成する"""
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger.info(f"出力ディレクトリを設定: {self.output_dir}")
        
    def _setup_logger(self):
        """ロガーの設定"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    @abstractmethod
    def download(self, url, **kwargs):
        """
        URLからコンテンツをダウンロードする抽象メソッド
        
        Args:
            url (str): ダウンロード対象のURL
            **kwargs: 追加のパラメータ
            
        Returns:
            str: ダウンロードしたファイルのパス
        """
        pass
    
    def validate_url(self, url):
        """
        URLが有効かどうか検証する
        
        Args:
            url (str): 検証するURL
            
        Returns:
            bool: URLが有効な場合はTrue、そうでない場合はFalse
        """
        if not url:
            self.logger.error("URLが空です")
            return False
        
        if not url.startswith(("http://", "https://", "www.")):
            self.logger.error(f"無効なURL形式です: {url}")
            return False
            
        return True
