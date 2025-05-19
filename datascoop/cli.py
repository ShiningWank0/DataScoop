"""
DataScoopコマンドラインインターフェース
"""

import os
import sys
import argparse
import logging
from .downloaders import VideoDownloader, AudioDownloader, YouTubeDownloader, AbemaDownloader
from .utils.helpers import setup_logger, get_platform_from_url, check_available_formats
from .utils.config import ConfigManager
from .interactive import InteractiveDownloader

logger = setup_logger()

def parse_arguments():
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser(
        description="yt-dlpを使用した動画/音声ダウンローダー（デフォルトは対話モード）"
    )
    
    parser.add_argument(
        "url", 
        help="ダウンロードするコンテンツのURL (指定するとコマンドラインモードで動作)",
        nargs="?",
        default=None
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="URLを指定しても強制的に対話モードを使用する"
    )
    
    parser.add_argument(
        "-t", "--type",
        choices=["video", "audio", "both"],
        default="video",
        help="ダウンロードするコンテンツの種類 (デフォルト: video)"
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        default="downloads",
        help="出力ディレクトリ (デフォルト: downloads)"
    )
    
    parser.add_argument(
        "-f", "--filename",
        help="出力ファイル名 (拡張子なし)"
    )
    
    parser.add_argument(
        "-q", "--quality",
        default="best",
        help="動画/音声の品質 (デフォルト: best)"
    )
    
    parser.add_argument(
        "--audio-format",
        default="mp3",
        choices=["mp3", "m4a", "wav", "flac"],
        help="音声フォーマット (デフォルト: mp3)"
    )
    
    parser.add_argument(
        "--video-format",
        default="mp4",
        choices=["mp4", "webm", "mkv"],
        help="動画フォーマット (デフォルト: mp4)"
    )
    
    parser.add_argument(
        "--subtitles",
        action="store_true",
        help="可能であれば字幕もダウンロード"
    )
    
    parser.add_argument(
        "--list-formats",
        action="store_true",
        help="利用可能なフォーマットを表示"
    )
    
    parser.add_argument(
        "--batch-file",
        help="URLリストを含むファイルからバッチダウンロード"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="詳細なログを出力"
    )
    
    parser.add_argument(
        "--version",
        action="store_true",
        help="バージョン情報を表示"
    )
    
    return parser.parse_args()

def print_version():
    """バージョン情報を表示"""
    from . import __version__
    print(f"DataScoop version {__version__}")
    print("A Python application for downloading videos and audio using yt-dlp")
    sys.exit(0)

def print_formats(url):
    """利用可能なフォーマットを表示"""
    if not url:
        logger.error("フォーマット一覧を取得するにはURLを指定してください")
        sys.exit(1)
        
    formats = check_available_formats(url)
    
    if not formats:
        logger.error("利用可能なフォーマットを取得できませんでした")
        sys.exit(1)
        
    print(f"\n{url} の利用可能なフォーマット:")
    print("-" * 80)
    print(f"{'ID':<8} {'拡張子':<8} {'解像度':<12} {'FPS':<6} {'コーデック':<15} {'ファイルサイズ':<12} {'タイプ':<8}")
    print("-" * 80)
    
    for fmt in formats:
        # 主要な情報を抽出
        fmt_id = fmt.get('format_id', 'N/A')
        ext = fmt.get('ext', 'N/A')
        resolution = f"{fmt.get('width', 'N/A')}x{fmt.get('height', 'N/A')}" if fmt.get('width') else 'N/A'
        fps = fmt.get('fps', 'N/A')
        codec = fmt.get('vcodec', 'N/A') if fmt.get('vcodec') != 'none' else fmt.get('acodec', 'N/A')
        filesize = f"{fmt.get('filesize', 0) / (1024 * 1024):.2f} MB" if fmt.get('filesize') else 'N/A'
        
        # 音声か動画かを判定
        if fmt.get('vcodec') == 'none':
            type_ = 'audio'
        elif fmt.get('acodec') == 'none':
            type_ = 'video'
        else:
            type_ = 'both'
            
        print(f"{fmt_id:<8} {ext:<8} {resolution:<12} {fps:<6} {codec:<15} {filesize:<12} {type_:<8}")
    
    print("-" * 80)
    sys.exit(0)

