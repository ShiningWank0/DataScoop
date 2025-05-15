"""
ヘルパー関数のテスト
"""

import pytest
from datascoop.utils.helpers import (
    sanitize_filename,
    extract_video_id,
    get_platform_from_url,
    verify_output_directory,
)
import os
import shutil
import tempfile

class TestHelpers:
    """ヘルパー関数のテストクラス"""
    
    def test_sanitize_filename(self):
        """sanitize_filename関数のテスト"""
        # 無効な文字がある場合
        assert sanitize_filename('test/file:name?') == 'testfilename'
        # スペースがある場合
        assert sanitize_filename('test file name') == 'test_file_name'
        # 正常な文字だけの場合
        assert sanitize_filename('normal_filename') == 'normal_filename'
    
    def test_extract_video_id(self):
        """extract_video_id関数のテスト"""
        # 標準的なYouTube URL
        assert extract_video_id('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
        # 短縮URL
        assert extract_video_id('https://youtu.be/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
        # ショートURL
        assert extract_video_id('https://www.youtube.com/shorts/dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
        # 無効なURL
        assert extract_video_id('https://example.com') is None
    
    def test_get_platform_from_url(self):
        """get_platform_from_url関数のテスト"""
        # YouTube URL
        assert get_platform_from_url('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == 'youtube'
        assert get_platform_from_url('https://youtu.be/dQw4w9WgXcQ') == 'youtube'
        # ニコニコ動画URL
        assert get_platform_from_url('https://www.nicovideo.jp/watch/sm12345678') == 'niconico'
        assert get_platform_from_url('https://nico.ms/sm12345678') == 'niconico'
        # Abema URL
        assert get_platform_from_url('https://abema.tv/video/episode/12345') == 'abema'
        # 未知のプラットフォーム
        assert get_platform_from_url('https://example.com/video') == 'unknown'
    
    def test_verify_output_directory(self):
        """verify_output_directory関数のテスト"""
        # 一時ディレクトリを作成
        temp_dir = tempfile.mkdtemp()
        try:
            # 存在するディレクトリ
            assert verify_output_directory(temp_dir) is True
            
            # 存在しないが作成可能なディレクトリ
            new_dir = os.path.join(temp_dir, 'new_dir')
            assert verify_output_directory(new_dir) is True
            assert os.path.exists(new_dir) is True
            
            # 空のパス
            assert verify_output_directory('') is False
        finally:
            # 後片付け
            shutil.rmtree(temp_dir)
