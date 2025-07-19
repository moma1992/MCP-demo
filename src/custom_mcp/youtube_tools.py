#!/usr/bin/env python3
"""
YouTube分析ツール for MCP Server
YouTube Data API v3を使用して動画検索・分析機能を提供
"""

import json
import os
import re
from datetime import datetime, timedelta
from typing import Any

from googleapiclient.discovery import build


class YouTubeAnalyzer:
    """YouTube Data API v3を使用した動画分析クラス"""

    def __init__(self, api_key: str):
        """
        Initialize YouTube analyzer with API key
        
        Args:
            api_key: YouTube Data API v3 API key
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def search_popular_videos(self, keyword: str, max_results: int = 10) -> list[dict[str, Any]]:
        """
        キーワードで人気動画を検索
        
        Args:
            keyword: 検索キーワード
            max_results: 取得する動画数（デフォルト: 10）
            
        Returns:
            人気動画のリスト
        """
        try:
            # 人気順で動画を検索
            search_response = self.youtube.search().list(
                q=keyword,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                order='relevance',  # 関連度順（人気度を含む）
                regionCode='JP',  # 日本の結果を優先
                relevanceLanguage='ja'
            ).execute()

            video_ids = []
            videos_data = []

            # 動画IDを収集
            for item in search_response['items']:
                video_ids.append(item['id']['videoId'])
                videos_data.append({
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'description': item['snippet']['description'][:200] + '...' if len(item['snippet']['description']) > 200 else item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url'] if 'high' in item['snippet']['thumbnails'] else item['snippet']['thumbnails']['default']['url']
                })

            # 動画の詳細統計を取得
            if video_ids:
                stats_response = self.youtube.videos().list(
                    part='statistics,contentDetails',
                    id=','.join(video_ids)
                ).execute()

                # 統計データを動画データに追加
                for i, stats_item in enumerate(stats_response['items']):
                    if i < len(videos_data):
                        videos_data[i].update({
                            'view_count': int(stats_item['statistics'].get('viewCount', 0)),
                            'like_count': int(stats_item['statistics'].get('likeCount', 0)),
                            'comment_count': int(stats_item['statistics'].get('commentCount', 0)),
                            'duration': stats_item['contentDetails']['duration'],
                            'engagement_rate': self._calculate_engagement_rate(stats_item['statistics'])
                        })

            # 人気度でソート（視聴回数 + エンゲージメント率）
            videos_data.sort(key=lambda x: x.get('view_count', 0) + (x.get('engagement_rate', 0) * 1000), reverse=True)

            return videos_data

        except Exception as e:
            raise Exception(f"YouTube検索エラー: {str(e)}")

    def analyze_video_popularity(self, video_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        動画の人気要因を分析
        
        Args:
            video_data: 動画データのリスト
            
        Returns:
            分析結果
        """
        if not video_data:
            return {"error": "分析する動画データがありません"}

        # 基本統計
        total_views = sum(video.get('view_count', 0) for video in video_data)
        total_likes = sum(video.get('like_count', 0) for video in video_data)
        total_comments = sum(video.get('comment_count', 0) for video in video_data)

        avg_views = total_views / len(video_data)
        avg_likes = total_likes / len(video_data)
        avg_comments = total_comments / len(video_data)

        # タイトル分析
        title_keywords = self._analyze_title_patterns(video_data)

        # 時間帯分析
        publish_time_analysis = self._analyze_publish_times(video_data)

        # エンゲージメント分析
        engagement_analysis = self._analyze_engagement_patterns(video_data)

        # 人気要因の特定
        success_factors = self._identify_success_factors(video_data)

        return {
            "基本統計": {
                "動画数": len(video_data),
                "平均視聴回数": f"{avg_views:,.0f}",
                "平均いいね数": f"{avg_likes:,.0f}",
                "平均コメント数": f"{avg_comments:,.0f}",
                "総視聴回数": f"{total_views:,.0f}"
            },
            "タイトル傾向": title_keywords,
            "投稿時間分析": publish_time_analysis,
            "エンゲージメント分析": engagement_analysis,
            "成功要因": success_factors,
            "トップ3動画": [
                {
                    "タイトル": video['title'],
                    "チャンネル": video['channel'],
                    "視聴回数": f"{video.get('view_count', 0):,}",
                    "いいね数": f"{video.get('like_count', 0):,}",
                    "エンゲージメント率": f"{video.get('engagement_rate', 0):.2f}%"
                }
                for video in video_data[:3]
            ]
        }

    def get_detailed_video_analysis(self, video_id: str) -> dict[str, Any]:
        """
        特定の動画の詳細分析
        
        Args:
            video_id: YouTube動画ID
            
        Returns:
            詳細分析結果
        """
        try:
            # 動画の詳細情報を取得
            video_response = self.youtube.videos().list(
                part='snippet,statistics,contentDetails,status',
                id=video_id
            ).execute()

            if not video_response['items']:
                return {"error": "動画が見つかりません"}

            video = video_response['items'][0]

            # コメントを取得（最新20件）
            comments = self._get_video_comments(video_id, max_results=20)

            # 詳細分析
            analysis = {
                "動画情報": {
                    "タイトル": video['snippet']['title'],
                    "チャンネル": video['snippet']['channelTitle'],
                    "投稿日": video['snippet']['publishedAt'],
                    "説明": video['snippet']['description'][:300] + '...' if len(video['snippet']['description']) > 300 else video['snippet']['description'],
                    "カテゴリID": video['snippet']['categoryId'],
                    "言語": video['snippet'].get('defaultLanguage', 'N/A'),
                    "タグ": video['snippet'].get('tags', [])[:10]  # 最初の10個のタグ
                },
                "パフォーマンス": {
                    "視聴回数": f"{int(video['statistics'].get('viewCount', 0)):,}",
                    "いいね数": f"{int(video['statistics'].get('likeCount', 0)):,}",
                    "コメント数": f"{int(video['statistics'].get('commentCount', 0)):,}",
                    "エンゲージメント率": f"{self._calculate_engagement_rate(video['statistics']):.2f}%",
                    "再生時間": self._convert_duration(video['contentDetails']['duration'])
                },
                "コンテンツ分析": {
                    "タイトル長": len(video['snippet']['title']),
                    "説明文長": len(video['snippet']['description']),
                    "タグ数": len(video['snippet'].get('tags', [])),
                    "サムネイル品質": "高解像度" if 'maxres' in video['snippet']['thumbnails'] else "標準"
                },
                "コメント分析": self._analyze_comments(comments),
                "成功要因推定": self._estimate_success_factors(video, comments)
            }

            return analysis

        except Exception as e:
            return {"error": f"動画分析エラー: {str(e)}"}

    def _calculate_engagement_rate(self, statistics: dict[str, str]) -> float:
        """エンゲージメント率を計算"""
        views = int(statistics.get('viewCount', 0))
        likes = int(statistics.get('likeCount', 0))
        comments = int(statistics.get('commentCount', 0))

        if views == 0:
            return 0.0

        return ((likes + comments) / views) * 100

    def _analyze_title_patterns(self, videos: list[dict[str, Any]]) -> dict[str, Any]:
        """タイトルのパターンを分析"""
        all_titles = [video['title'] for video in videos]

        # よく使われる単語を抽出（日本語対応の簡易版）
        common_words = {}
        for title in all_titles:
            # 簡易的な単語分割（実際の実装では形態素解析を使用推奨）
            words = re.findall(r'[ぁ-んァ-ヴー一-龠]+|[a-zA-Z]+', title)
            for word in words:
                if len(word) > 1:  # 1文字の単語は除外
                    common_words[word] = common_words.get(word, 0) + 1

        # 頻出単語トップ10
        sorted_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "頻出キーワード": [{"単語": word, "出現回数": count} for word, count in sorted_words],
            "平均タイトル長": sum(len(title) for title in all_titles) / len(all_titles),
            "感嘆符使用率": sum(1 for title in all_titles if '!' in title or '！' in title) / len(all_titles) * 100
        }

    def _analyze_publish_times(self, videos: list[dict[str, Any]]) -> dict[str, Any]:
        """投稿時間を分析"""
        publish_hours = []
        publish_days = []

        for video in videos:
            try:
                publish_time = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                # 日本時間に変換
                jst_time = publish_time + timedelta(hours=9)
                publish_hours.append(jst_time.hour)
                publish_days.append(jst_time.strftime('%A'))
            except:
                continue

        # 時間帯分析
        hour_counts = {}
        for hour in publish_hours:
            hour_counts[hour] = hour_counts.get(hour, 0) + 1

        # 曜日分析
        day_counts = {}
        for day in publish_days:
            day_counts[day] = day_counts.get(day, 0) + 1

        # 最適な投稿時間帯を特定
        best_hour = max(hour_counts.items(), key=lambda x: x[1]) if hour_counts else (0, 0)
        best_day = max(day_counts.items(), key=lambda x: x[1]) if day_counts else ("N/A", 0)

        return {
            "最適投稿時間": f"{best_hour[0]}時頃",
            "最適投稿曜日": best_day[0],
            "時間帯別投稿数": dict(sorted(hour_counts.items())),
            "曜日別投稿数": day_counts
        }

    def _analyze_engagement_patterns(self, videos: list[dict[str, Any]]) -> dict[str, Any]:
        """エンゲージメントパターンを分析"""
        high_engagement = [v for v in videos if v.get('engagement_rate', 0) > 2.0]
        low_engagement = [v for v in videos if v.get('engagement_rate', 0) < 1.0]

        return {
            "高エンゲージメント動画数": len(high_engagement),
            "低エンゲージメント動画数": len(low_engagement),
            "平均エンゲージメント率": f"{sum(v.get('engagement_rate', 0) for v in videos) / len(videos):.2f}%",
            "エンゲージメント率分布": {
                "2%以上": len(high_engagement),
                "1-2%": len([v for v in videos if 1.0 <= v.get('engagement_rate', 0) < 2.0]),
                "1%未満": len(low_engagement)
            }
        }

    def _identify_success_factors(self, videos: list[dict[str, Any]]) -> list[str]:
        """成功要因を特定"""
        factors = []

        # 視聴回数の上位25%を成功動画とする
        sorted_videos = sorted(videos, key=lambda x: x.get('view_count', 0), reverse=True)
        top_quarter = sorted_videos[:len(videos)//4] if len(videos) >= 4 else sorted_videos[:1]

        if not top_quarter:
            return ["データが不足しています"]

        # 平均エンゲージメント率が高い
        avg_engagement = sum(v.get('engagement_rate', 0) for v in top_quarter) / len(top_quarter)
        if avg_engagement > 2.0:
            factors.append(f"高エンゲージメント率 (平均{avg_engagement:.1f}%)")

        # タイトルの特徴
        titles = [v['title'] for v in top_quarter]
        if any('!' in title or '！' in title for title in titles):
            factors.append("感嘆符を使用したタイトル")

        if any(len(title) > 30 for title in titles):
            factors.append("詳細なタイトル（30文字以上）")

        # 投稿の一貫性
        channels = [v['channel'] for v in top_quarter]
        if len(set(channels)) < len(channels):
            factors.append("特定チャンネルの継続的な投稿")

        return factors if factors else ["明確な成功パターンは特定できませんでした"]

    def _get_video_comments(self, video_id: str, max_results: int = 20) -> list[dict[str, Any]]:
        """動画のコメントを取得"""
        try:
            comments_response = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                order='relevance'
            ).execute()

            comments = []
            for item in comments_response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'text': comment['textDisplay'],
                    'author': comment['authorDisplayName'],
                    'like_count': comment['likeCount'],
                    'published_at': comment['publishedAt']
                })

            return comments
        except:
            return []

    def _analyze_comments(self, comments: list[dict[str, Any]]) -> dict[str, Any]:
        """コメントを分析"""
        if not comments:
            return {"メッセージ": "コメントデータがありません"}

        # 感情分析（簡易版）
        positive_words = ['素晴らしい', '最高', 'すごい', '感動', '良い', '好き', '面白い', 'ありがとう']
        negative_words = ['つまらない', '嫌い', '最悪', 'ひどい', '悪い', '残念']

        positive_count = 0
        negative_count = 0

        for comment in comments:
            text = comment['text'].lower()
            if any(word in text for word in positive_words):
                positive_count += 1
            if any(word in text for word in negative_words):
                negative_count += 1

        avg_likes = sum(comment['like_count'] for comment in comments) / len(comments)

        return {
            "コメント数": len(comments),
            "平均いいね数": f"{avg_likes:.1f}",
            "感情分析": {
                "ポジティブ": positive_count,
                "ネガティブ": negative_count,
                "ニュートラル": len(comments) - positive_count - negative_count
            },
            "エンゲージメント": "高い" if avg_likes > 5 else "標準" if avg_likes > 1 else "低い"
        }

    def _estimate_success_factors(self, video: dict[str, Any], comments: list[dict[str, Any]]) -> list[str]:
        """個別動画の成功要因を推定"""
        factors = []

        stats = video['statistics']
        snippet = video['snippet']

        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments_count = int(stats.get('commentCount', 0))

        # 高い視聴回数
        if views > 100000:
            factors.append(f"高視聴回数 ({views:,}回)")

        # 高エンゲージメント
        engagement = self._calculate_engagement_rate(stats)
        if engagement > 3.0:
            factors.append(f"高エンゲージメント率 ({engagement:.1f}%)")

        # タイトルの魅力
        title = snippet['title']
        if '!' in title or '！' in title:
            factors.append("感嘆符による注目度向上")

        if len(title) > 40:
            factors.append("詳細で分かりやすいタイトル")

        # タグの活用
        tags = snippet.get('tags', [])
        if len(tags) > 10:
            factors.append("豊富なタグによる検索性向上")

        # コメントの質
        if comments and len(comments) > 0:
            avg_comment_likes = sum(c['like_count'] for c in comments) / len(comments)
            if avg_comment_likes > 5:
                factors.append("質の高いコメントによるエンゲージメント")

        return factors if factors else ["特別な成功要因は特定できませんでした"]

    def _convert_duration(self, duration: str) -> str:
        """ISO 8601形式の動画時間を人間が読める形式に変換"""
        import re

        # PT1H2M10S -> 1時間2分10秒
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
def search_youtube_videos(keyword: str, max_results: int = 10) -> str:
    """
    キーワードでYouTube動画を検索し、人気動画を分析
    
    Args:
        keyword: 検索キーワード
        max_results: 取得する動画数（デフォルト: 10）
    
    Returns:
        検索結果と分析の JSON文字列
    """
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        return json.dumps({
            "error": "YouTube API keyが設定されていません。環境変数YOUTUBE_API_KEYを設定してください。"
        }, ensure_ascii=False, indent=2)

    try:
        analyzer = YouTubeAnalyzer(api_key)
        videos = analyzer.search_popular_videos(keyword, max_results)
        analysis = analyzer.analyze_video_popularity(videos)

        result = {
            "検索キーワード": keyword,
            "検索結果": videos,
            "分析結果": analysis
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"YouTube検索エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)


def analyze_youtube_video(video_id: str) -> str:
    """
    特定のYouTube動画を詳細分析
    
    Args:
        video_id: YouTube動画ID (URLのv=以降の部分)
    
    Returns:
        動画の詳細分析結果の JSON文字列
    """
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        return json.dumps({
            "error": "YouTube API keyが設定されていません。環境変数YOUTUBE_API_KEYを設定してください。"
        }, ensure_ascii=False, indent=2)

    try:
        analyzer = YouTubeAnalyzer(api_key)
        analysis = analyzer.get_detailed_video_analysis(video_id)

        return json.dumps(analysis, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"動画分析エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)


def get_youtube_trending_analysis(region_code: str = 'JP', category_id: str = '0') -> str:
    """
    YouTube急上昇動画を取得・分析
    
    Args:
        region_code: 地域コード（デフォルト: JP）
        category_id: カテゴリID（デフォルト: 0=全カテゴリ）
    
    Returns:
        急上昇動画の分析結果の JSON文字列
    """
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        return json.dumps({
            "error": "YouTube API keyが設定されていません。環境変数YOUTUBE_API_KEYを設定してください。"
        }, ensure_ascii=False, indent=2)

    try:
        analyzer = YouTubeAnalyzer(api_key)

        # 急上昇動画を取得
        trending_response = analyzer.youtube.videos().list(
            part='snippet,statistics,contentDetails',
            chart='mostPopular',
            regionCode=region_code,
            categoryId=category_id if category_id != '0' else None,
            maxResults=20
        ).execute()

        # データを整形
        videos_data = []
        for item in trending_response['items']:
            videos_data.append({
                'id': item['id'],
                'title': item['snippet']['title'],
                'channel': item['snippet']['channelTitle'],
                'published_at': item['snippet']['publishedAt'],
                'description': item['snippet']['description'][:200] + '...' if len(item['snippet']['description']) > 200 else item['snippet']['description'],
                'view_count': int(item['statistics'].get('viewCount', 0)),
                'like_count': int(item['statistics'].get('likeCount', 0)),
                'comment_count': int(item['statistics'].get('commentCount', 0)),
                'duration': item['contentDetails']['duration'],
                'engagement_rate': analyzer._calculate_engagement_rate(item['statistics'])
            })

        # 分析実行
        analysis = analyzer.analyze_video_popularity(videos_data)

        result = {
            "地域": region_code,
            "カテゴリ": category_id,
            "急上昇動画": videos_data,
            "トレンド分析": analysis
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"急上昇動画分析エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)