def process_batch_file(batch_file, args):
    """バッチファイルからURLリストを処理する"""
    if not os.path.exists(batch_file):
        logger.error(f"バッチファイルが見つかりません: {batch_file}")
        sys.exit(1)
        
    with open(batch_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    
    if not urls:
        logger.error("バッチファイルに有効なURLが含まれていません")
        sys.exit(1)
        
    logger.info(f"{len(urls)}件のURLを処理します...")
    
    for i, url in enumerate(urls, 1):
        logger.info(f"[{i}/{len(urls)}] {url} をダウンロード中...")
        download_content(url, args)
    
    logger.info("バッチダウンロードが完了しました")

def download_content(url, args):
    """指定されたURLからコンテンツをダウンロードする"""
    # URLからプラットフォームを判定
    platform = get_platform_from_url(url)
    logger.info(f"検出されたプラットフォーム: {platform}")
    
    # コンテンツの種類に応じたダウンローダーを準備
    if args.type in ["video", "both"]:
        video_output_dir = os.path.join(args.output_dir, "videos") if args.type == "both" else args.output_dir
        
        # プラットフォームに応じたダウンローダーを選択
        if platform == 'youtube':
            video_downloader = YouTubeDownloader(output_dir=video_output_dir, quality=args.quality)
        elif platform == 'abema':
            video_downloader = AbemaDownloader(output_dir=video_output_dir, quality=args.quality)
        else:
            # その他のプラットフォームは一般的なVideoDownloaderを使用
            video_downloader = VideoDownloader(output_dir=video_output_dir, quality=args.quality)
        
        # 動画をダウンロード
        logger.info("動画のダウンロードを開始します...")
        video_file = video_downloader.download(
            url, 
            filename=args.filename,
            format=f"bestvideo[ext={args.video_format}]+bestaudio/best[ext={args.video_format}]",
            subtitles=args.subtitles
        )
        
        if video_file:
            logger.info(f"動画ダウンロード成功: {video_file}")
        else:
            logger.error("動画のダウンロードに失敗しました")
    
    if args.type in ["audio", "both"]:
        audio_output_dir = os.path.join(args.output_dir, "audio")
        audio_downloader = AudioDownloader(
            output_dir=audio_output_dir, 
            quality=args.quality,
            audio_format=args.audio_format
        )
        
        # 音声をダウンロード
        logger.info("音声のダウンロードを開始します...")
        audio_file = audio_downloader.download(
            url, 
            filename=args.filename,
            bitrate="192K"
        )
        
        if audio_file:
            logger.info(f"音声ダウンロード成功: {audio_file}")
        else:
            logger.error("音声のダウンロードに失敗しました")

def main():
    """メイン関数"""
    args = parse_arguments()
    
    # バージョン情報表示
    if args.version:
        print_version()
        return
    
    # 詳細ログが有効の場合、ログレベルを DEBUG に設定
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("詳細ログが有効になりました")
    
    # URLが指定されていて、かつ明示的に対話モードが無効の場合のみコマンドラインモードを使用
    # つまり、デフォルトは対話モード
    use_command_line = args.url and not args.interactive
    
    if not use_command_line:
        # 対話モードの実行（デフォルト）
        interactive = InteractiveDownloader()
        interactive.start()
        return
    
    # 以下はコマンドラインモードの処理
    
    # フォーマット一覧表示
    if args.list_formats:
        if not args.url:
            logger.error("フォーマット一覧を取得するにはURLを指定してください")
            # フォールバックとして対話モードを使用
            interactive = InteractiveDownloader()
            interactive.start()
            return
        print_formats(args.url)
        return
    
    # バッチファイルがある場合はバッチ処理
    if args.batch_file:
        process_batch_file(args.batch_file, args)
        return
    
    # URLが指定されている場合はコマンドラインモードでダウンロード
    download_content(args.url, args)
    logger.info("処理が完了しました")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("ユーザーによって処理が中断されました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)
