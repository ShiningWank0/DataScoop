#!/usr/bin/env python
"""
DataScoopの使用例を示すサンプルスクリプト
"""

import os
import sys
from datascoop import VideoDownloader, AudioDownloader
from datascoop.downloaders import YouTubeDownloader
from datascoop.utils.helpers import setup_logger

logger = setup_logger()

def example_video_download():
    """基本的な動画ダウンロードの例"""
    logger.info("=== 基本的な動画ダウンロードの例 ===")
    
    # 動画ダウンローダーを初期化
    downloader = VideoDownloader(output_dir="examples/videos")
    
    # サンプル動画をダウンロード（Creative CommonsビデオなどのURLを指定してください）
    sample_url = "https://www.youtube.com/watch?v=C0DPdy98e4c"  # サンプル動画のURL
    
    result = downloader.download(sample_url)
    if result:
        logger.info(f"動画をダウンロードしました: {result}")
    else:
        logger.error("動画のダウンロードに失敗しました")
    
    logger.info("=" * 50)

def example_audio_download():
    """音声ダウンロードの例"""
    logger.info("=== 音声ダウンロードの例 ===")
    
    # 音声ダウンローダーを初期化
    downloader = AudioDownloader(output_dir="examples/audio", audio_format="mp3")
    
    # サンプル動画から音声をダウンロード
    sample_url = "https://www.youtube.com/watch?v=C0DPdy98e4c"  # サンプル動画のURL
    
    result = downloader.download(sample_url, bitrate="192K")
    if result:
        logger.info(f"音声をダウンロードしました: {result}")
    else:
        logger.error("音声のダウンロードに失敗しました")
    
    logger.info("=" * 50)

def example_youtube_features():
    """YouTube専用機能の例"""
    logger.info("=== YouTube専用機能の例 ===")
    
    # YouTubeダウンローダーを初期化
    downloader = YouTubeDownloader(output_dir="examples/youtube")
    
    # サンプルプレイリスト (クリエイティブ・コモンズライセンスのショート動画集などを指定)
    sample_playlist = "https://www.youtube.com/playlist?list=PLzH6n4zXuckoAod3z31QEST1ZaizBuNHh"
    
    # プレイリストから最初の2つの動画をダウンロード
    logger.info("プレイリストから動画をダウンロード...")
    results = downloader.download_playlist(sample_playlist, max_videos=2)
    
    if results:
        logger.info(f"{len(results)}個の動画をダウンロードしました")
    else:
        logger.error("プレイリストのダウンロードに失敗しました")
    
    # チャプター付き動画のダウンロード (チャプター付きの動画URLを指定)
    sample_chaptered_video = "https://www.youtube.com/watch?v=C0DPdy98e4c"
    
    logger.info("チャプター情報付き動画をダウンロード...")
    result = downloader.download_with_chapters(sample_chaptered_video)
    
    if result:
        logger.info(f"チャプター付き動画をダウンロードしました: {result}")
    else:
        logger.error("チャプター付き動画のダウンロードに失敗しました")
    
    logger.info("=" * 50)

def main():
    """サンプルを実行"""
    # 出力ディレクトリを作成
    os.makedirs("examples/videos", exist_ok=True)
    os.makedirs("examples/audio", exist_ok=True)
    os.makedirs("examples/youtube", exist_ok=True)
    
    try:
        example_video_download()
        example_audio_download()
        example_youtube_features()
        
        logger.info("すべてのサンプルが完了しました！")
    except Exception as e:
        logger.error(f"サンプル実行中にエラーが発生しました: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
