#!/usr/bin/env python3
"""
YouTube OAuth 2.0 認証モジュール
チャンネル所有者向けの認証機能を提供
"""

import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# OAuth2.0のスコープ設定
SCOPES = [
    'https://www.googleapis.com/auth/youtube',  # YouTube全般の権限
    'https://www.googleapis.com/auth/youtube.readonly',  # 読み取り専用
    'https://www.googleapis.com/auth/youtube.force-ssl',  # SSL強制
    'https://www.googleapis.com/auth/yt-analytics.readonly',  # Analytics読み取り
    'https://www.googleapis.com/auth/yt-analytics-monetary.readonly',  # 収益分析
]

# 認証情報の保存パス
TOKEN_PATH = Path.home() / '.youtube_mcp' / 'token.pickle'
CREDENTIALS_PATH = Path.home() / '.youtube_mcp' / 'credentials.json'


class YouTubeAuthManager:
    """YouTube OAuth認証を管理するクラス"""

    def __init__(self, credentials_path: str | None = None):
        """
        Initialize auth manager
        
        Args:
            credentials_path: OAuth2 credentials JSONファイルのパス
        """
        self.credentials_path = Path(credentials_path) if credentials_path else CREDENTIALS_PATH
        self.token_path = TOKEN_PATH
        self.creds = None

        # 保存ディレクトリの作成
        self.token_path.parent.mkdir(parents=True, exist_ok=True)

    def authenticate(self) -> tuple:
        """
        OAuth2.0認証を実行し、YouTube APIクライアントを返す
        
        Returns:
            tuple: (youtube_client, youtube_analytics_client)
        """
        # 既存のトークンをロード
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # トークンが無効または期限切れの場合
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # トークンのリフレッシュ
                self.creds.refresh(Request())
            else:
                # 新規認証フロー
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"認証情報ファイルが見つかりません: {self.credentials_path}\n"
                        "Google Cloud ConsoleからOAuth 2.0クライアントIDをダウンロードし、"
                        f"{self.credentials_path} に保存してください。"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # トークンを保存
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        # APIクライアントを構築
        youtube = build('youtube', 'v3', credentials=self.creds)
        youtube_analytics = build('youtubeAnalytics', 'v2', credentials=self.creds)

        return youtube, youtube_analytics

    def get_credentials(self):
        """
        認証済みの credentials オブジェクトを取得
        
        Returns:
            google.oauth2.credentials.Credentials: 認証情報
        """
        # 既存のトークンをロード
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # トークンが無効または期限切れの場合
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                # トークンのリフレッシュ
                self.creds.refresh(Request())
            else:
                # 新規認証フロー
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"認証情報ファイルが見つかりません: {self.credentials_path}\n"
                        "Google Cloud ConsoleからOAuth 2.0クライアントIDをダウンロードし、"
                        f"{self.credentials_path} に保存してください。"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            # トークンを保存
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        return self.creds

    def get_channel_info(self) -> dict:
        """
        認証されたユーザーのチャンネル情報を取得
        
        Returns:
            チャンネル情報の辞書
        """
        youtube, _ = self.authenticate()

        request = youtube.channels().list(
            part='snippet,statistics,contentDetails',
            mine=True
        )
        response = request.execute()

        if not response.get('items'):
            raise Exception("チャンネル情報が取得できませんでした")

        channel = response['items'][0]
        return {
            'id': channel['id'],
            'title': channel['snippet']['title'],
            'description': channel['snippet']['description'],
            'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
            'video_count': int(channel['statistics'].get('videoCount', 0)),
            'view_count': int(channel['statistics'].get('viewCount', 0)),
            'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads']
        }

    def revoke_token(self):
        """保存されたトークンを削除"""
        if self.token_path.exists():
            self.token_path.unlink()
            print("認証トークンを削除しました")

    def is_authenticated(self) -> bool:
        """認証済みかどうかを確認"""
        if not self.token_path.exists():
            return False

        try:
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
                return creds and creds.valid
        except:
            return False


def setup_oauth_credentials():
    """
    OAuth認証の初期設定を行うヘルパー関数
    Google Cloud ConsoleでのOAuth設定手順を表示
    """
    print("""
YouTube OAuth 2.0 認証の設定方法:

1. Google Cloud Consoleにアクセス:
   https://console.cloud.google.com/

2. プロジェクトを作成または選択

3. YouTube Data API v3 と YouTube Analytics API を有効化:
   - APIとサービス > ライブラリ
   - "YouTube Data API v3" を検索して有効化
   - "YouTube Analytics API" を検索して有効化

4. OAuth 2.0 認証情報を作成:
   - APIとサービス > 認証情報
   - "認証情報を作成" > "OAuth クライアント ID"
   - アプリケーションの種類: "デスクトップ"
   - 名前を入力して作成

5. JSONファイルをダウンロード:
   - 作成した認証情報の右端のダウンロードボタンをクリック
   - ダウンロードしたファイルを以下の場所に保存:
     ~/.youtube_mcp/credentials.json

6. 初回実行時にブラウザが開き、Googleアカウントでの認証を求められます
""")


if __name__ == "__main__":
    # 認証設定の説明を表示
    setup_oauth_credentials()
