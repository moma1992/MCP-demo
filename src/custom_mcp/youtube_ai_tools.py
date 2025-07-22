#!/usr/bin/env python3
"""
YouTube AI Tools for MCP Server
AIを活用したタイトル生成、企画提案、コンテンツ分析機能
"""

import json
import random
import re
from datetime import datetime, timedelta
from typing import Any

from .youtube_analytics_tools import YouTubeAnalyticsManager
from .youtube_channel_tools import YouTubeChannelManager


class YouTubeAIAssistant:
    """YouTube向けAI支援クラス"""

    def __init__(self):
        """Initialize AI assistant"""
        self.channel_manager = YouTubeChannelManager()
        self.analytics_manager = YouTubeAnalyticsManager()

    def generate_optimized_titles(self, video_id: str,
                                target_audience: str | None = None) -> list[dict[str, Any]]:
        """
        AIベースの最適化されたタイトルを生成
        
        Args:
            video_id: 動画ID
            target_audience: ターゲット層（若年層、ビジネス、主婦層など）
            
        Returns:
            最適化されたタイトル候補リスト
        """
        try:
            # 動画情報を取得
            videos = self.channel_manager.list_my_videos(max_results=50)
            target_video = None

            for video in videos['videos']:
                if video['video_id'] == video_id:
                    target_video = video
                    break

            if not target_video:
                raise Exception(f"動画が見つかりません: {video_id}")

            # 過去30日のパフォーマンスデータを取得
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)

            analytics = self.analytics_manager.get_video_analytics(
                video_id,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            # トップパフォーマンス動画を分析
            top_videos = self._get_top_performing_videos()

            # タイトル生成
            suggestions = self._generate_title_suggestions(
                target_video,
                analytics,
                top_videos,
                target_audience
            )

            return suggestions

        except Exception as e:
            raise Exception(f"タイトル生成エラー: {str(e)}")

    def suggest_next_content(self, category: str | None = None) -> list[dict[str, Any]]:
        """
        次の動画企画を提案
        
        Args:
            category: カテゴリ（ゲーム、教育、エンタメなど）
            
        Returns:
            企画提案リスト
        """
        try:
            # チャンネル分析データを取得
            channel_analytics = self._get_channel_performance_summary()

            # トレンド分析
            trending_topics = self._analyze_current_trends(category)

            # 成功パターン分析
            success_patterns = self._analyze_channel_success_patterns()

            # 視聴者の興味分析
            audience_interests = self._analyze_audience_interests()

            # 企画提案を生成
            suggestions = self._generate_content_suggestions(
                channel_analytics,
                trending_topics,
                success_patterns,
                audience_interests,
                category
            )

            return suggestions

        except Exception as e:
            raise Exception(f"企画提案エラー: {str(e)}")

    def analyze_success_patterns(self) -> dict[str, Any]:
        """
        チャンネルの成功パターンを分析
        
        Returns:
            成功パターン分析結果
        """
        try:
            # 過去90日のトップ動画を分析
            videos = self.channel_manager.list_my_videos(max_results=50)

            # パフォーマンスでソート
            sorted_videos = sorted(
                videos['videos'],
                key=lambda x: x['statistics']['view_count'],
                reverse=True
            )

            # トップ20%を成功動画として分析
            top_count = max(1, len(sorted_videos) // 5)
            top_videos = sorted_videos[:top_count]

            # パターン分析
            patterns = {
                'title_patterns': self._analyze_title_patterns(top_videos),
                'optimal_length': self._analyze_video_length_patterns(top_videos),
                'best_publishing_time': self._analyze_publishing_patterns(top_videos),
                'tag_patterns': self._analyze_tag_patterns(top_videos),
                'engagement_factors': self._analyze_engagement_patterns(top_videos),
                'content_themes': self._extract_content_themes(top_videos)
            }

            # 推奨事項を生成
            recommendations = self._generate_success_recommendations(patterns)

            return {
                'analysis_period': '過去90日',
                'videos_analyzed': len(sorted_videos),
                'top_performers_count': top_count,
                'success_patterns': patterns,
                'recommendations': recommendations
            }

        except Exception as e:
            raise Exception(f"成功パターン分析エラー: {str(e)}")

    def optimize_posting_schedule(self) -> dict[str, Any]:
        """
        最適な投稿スケジュールを提案
        
        Returns:
            投稿スケジュール提案
        """
        try:
            # 過去の投稿パフォーマンスを分析
            videos = self.channel_manager.list_my_videos(max_results=100)

            # 視聴者のアクティブ時間を分析
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=90)

            audience_insights = self.analytics_manager.analyze_audience_insights(
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )

            # 最適なスケジュールを計算
            optimal_schedule = self._calculate_optimal_schedule(
                videos['videos'],
                audience_insights
            )

            # 具体的な投稿計画を生成
            posting_plan = self._generate_posting_plan(optimal_schedule)

            return {
                'optimal_schedule': optimal_schedule,
                'posting_plan': posting_plan,
                'expected_impact': self._estimate_schedule_impact(optimal_schedule)
            }

        except Exception as e:
            raise Exception(f"投稿スケジュール最適化エラー: {str(e)}")

    def _generate_title_suggestions(self, video: dict, analytics: dict,
                                  top_videos: list[dict], target_audience: str | None) -> list[dict]:
        """タイトル候補を生成"""
        suggestions = []
        current_title = video['title']
        base_title = re.sub(r'【.*?】', '', current_title).strip()

        # パフォーマンスベースの提案
        view_count = video['statistics']['view_count']

        # 1. 数字を使った具体的なタイトル
        if view_count > 10000:
            suggestions.append({
                'title': f'【{view_count//1000}万回再生】{base_title}の真実',
                'strategy': '社会的証明を活用',
                'expected_ctr_boost': '+15-20%'
            })

        # 2. 感情に訴えるタイトル
        emotional_triggers = ['衝撃', '感動', '爆笑', '神回', '奇跡']
        trigger = random.choice(emotional_triggers)
        suggestions.append({
            'title': f'{base_title}で{trigger}の展開に...',
            'strategy': '感情的フック',
            'expected_ctr_boost': '+10-15%'
        })

        # 3. 質問形式のタイトル
        suggestions.append({
            'title': f'なぜ{base_title}が話題なのか？その理由がヤバすぎた',
            'strategy': '好奇心を刺激',
            'expected_ctr_boost': '+12-18%'
        })

        # 4. リスト形式のタイトル
        suggestions.append({
            'title': f'{base_title}で分かった5つの重要ポイント',
            'strategy': 'リスト形式で整理',
            'expected_ctr_boost': '+8-12%'
        })

        # 5. ターゲット層別の提案
        if target_audience:
            audience_titles = {
                '若年層': f'【Z世代必見】{base_title}がエモすぎる件',
                'ビジネス': f'{base_title}｜成功者が実践する3つの法則',
                '主婦層': f'【保存版】{base_title}で家事が楽になる方法',
                'シニア': f'【分かりやすく解説】{base_title}の基本と応用'
            }

            if target_audience in audience_titles:
                suggestions.append({
                    'title': audience_titles[target_audience],
                    'strategy': f'{target_audience}向けに最適化',
                    'expected_ctr_boost': '+20-25%'
                })

        # 6. トレンドを活用したタイトル
        year = datetime.now().year
        month = datetime.now().month
        season = self._get_current_season()

        suggestions.append({
            'title': f'【{year}年{month}月最新】{base_title}完全ガイド',
            'strategy': '最新性をアピール',
            'expected_ctr_boost': '+10-15%'
        })

        # CTR予測スコアでソート
        for suggestion in suggestions:
            suggestion['score'] = self._calculate_title_score(suggestion['title'], top_videos)

        suggestions.sort(key=lambda x: x['score'], reverse=True)

        return suggestions[:5]

    def _get_top_performing_videos(self) -> list[dict]:
        """トップパフォーマンス動画を取得"""
        videos = self.channel_manager.list_my_videos(max_results=50)
        sorted_videos = sorted(
            videos['videos'],
            key=lambda x: x['statistics']['view_count'],
            reverse=True
        )
        return sorted_videos[:10]

    def _calculate_title_score(self, title: str, top_videos: list[dict]) -> float:
        """タイトルのスコアを計算"""
        score = 0

        # 文字数スコア（40-60文字が最適）
        length = len(title)
        if 40 <= length <= 60:
            score += 20
        elif 30 <= length <= 70:
            score += 10

        # キーワードスコア
        power_words = ['必見', '最新', '完全', '保存版', '神', '最強', '究極']
        for word in power_words:
            if word in title:
                score += 5

        # 数字の使用
        if any(char.isdigit() for char in title):
            score += 10

        # 括弧の使用
        if '【' in title and '】' in title:
            score += 5

        # 感嘆符の使用
        if '!' in title or '！' in title:
            score += 3

        # 疑問符の使用
        if '?' in title or '？' in title:
            score += 5

        return score

    def _get_channel_performance_summary(self) -> dict[str, Any]:
        """チャンネルパフォーマンスのサマリーを取得"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        return self.analytics_manager.get_channel_analytics(
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

    def _analyze_current_trends(self, category: str | None) -> list[dict]:
        """現在のトレンドを分析"""
        # 実際のトレンド分析の代わりにサンプルデータを返す
        trends = [
            {'topic': 'AI活用術', 'growth_rate': 45, 'competition': 'medium'},
            {'topic': 'ショート動画', 'growth_rate': 80, 'competition': 'high'},
            {'topic': 'ライブ配信', 'growth_rate': 35, 'competition': 'low'},
            {'topic': 'コラボ企画', 'growth_rate': 25, 'competition': 'medium'},
            {'topic': 'How-to動画', 'growth_rate': 20, 'competition': 'high'}
        ]

        if category:
            # カテゴリに応じてフィルタリング
            category_trends = {
                'ゲーム': ['新作ゲーム実況', 'ゲーム攻略', 'e-sports'],
                '教育': ['プログラミング', '語学学習', '資格試験'],
                'エンタメ': ['ドッキリ', 'チャレンジ企画', 'Vlog']
            }

            if category in category_trends:
                for topic in category_trends[category]:
                    trends.append({
                        'topic': topic,
                        'growth_rate': random.randint(20, 60),
                        'competition': random.choice(['low', 'medium', 'high'])
                    })

        return sorted(trends, key=lambda x: x['growth_rate'], reverse=True)[:5]

    def _analyze_channel_success_patterns(self) -> dict[str, Any]:
        """チャンネルの成功パターンを分析"""
        videos = self.channel_manager.list_my_videos(max_results=50)
        top_videos = sorted(
            videos['videos'],
            key=lambda x: x['statistics']['view_count'],
            reverse=True
        )[:10]

        patterns = {
            'average_video_length': sum(self._parse_duration_to_seconds(v['duration']) for v in top_videos) / len(top_videos),
            'common_tags': self._extract_common_tags(top_videos),
            'publishing_frequency': self._analyze_publishing_frequency(top_videos),
            'engagement_rate': sum(
                (v['statistics']['like_count'] + v['statistics']['comment_count']) / v['statistics']['view_count']
                for v in top_videos if v['statistics']['view_count'] > 0
            ) / len(top_videos) * 100
        }

        return patterns

    def _analyze_audience_interests(self) -> list[str]:
        """視聴者の興味を分析"""
        # 実際の実装では視聴者のコメントや視聴履歴から分析
        return [
            '実用的なテクニック',
            '最新情報',
            'エンターテインメント',
            '学習コンテンツ',
            'レビュー・比較'
        ]

    def _generate_content_suggestions(self, channel_analytics: dict,
                                    trending_topics: list[dict],
                                    success_patterns: dict,
                                    audience_interests: list[str],
                                    category: str | None) -> list[dict]:
        """コンテンツ提案を生成"""
        suggestions = []

        # トレンドベースの提案
        for trend in trending_topics[:3]:
            suggestions.append({
                'title': f"{trend['topic']}について徹底解説",
                'description': f"現在急成長中の{trend['topic']}をテーマにした動画",
                'expected_views': self._estimate_views(trend['growth_rate']),
                'difficulty': trend['competition'],
                'priority': 'high' if trend['growth_rate'] > 50 else 'medium',
                'content_outline': [
                    f'{trend["topic"]}の基本',
                    '最新トレンドの紹介',
                    '実践的なテクニック',
                    '視聴者Q&A'
                ]
            })

        # 成功パターンベースの提案
        if success_patterns['average_video_length'] > 600:  # 10分以上
            suggestions.append({
                'title': '完全保存版！長編解説動画',
                'description': '人気の長編フォーマットを活用した詳細解説',
                'expected_views': 50000,
                'difficulty': 'medium',
                'priority': 'high',
                'content_outline': [
                    '導入（フック）',
                    'メインコンテンツ（3部構成）',
                    '実例・デモンストレーション',
                    'まとめとCTA'
                ]
            })

        # 視聴者興味ベースの提案
        for interest in audience_interests[:2]:
            suggestions.append({
                'title': f'視聴者リクエスト企画：{interest}',
                'description': f'コメントで要望の多い{interest}に応える動画',
                'expected_views': 30000,
                'difficulty': 'low',
                'priority': 'medium',
                'content_outline': [
                    '視聴者の疑問に回答',
                    f'{interest}の実演',
                    'よくある間違いと対策',
                    '次回予告'
                ]
            })

        # シリーズ物の提案
        suggestions.append({
            'title': '新シリーズ：週刊アップデート',
            'description': '毎週の最新情報をまとめて紹介する定期コンテンツ',
            'expected_views': 25000,
            'difficulty': 'low',
            'priority': 'high',
            'content_outline': [
                '今週のハイライト',
                '注目のニュース3選',
                '来週の予定',
                '視聴者からの情報募集'
            ]
        })

        return suggestions

    def _analyze_title_patterns(self, videos: list[dict]) -> dict[str, Any]:
        """タイトルパターンを分析"""
        patterns = {
            'average_length': sum(len(v['title']) for v in videos) / len(videos),
            'use_brackets': sum(1 for v in videos if '【' in v['title']) / len(videos) * 100,
            'use_numbers': sum(1 for v in videos if any(c.isdigit() for c in v['title'])) / len(videos) * 100,
            'common_words': self._extract_common_words([v['title'] for v in videos])
        }
        return patterns

    def _analyze_video_length_patterns(self, videos: list[dict]) -> dict[str, Any]:
        """動画の長さパターンを分析"""
        lengths = [self._parse_duration_to_seconds(v['duration']) for v in videos]

        return {
            'average_seconds': sum(lengths) / len(lengths),
            'optimal_range': f'{min(lengths)//60}-{max(lengths)//60}分',
            'most_common': f'{(sum(lengths) / len(lengths))//60}分前後'
        }

    def _analyze_publishing_patterns(self, videos: list[dict]) -> dict[str, Any]:
        """投稿パターンを分析"""
        publish_times = []

        for video in videos:
            try:
                publish_time = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                publish_times.append(publish_time)
            except:
                continue

        if not publish_times:
            return {'message': 'データ不足'}

        # 曜日別分析
        weekdays = [t.strftime('%A') for t in publish_times]
        most_common_day = max(set(weekdays), key=weekdays.count)

        # 時間帯分析
        hours = [t.hour for t in publish_times]
        most_common_hour = max(set(hours), key=hours.count)

        return {
            'best_day': most_common_day,
            'best_hour': f'{most_common_hour}時頃',
            'frequency': f'平均{len(videos)/3:.1f}本/月'
        }

    def _analyze_tag_patterns(self, videos: list[dict]) -> list[str]:
        """タグパターンを分析"""
        all_tags = []
        for video in videos:
            all_tags.extend(video.get('tags', []))

        # 頻出タグを抽出
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, count in sorted_tags[:10]]

    def _analyze_engagement_patterns(self, videos: list[dict]) -> dict[str, Any]:
        """エンゲージメントパターンを分析"""
        engagement_rates = []

        for video in videos:
            views = video['statistics']['view_count']
            if views > 0:
                likes = video['statistics']['like_count']
                comments = video['statistics']['comment_count']
                rate = (likes + comments) / views * 100
                engagement_rates.append(rate)

        if not engagement_rates:
            return {'average_rate': 0}

        return {
            'average_rate': sum(engagement_rates) / len(engagement_rates),
            'highest_rate': max(engagement_rates),
            'engagement_factors': self._identify_engagement_factors(videos)
        }

    def _identify_engagement_factors(self, videos: list[dict]) -> list[str]:
        """エンゲージメント要因を特定"""
        factors = []

        high_engagement = [v for v in videos if
                         v['statistics']['view_count'] > 0 and
                         (v['statistics']['like_count'] + v['statistics']['comment_count']) / v['statistics']['view_count'] > 0.05]

        if len(high_engagement) > len(videos) / 2:
            factors.append('視聴者との積極的な対話')

        # タイトルに質問が含まれる動画をチェック
        question_videos = [v for v in high_engagement if '?' in v['title'] or '？' in v['title']]
        if len(question_videos) > len(high_engagement) / 3:
            factors.append('質問形式のタイトル')

        return factors if factors else ['一貫した高品質コンテンツ']

    def _extract_content_themes(self, videos: list[dict]) -> list[str]:
        """コンテンツテーマを抽出"""
        # 実際の実装では自然言語処理を使用
        # ここでは簡易実装
        themes = []

        keywords = {
            'tutorial': ['方法', 'やり方', 'How to', 'チュートリアル'],
            'review': ['レビュー', '比較', '検証', 'おすすめ'],
            'entertainment': ['やってみた', 'チャレンジ', '実験', 'ドッキリ'],
            'news': ['最新', 'ニュース', '速報', '発表']
        }

        for theme, words in keywords.items():
            count = sum(1 for v in videos if any(word in v['title'] for word in words))
            if count > len(videos) / 4:
                themes.append(theme)

        return themes if themes else ['バラエティ']

    def _generate_success_recommendations(self, patterns: dict) -> list[str]:
        """成功パターンから推奨事項を生成"""
        recommendations = []

        # タイトルに関する推奨
        if patterns['title_patterns']['use_brackets'] > 70:
            recommendations.append('【】を使ったタイトル構成を継続')

        if patterns['title_patterns']['average_length'] > 50:
            recommendations.append('詳細なタイトルが効果的 - 50文字以上を維持')

        # 動画の長さに関する推奨
        avg_seconds = patterns['optimal_length']['average_seconds']
        if avg_seconds > 600:
            recommendations.append('10分以上の詳細コンテンツが人気')
        elif avg_seconds < 300:
            recommendations.append('5分以内の短い動画が効果的')

        # 投稿時間に関する推奨
        if patterns['best_publishing_time']['best_day']:
            recommendations.append(
                f"{patterns['best_publishing_time']['best_day']}の"
                f"{patterns['best_publishing_time']['best_hour']}投稿が最適"
            )

        # エンゲージメントに関する推奨
        if patterns['engagement_factors']['average_rate'] > 5:
            recommendations.append('高エンゲージメント維持 - 視聴者との対話を継続')

        return recommendations

    def _calculate_optimal_schedule(self, videos: list[dict],
                                  audience_insights: dict) -> dict[str, Any]:
        """最適なスケジュールを計算"""
        # 視聴者のアクティブ時間を考慮
        viewing_times = audience_insights.get('viewing_times', {})

        optimal_schedule = {
            'best_days': ['土曜日', '日曜日', '金曜日'],  # 週末重視
            'best_times': viewing_times.get('peak_hours', ['20:00-22:00', '12:00-13:00']),
            'recommended_frequency': self._calculate_optimal_frequency(videos),
            'content_mix': self._suggest_content_mix()
        }

        return optimal_schedule

    def _calculate_optimal_frequency(self, videos: list[dict]) -> str:
        """最適な投稿頻度を計算"""
        if not videos:
            return '週2-3本'

        # 過去の投稿頻度を分析
        publish_dates = []
        for video in videos:
            try:
                date = datetime.fromisoformat(video['published_at'].replace('Z', '+00:00'))
                publish_dates.append(date)
            except:
                continue

        if len(publish_dates) < 2:
            return '週2-3本'

        # 平均投稿間隔を計算
        intervals = []
        for i in range(1, len(publish_dates)):
            interval = (publish_dates[i-1] - publish_dates[i]).days
            if 0 < interval < 30:  # 異常値を除外
                intervals.append(interval)

        if not intervals:
            return '週2-3本'

        avg_interval = sum(intervals) / len(intervals)

        if avg_interval < 3:
            return '毎日または隔日'
        elif avg_interval < 5:
            return '週3-4本'
        elif avg_interval < 8:
            return '週2本'
        else:
            return '週1本'

    def _suggest_content_mix(self) -> dict[str, int]:
        """コンテンツミックスを提案"""
        return {
            'メインコンテンツ': 50,
            'トレンド対応': 20,
            'コラボ・企画物': 15,
            'Q&A・雑談': 10,
            'お知らせ・告知': 5
        }

    def _generate_posting_plan(self, optimal_schedule: dict) -> list[dict]:
        """具体的な投稿計画を生成"""
        plan = []

        # 次の2週間の計画を生成
        current_date = datetime.now()

        for i in range(14):
            date = current_date + timedelta(days=i)
            day_name = date.strftime('%A')

            if day_name in optimal_schedule['best_days']:
                time_slot = optimal_schedule['best_times'][0].split('-')[0]

                # コンテンツタイプを決定
                content_type = self._select_content_type(i, optimal_schedule['content_mix'])

                plan.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'day': day_name,
                    'time': time_slot,
                    'content_type': content_type,
                    'priority': 'high' if day_name in ['土曜日', '日曜日'] else 'medium'
                })

        return plan

    def _select_content_type(self, index: int, content_mix: dict[str, int]) -> str:
        """コンテンツタイプを選択"""
        types = []
        for content_type, percentage in content_mix.items():
            types.extend([content_type] * (percentage // 10))

        return types[index % len(types)] if types else 'メインコンテンツ'

    def _estimate_schedule_impact(self, optimal_schedule: dict) -> dict[str, str]:
        """スケジュール変更の影響を推定"""
        return {
            'expected_view_increase': '+15-25%',
            'expected_engagement_boost': '+10-15%',
            'subscriber_growth': '+5-10%/月',
            'consistency_score': '85/100'
        }

    def _parse_duration_to_seconds(self, duration: str) -> int:
        """ISO 8601形式の動画時間を秒に変換"""
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration)

        if not match:
            return 0

        hours, minutes, seconds = match.groups()
        total_seconds = 0

        if hours:
            total_seconds += int(hours) * 3600
        if minutes:
            total_seconds += int(minutes) * 60
        if seconds:
            total_seconds += int(seconds)

        return total_seconds

    def _extract_common_words(self, titles: list[str]) -> list[str]:
        """共通単語を抽出"""
        word_count = {}

        for title in titles:
            # 簡易的な単語分割
            words = re.findall(r'[ぁ-んァ-ヴー一-龠]+|[a-zA-Z]+', title)
            for word in words:
                if len(word) > 2:  # 3文字以上の単語のみ
                    word_count[word] = word_count.get(word, 0) + 1

        # 頻出上位5単語
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [word for word, count in sorted_words[:5]]

    def _get_current_season(self) -> str:
        """現在の季節を取得"""
        month = datetime.now().month

        if 3 <= month <= 5:
            return '春'
        elif 6 <= month <= 8:
            return '夏'
        elif 9 <= month <= 11:
            return '秋'
        else:
            return '冬'

    def _estimate_views(self, growth_rate: int) -> int:
        """予想視聴回数を推定"""
        base_views = 10000
        multiplier = 1 + (growth_rate / 100)
        return int(base_views * multiplier)


# MCP Tools Implementation
def generate_optimized_titles_tool(video_id: str, target_audience: str | None = None) -> str:
    """
    AIベースの最適化されたタイトルを生成
    
    Args:
        video_id: 動画ID
        target_audience: ターゲット層（若年層、ビジネス、主婦層、シニアなど）
        
    Returns:
        タイトル提案のJSON文字列
    """
    try:
        assistant = YouTubeAIAssistant()
        suggestions = assistant.generate_optimized_titles(video_id, target_audience)

        output = {
            'video_id': video_id,
            'target_audience': target_audience or '一般',
            'suggestions': suggestions,
            'recommendation': '最もスコアの高いタイトルを選択し、A/Bテストを実施することを推奨'
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"タイトル生成エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)


def suggest_next_content_tool(category: str | None = None) -> str:
    """
    次の動画企画を提案
    
    Args:
        category: カテゴリ（ゲーム、教育、エンタメなど）
        
    Returns:
        企画提案のJSON文字列
    """
    try:
        assistant = YouTubeAIAssistant()
        suggestions = assistant.suggest_next_content(category)

        output = {
            'category': category or '全般',
            'suggestions': suggestions,
            'implementation_tips': [
                'トレンドは変化が早いため、早期の実行を推奨',
                '視聴者のフィードバックを積極的に取り入れる',
                '最初は小規模でテストし、反応を見て拡大'
            ]
        }

        return json.dumps(output, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"企画提案エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)


def analyze_success_patterns_tool() -> str:
    """
    チャンネルの成功パターンを分析
    
    Returns:
        成功パターン分析のJSON文字列
    """
    try:
        assistant = YouTubeAIAssistant()
        analysis = assistant.analyze_success_patterns()

        return json.dumps(analysis, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"成功パターン分析エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)


def optimize_posting_schedule_tool() -> str:
    """
    最適な投稿スケジュールを提案
    
    Returns:
        投稿スケジュール提案のJSON文字列
    """
    try:
        assistant = YouTubeAIAssistant()
        schedule = assistant.optimize_posting_schedule()

        return json.dumps(schedule, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"スケジュール最適化エラー: {str(e)}"
        }, ensure_ascii=False, indent=2)
