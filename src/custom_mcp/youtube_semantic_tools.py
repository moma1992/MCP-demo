"""
YouTube セマンティック分析 MCP ツール
Gemini APIを使用したトランスクリプト分析とチャプター生成
"""

import os
from typing import Any

from fastmcp import FastMCP

from .gemini_analyzer import GeminiTranscriptAnalyzer


def create_youtube_semantic_tools(mcp: FastMCP):
    """YouTube セマンティック分析関連のMCPツールを作成"""

    @mcp.tool
    def analyze_video_transcript_semantic(
        video_id: str,
        segment_duration: int = 300,
        granularity: str = "medium",
        custom_prompt: str | None = None,
        api_key: str | None = None
    ) -> dict[str, Any]:
        """
        YouTube動画のトランスクリプトをGemini APIでセマンティック分析し、意味のあるチャプターを生成
        
        Args:
            video_id: YouTube動画ID
            segment_duration: 分析セグメントの長さ（秒）デフォルト5分
            granularity: 粒度レベル ("fine", "medium", "coarse", "custom")
                - fine: 詳細な分割（多くのチャプター）
                - medium: 標準的な分割
                - coarse: 大まかな分割（少ないチャプター）
                - custom: カスタムプロンプト使用
            custom_prompt: カスタム分析指示（例: "教育的な観点から分析して" など）
            api_key: Gemini API key（省略時は環境変数GEMINI_API_KEYを使用）
            
        Returns:
            セマンティック分析されたチャプター情報
        """
        try:
            analyzer = GeminiTranscriptAnalyzer(api_key)
            result = analyzer.generate_semantic_chapters(
                video_id, segment_duration, granularity, custom_prompt
            )

            return {
                "success": True,
                "video_id": video_id,
                "analysis": result,
                "message": f"{result['total_chapters']}個のセマンティックチャプターを生成しました"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"セマンティック分析に失敗しました: {e}"
            }

    @mcp.tool
    def generate_youtube_description_with_chapters(
        video_id: str,
        segment_duration: int = 300,
        granularity: str = "medium",
        custom_prompt: str | None = None,
        api_key: str | None = None
    ) -> dict[str, Any]:
        """
        YouTube動画のセマンティック分析を行い、説明欄用の目次を生成
        
        Args:
            video_id: YouTube動画ID
            segment_duration: 分析セグメントの長さ（秒）
            granularity: 粒度レベル ("fine", "medium", "coarse", "custom")
            custom_prompt: カスタム分析指示
            api_key: Gemini API key
            
        Returns:
            YouTube説明欄用のフォーマットされたテキスト
        """
        try:
            analyzer = GeminiTranscriptAnalyzer(api_key)
            chapters_data = analyzer.generate_semantic_chapters(
                video_id, segment_duration, granularity, custom_prompt
            )
            description_text = analyzer.format_for_youtube_description(chapters_data)

            return {
                "success": True,
                "video_id": video_id,
                "description_text": description_text,
                "chapters_count": chapters_data['total_chapters'],
                "duration": chapters_data['total_duration_formatted'],
                "message": "YouTube説明欄用の目次を生成しました"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"説明欄生成に失敗しました: {e}"
            }

    @mcp.tool
    def extract_video_key_topics(
        video_id: str,
        api_key: str | None = None
    ) -> dict[str, Any]:
        """
        動画の主要トピックとキーポイントを抽出
        
        Args:
            video_id: YouTube動画ID
            api_key: Gemini API key
            
        Returns:
            抽出された主要トピックとキーポイント
        """
        try:
            analyzer = GeminiTranscriptAnalyzer(api_key)
            chapters_data = analyzer.generate_semantic_chapters(video_id, segment_duration=600)  # 10分セグメント

            # トピック分析
            topics = {}
            all_key_points = []
            tech_levels = set()

            for chapter in chapters_data['chapters']:
                category = chapter['topic_category']
                if category not in topics:
                    topics[category] = []

                topics[category].append({
                    "title": chapter['title'],
                    "summary": chapter['summary'],
                    "timestamp": chapter['start_timestamp'],
                    "key_points": chapter['key_points']
                })

                all_key_points.extend(chapter['key_points'])
                tech_levels.add(chapter['technical_level'])

            # 重要キーワードの頻度分析
            keyword_count = {}
            for point in all_key_points:
                if point in keyword_count:
                    keyword_count[point] += 1
                else:
                    keyword_count[point] = 1

            # 頻度順でソート
            top_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:10]

            return {
                "success": True,
                "video_id": video_id,
                "duration": chapters_data['total_duration_formatted'],
                "topics_by_category": topics,
                "top_keywords": [{"keyword": k, "frequency": v} for k, v in top_keywords],
                "technical_levels": list(tech_levels),
                "total_chapters": len(chapters_data['chapters']),
                "message": "主要トピックとキーポイントを抽出しました"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"トピック抽出に失敗しました: {e}"
            }

    @mcp.tool
    def generate_chapter_timestamps_only(
        video_id: str,
        segment_duration: int = 300,
        granularity: str = "medium",
        custom_prompt: str | None = None,
        api_key: str | None = None
    ) -> dict[str, Any]:
        """
        YouTubeチャプター機能用のタイムスタンプとタイトルのみを生成
        
        Args:
            video_id: YouTube動画ID
            segment_duration: セグメント長（秒）
            granularity: 粒度レベル ("fine", "medium", "coarse", "custom")
            custom_prompt: カスタム分析指示
            api_key: Gemini API key
            
        Returns:
            YouTube投稿に直接貼り付け可能なチャプターリスト
        """
        try:
            analyzer = GeminiTranscriptAnalyzer(api_key)
            chapters_data = analyzer.generate_semantic_chapters(
                video_id, segment_duration, granularity, custom_prompt
            )

            # シンプルなチャプターリスト生成
            chapter_lines = []
            for chapter in chapters_data['chapters']:
                chapter_lines.append(f"{chapter['start_timestamp']} {chapter['title']}")

            chapter_text = "\n".join(chapter_lines)

            return {
                "success": True,
                "video_id": video_id,
                "chapter_timestamps": chapter_text,
                "chapters": [
                    {
                        "timestamp": ch['start_timestamp'],
                        "title": ch['title'],
                        "category": ch['topic_category']
                    }
                    for ch in chapters_data['chapters']
                ],
                "total_chapters": len(chapters_data['chapters']),
                "message": "YouTubeチャプター用タイムスタンプを生成しました"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"チャプター生成に失敗しました: {e}"
            }

    @mcp.tool
    def batch_analyze_channel_videos(
        video_ids: list[str],
        api_key: str | None = None
    ) -> dict[str, Any]:
        """
        複数の動画を一括でセマンティック分析
        
        Args:
            video_ids: YouTube動画IDのリスト
            api_key: Gemini API key
            
        Returns:
            各動画の分析結果
        """
        try:
            analyzer = GeminiTranscriptAnalyzer(api_key)
            results = {}

            for video_id in video_ids:
                try:
                    chapters_data = analyzer.generate_semantic_chapters(video_id, segment_duration=300)

                    results[video_id] = {
                        "success": True,
                        "duration": chapters_data['total_duration_formatted'],
                        "chapters_count": chapters_data['total_chapters'],
                        "topics": list(set(ch['topic_category'] for ch in chapters_data['chapters'])),
                        "tech_levels": list(set(ch['technical_level'] for ch in chapters_data['chapters']))
                    }

                except Exception as e:
                    results[video_id] = {
                        "success": False,
                        "error": str(e)
                    }

            successful_analyses = sum(1 for r in results.values() if r['success'])

            return {
                "success": True,
                "total_videos": len(video_ids),
                "successful_analyses": successful_analyses,
                "results": results,
                "message": f"{successful_analyses}/{len(video_ids)}個の動画を分析しました"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"一括分析に失敗しました: {e}"
            }

    @mcp.tool
    def check_gemini_api_status(api_key: str | None = None) -> dict[str, Any]:
        """
        Gemini APIの接続状態を確認
        
        Args:
            api_key: Gemini API key
            
        Returns:
            API接続状態
        """
        try:
            if api_key:
                test_key = api_key
            else:
                test_key = os.getenv('GEMINI_API_KEY')

            if not test_key:
                return {
                    "success": False,
                    "error": "API key not found",
                    "message": "GEMINI_API_KEY環境変数が設定されていません"
                }

            # 簡単なテストリクエスト
            import google.generativeai as genai
            genai.configure(api_key=test_key)
            model = genai.GenerativeModel('gemini-1.5-pro')

            # テスト用の簡単なリクエスト
            response = model.generate_content("こんにちは、これはAPIテストです。")

            return {
                "success": True,
                "api_key_status": "valid",
                "model": "gemini-1.5-pro",
                "test_response": response.text[:100] + "..." if len(response.text) > 100 else response.text,
                "message": "Gemini APIが正常に動作しています"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Gemini API接続エラー: {e}"
            }

    # ツールは @mcp.tool デコレーターにより自動的にサーバーに登録されます
