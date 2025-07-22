#!/usr/bin/env python3
"""
YouTube Channel Management Tools for MCP Server
自分のチャンネルのコンテンツを管理するためのツール集
"""

import json
import re
from datetime import datetime
from typing import Any

from googleapiclient.errors import HttpError

from .youtube_auth import YouTubeAuthManager


class YouTubeChannelManager:
    """YouTubeチャンネル管理クラス"""

    def __init__(self):
        """Initialize channel manager with authentication"""
        self.auth_manager = YouTubeAuthManager()
        self.youtube = None
        self.youtube_analytics = None
        self.channel_id = None
        self.uploads_playlist_id = None
        self._authenticate()

    def _authenticate(self):
        """認証とチャンネル情報の初期化"""
        try:
            self.youtube, self.youtube_analytics = self.auth_manager.authenticate()
            channel_info = self.auth_manager.get_channel_info()
            self.channel_id = channel_info['id']
            self.uploads_playlist_id = channel_info['uploads_playlist_id']
        except Exception as e:
            raise Exception(f"認証エラー: {str(e)}")

    def list_my_videos(self, max_results: int = 50, page_token: str | None = None) -> dict[str, Any]:
        """
        自分のチャンネルの動画一覧を取得
        
        Args:
            max_results: 取得する動画数（最大50）
            page_token: ページネーショントークン
            
        Returns:
            動画リストと次ページトークン
        """
        try:
            # アップロード済み動画のプレイリストから取得
            request = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=self.uploads_playlist_id,
                maxResults=min(max_results, 50),
                pageToken=page_token
            )
            response = request.execute()

            video_ids = []
            basic_info = []

            # 基本情報を収集
            for item in response.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
                basic_info.append({
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'published_at': item['snippet']['publishedAt']
                })

            # 詳細情報を一括取得
            if video_ids:
                videos_request = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails,status',
                    id=','.join(video_ids)
                )
                videos_response = videos_request.execute()

                # 詳細情報をマージ
                videos = []
                for i, video in enumerate(videos_response.get('items', [])):
                    video_data = {
                        'video_id': video['id'],
                        'title': video['snippet']['title'],
                        'description': video['snippet']['description'],
                        'tags': video['snippet'].get('tags', []),
                        'published_at': video['snippet']['publishedAt'],
                        'thumbnail': video['snippet']['thumbnails']['high']['url'],
                        'duration': self._parse_duration(video['contentDetails']['duration']),
                        'privacy_status': video['status']['privacyStatus'],
                        'statistics': {
                            'view_count': int(video['statistics'].get('viewCount', 0)),
                            'like_count': int(video['statistics'].get('likeCount', 0)),
                            'comment_count': int(video['statistics'].get('commentCount', 0))
                        },
                        'category_id': video['snippet']['categoryId'],
                        'default_language': video['snippet'].get('defaultLanguage'),
                        'default_audio_language': video['snippet'].get('defaultAudioLanguage')
                    }
                    videos.append(video_data)

            return {
                'videos': videos,
                'next_page_token': response.get('nextPageToken'),
                'total_results': response.get('pageInfo', {}).get('totalResults', 0)
            }

        except HttpError as e:
            raise Exception(f"動画リスト取得エラー: {str(e)}")

    def update_video_metadata(self, video_id: str, title: str | None = None,
                            description: str | None = None, tags: list[str] | None = None,
                            category_id: str | None = None) -> dict[str, Any]:
        """
        動画のメタデータを更新
        
        Args:
            video_id: 動画ID
            title: 新しいタイトル
            description: 新しい説明
            tags: 新しいタグリスト
            category_id: カテゴリID
            
        Returns:
            更新結果
        """
        try:
            # 現在の動画情報を取得
            video_request = self.youtube.videos().list(
                part='snippet',
                id=video_id
            )
            video_response = video_request.execute()

            if not video_response.get('items'):
                raise Exception(f"動画が見つかりません: {video_id}")

            video = video_response['items'][0]
            snippet = video['snippet']

            # 更新する項目のみ変更
            if title is not None:
                snippet['title'] = title
            if description is not None:
                snippet['description'] = description
            if tags is not None:
                snippet['tags'] = tags
            if category_id is not None:
                snippet['categoryId'] = category_id

            # 更新リクエスト
            update_request = self.youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': snippet
                }
            )
            update_response = update_request.execute()

            return {
                'success': True,
                'video_id': video_id,
                'updated_fields': {
                    'title': title if title else 'unchanged',
                    'description': 'updated' if description else 'unchanged',
                    'tags': len(tags) if tags else 'unchanged',
                    'category_id': category_id if category_id else 'unchanged'
                }
            }

        except HttpError as e:
            raise Exception(f"動画メタデータ更新エラー: {str(e)}")

    def batch_update_videos(self, updates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        複数の動画を一括更新
        
        Args:
            updates: 更新情報のリスト
                    [{'video_id': 'xxx', 'title': 'new title', ...}, ...]
                    
        Returns:
            更新結果のリスト
        """
        results = []

        for update in updates:
            try:
                video_id = update.pop('video_id')
                result = self.update_video_metadata(video_id, **update)
                results.append(result)
            except Exception as e:
                results.append({
                    'success': False,
                    'video_id': update.get('video_id', 'unknown'),
                    'error': str(e)
                })

        return results

    def add_video_chapters(self, video_id: str, chapters: list[dict[str, Any]]) -> dict[str, Any]:
        """
        動画に目次（チャプター）を追加
        
        Args:
            video_id: 動画ID
            chapters: チャプター情報のリスト
                    [{'time': '0:00', 'title': 'イントロ'}, ...]
                    
        Returns:
            更新結果
        """
        try:
            # 現在の説明を取得
            video_request = self.youtube.videos().list(
                part='snippet',
                id=video_id
            )
            video_response = video_request.execute()

            if not video_response.get('items'):
                raise Exception(f"動画が見つかりません: {video_id}")

            current_description = video_response['items'][0]['snippet']['description']

            # チャプター文字列を生成
            chapter_text = "\n\n📍 目次\n"
            for chapter in chapters:
                chapter_text += f"{chapter['time']} {chapter['title']}\n"

            # 既存のチャプターを削除（あれば）
            chapter_pattern = r'\n*📍 目次\n[\s\S]*?(?=\n\n|$)'
            new_description = re.sub(chapter_pattern, '', current_description)

            # 新しいチャプターを追加
            new_description = chapter_text + "\n" + new_description.strip()

            # 説明を更新
            result = self.update_video_metadata(video_id, description=new_description)
            result['chapters_added'] = len(chapters)

            return result

        except Exception as e:
            raise Exception(f"チャプター追加エラー: {str(e)}")

    def generate_buzz_title(self, current_title: str, video_stats: dict[str, Any] | None = None) -> list[str]:
        """
        バズるタイトルを生成（簡易版）
        
        Args:
            current_title: 現在のタイトル
            video_stats: 動画の統計情報
            
        Returns:
            提案タイトルのリスト
        """
        suggestions = []

        # 基本的なパターンを適用
        patterns = [
            {
                'template': '【必見】{title}【{year}年最新】',
                'condition': lambda t: len(t) < 30
            },
            {
                'template': '{title}した結果...衝撃の事実が判明',
                'condition': lambda t: '方法' in t or 'やり方' in t
            },
            {
                'template': '知らないと損する{title}のコツ',
                'condition': lambda t: 'コツ' not in t and len(t) < 20
            },
            {
                'template': '{title}｜プロが教える3つのポイント',
                'condition': lambda t: '初心者' in t or '入門' in t
            },
            {
                'template': '【{views}万回再生】{title}がヤバすぎる件',
                'condition': lambda t: video_stats and video_stats.get('view_count', 0) > 10000
            }
        ]

        year = datetime.now().year
        base_title = re.sub(r'【.*?】', '', current_title).strip()

        for pattern in patterns:
            if pattern['condition'](base_title):
                if '{views}' in pattern['template'] and video_stats:
                    views = video_stats.get('view_count', 0) // 10000
                    if views > 0:
                        suggestion = pattern['template'].format(
                            title=base_title,
                            year=year,
                            views=views
                        )
                    else:
                        continue
                else:
                    suggestion = pattern['template'].format(
                        title=base_title,
                        year=year
                    )

                # 文字数制限（YouTube は100文字まで）
                if len(suggestion) <= 100:
                    suggestions.append(suggestion)

        # 元のタイトルも含める
        suggestions.insert(0, current_title)

        return suggestions[:5]  # 最大5個の提案

    def _parse_duration(self, duration: str) -> str:
        """ISO 8601形式の動画時間を人間が読める形式に変換"""
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration)

        if not match:
            return duration

        hours, minutes, seconds = match.groups()

        parts = []
        if hours:
            parts.append(f"{hours}時間")
        if minutes:
            parts.append(f"{minutes}分")
        if seconds:
            parts.append(f"{seconds}秒")

        return "".join(parts) if parts else "0秒"


# MCP Tools Implementation
def list_my_videos_tool(max_results: int = 50, page_token: str | None = None) -> str:
    """
    自分のYouTubeチャンネルの動画一覧を取得
    
    Args:
        max_results: 取得する動画数（最大50）
        page_token: 次ページ取得用のトークン
        
    Returns:
        動画一覧のJSON文字列
    """
    try:
        manager = YouTubeChannelManager()
        result = manager.list_my_videos(max_results, page_token)

        # 結果を整形
        output = {
            "channel_videos": result['videos'],
            "total_videos": result['total_results'],
            "next_page_token": result.get('next_page_token'),
            "has_more": result.get('next_page_token') is not None
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"動画リスト取得エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)


def update_video_metadata_tool(video_id: str, title: str | None = None,
                             description: str | None = None,
                             tags: list[str] | None = None) -> str:
    """
    YouTube動画のメタデータを更新
    
    Args:
        video_id: 動画ID
        title: 新しいタイトル
        description: 新しい説明
        tags: 新しいタグのリスト
        
    Returns:
        更新結果のJSON文字列
    """
    try:
        manager = YouTubeChannelManager()
        result = manager.update_video_metadata(video_id, title, description, tags)

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"メタデータ更新エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)


def batch_update_videos_tool(updates: str) -> str:
    """
    複数の動画を一括更新
    
    Args:
        updates: JSON形式の更新情報
                '[{"video_id": "xxx", "title": "新タイトル", "tags": ["tag1", "tag2"]}, ...]'
                
    Returns:
        更新結果のJSON文字列
    """
    try:
        update_list = json.loads(updates)
        manager = YouTubeChannelManager()
        results = manager.batch_update_videos(update_list)

        # サマリーを作成
        success_count = sum(1 for r in results if r.get('success'))
        failed_count = len(results) - success_count

        output = {
            "summary": {
                "total": len(results),
                "success": success_count,
                "failed": failed_count
            },
            "results": results
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except json.JSONDecodeError:
        return json.dumps({
            "error": "無効なJSON形式です"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "error": f"一括更新エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)


def add_video_chapters_tool(video_id: str, chapters: str) -> str:
    """
    動画に目次（チャプター）を追加
    
    Args:
        video_id: 動画ID
        chapters: JSON形式のチャプター情報
                 '[{"time": "0:00", "title": "イントロ"}, {"time": "1:30", "title": "本編"}, ...]'
                 
    Returns:
        更新結果のJSON文字列
    """
    try:
        chapter_list = json.loads(chapters)
        manager = YouTubeChannelManager()
        result = manager.add_video_chapters(video_id, chapter_list)

        return json.dumps(result, ensure_ascii=False, indent=2)

    except json.JSONDecodeError:
        return json.dumps({
            "error": "無効なJSON形式です"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "error": f"チャプター追加エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)


def generate_buzz_title_tool(video_id: str) -> str:
    """
    動画のバズるタイトルを生成
    
    Args:
        video_id: 動画ID
        
    Returns:
        タイトル提案のJSON文字列
    """
    try:
        manager = YouTubeChannelManager()

        # 動画情報を取得
        videos = manager.list_my_videos(max_results=50)
        target_video = None

        for video in videos['videos']:
            if video['video_id'] == video_id:
                target_video = video
                break

        if not target_video:
            return json.dumps({
                "error": f"動画が見つかりません: {video_id}"
            }, ensure_ascii=False, indent=2)

        # タイトル生成
        suggestions = manager.generate_buzz_title(
            target_video['title'],
            target_video['statistics']
        )

        output = {
            "current_title": target_video['title'],
            "suggestions": suggestions,
            "current_stats": {
                "views": target_video['statistics']['view_count'],
                "likes": target_video['statistics']['like_count'],
                "comments": target_video['statistics']['comment_count']
            }
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"タイトル生成エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)


def setup_youtube_oauth_tool() -> str:
    """
    YouTube OAuth認証の設定方法を表示
    
    Returns:
        設定手順のJSON文字列
    """
    from .youtube_auth import setup_oauth_credentials

    setup_oauth_credentials()

    return json.dumps({
        "message": "OAuth認証の設定方法を表示しました。コンソールを確認してください。",
        "next_steps": [
            "Google Cloud ConsoleでOAuth認証情報を作成",
            "credentials.jsonをダウンロード",
            "~/.youtube_mcp/credentials.json に保存",
            "MCPツールを実行して認証"
        ]
    }, ensure_ascii=False, indent=2)
