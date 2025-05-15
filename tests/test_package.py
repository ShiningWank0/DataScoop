"""
パッケージ情報のテスト
"""

import re
import importlib.metadata
import toml

def test_version_format():
    """バージョン形式のテスト"""
    import datascoop
    
    # pyproject.tomlからバージョンを取得
    try:
        with open("pyproject.toml", "r") as f:
            pyproject_data = toml.load(f)
            pyproject_version = pyproject_data["project"]["version"]
    except (FileNotFoundError, KeyError, toml.TomlDecodeError):
        pyproject_version = None
    
    # パッケージのバージョン
    version = datascoop.__version__
    
    # バージョン番号がセマンティックバージョニング（X.Y.Z）に準拠しているかをチェック
    pattern = r'^\d+\.\d+\.\d+(\-[a-zA-Z0-9\.]+)?(\+[a-zA-Z0-9\.]+)?$'
    
    # not unknownの場合のみバージョン形式をチェック
    if version != "unknown":
        assert re.match(pattern, version) is not None, f"バージョン '{version}' がセマンティックバージョニングに準拠していません"
    
    # pyproject.tomlとバージョンが一致するか
    if pyproject_version and version != "unknown":
        assert version == pyproject_version, f"__version__({version})とpyproject.toml({pyproject_version})のバージョンが一致しません"

def test_exports():
    """エクスポートされる要素のテスト"""
    import datascoop
    
    # 重要なクラスがエクスポートされていることを確認
    assert hasattr(datascoop, 'VideoDownloader')
    assert hasattr(datascoop, 'AudioDownloader')
    assert hasattr(datascoop, 'YouTubeDownloader')
    assert hasattr(datascoop, 'ConfigManager')
