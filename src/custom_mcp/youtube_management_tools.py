"""
YouTube管理画面操作のMCPツール
動画メタデータの自動更新とコンテンツ最適化
"""

from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from .youtube_content_generator import YouTubeContentGenerator


def create_youtube_management_tools(mcp: FastMCP):
    """YouTube管理・最適化関連のMCPツールを作成"""
    
    @mcp.tool
    def generate_video_content_automatically(
        video_id: str,
        include_chapters: bool = True,
        include_summary: bool = True,
        include_hashtags: bool = True,
        tone: str = "professional",
        custom_sections: Optional[List[str]] = None,
        gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        動画の説明文、ハッシュタグ、タイトル候補を自動生成
        
        Args:
            video_id: YouTube動画ID
            include_chapters: セマンティックチャプターを含めるか
            include_summary: 動画要約を含めるか
            include_hashtags: ハッシュタグを含めるか
            tone: 文体（professional, casual, educational, marketing）
            custom_sections: カスタムセクション（例: ["関連リンク", "使用ツール"]）
            gemini_api_key: Gemini API key
            
        Returns:
            生成されたコンテンツ情報
        """
        try:
            generator = YouTubeContentGenerator(gemini_api_key)
            
            result = generator.generate_video_description(
                video_id=video_id,
                include_chapters=include_chapters,
                include_summary=include_summary,
                include_hashtags=include_hashtags,
                custom_sections=custom_sections,
                tone=tone
            )
            
            # 結果に追加情報を含める
            if result['success']:
                result.update({
                    "character_count": len(result['description']),
                    "hashtag_count": len(result['hashtags']),
                    "title_options": len(result['title_suggestions']),
                    "message": "動画コンテンツを自動生成しました"
                })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"コンテンツ生成に失敗: {e}"
            }
    
    @mcp.tool
    def generate_seo_optimized_tags(
        video_id: str,
        max_tags: int = 30,
        include_trending: bool = True,
        gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        SEO最適化されたタグを生成
        
        Args:
            video_id: YouTube動画ID
            max_tags: 最大タグ数（1-500）
            include_trending: トレンドキーワードを含めるか
            gemini_api_key: Gemini API key
            
        Returns:
            最適化されたタグリストと分析情報
        """
        try:
            generator = YouTubeContentGenerator(gemini_api_key)
            
            tags = generator.generate_optimized_tags(
                video_id=video_id,
                max_tags=max_tags,
                include_trending=include_trending
            )
            
            # タグ分析
            japanese_tags = [tag for tag in tags if any('\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' for char in tag)]
            english_tags = [tag for tag in tags if tag not in japanese_tags]
            
            return {
                "success": True,
                "video_id": video_id,
                "tags": tags,
                "total_count": len(tags),
                "japanese_tags": japanese_tags,
                "english_tags": english_tags,
                "analysis": {
                    "japanese_ratio": len(japanese_tags) / len(tags) * 100 if tags else 0,
                    "average_length": sum(len(tag) for tag in tags) / len(tags) if tags else 0
                },
                "message": f"{len(tags)}個のSEO最適化タグを生成しました"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"タグ生成に失敗: {e}"
            }
    
    @mcp.tool
    def update_youtube_video_metadata(
        video_id: str,
        update_title: bool = False,
        update_description: bool = True,
        update_tags: bool = True,
        title_index: int = 0,
        dry_run: bool = False,
        gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        AIが生成したコンテンツでYouTube動画のメタデータを更新
        
        Args:
            video_id: YouTube動画ID
            update_title: タイトルを更新するか
            update_description: 説明文を更新するか
            update_tags: タグを更新するか
            title_index: 使用するタイトル候補のインデックス（0-2）
            dry_run: プレビューのみ（実際には更新しない）
            gemini_api_key: Gemini API key
            
        Returns:
            更新結果または更新プレビュー
        """
        try:
            generator = YouTubeContentGenerator(gemini_api_key)
            
            result = generator.update_video_metadata_with_generated_content(
                video_id=video_id,
                update_title=update_title,
                update_description=update_description,
                update_tags=update_tags,
                title_index=title_index,
                dry_run=dry_run
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"メタデータ更新に失敗: {e}"
            }
    
    @mcp.tool
    def generate_social_media_content(
        video_id: str,
        platforms: List[str] = ["twitter", "facebook", "linkedin"],
        gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        各SNSプラットフォーム用の投稿文を生成
        
        Args:
            video_id: YouTube動画ID
            platforms: 対象プラットフォーム（twitter, facebook, linkedin, instagram）
            gemini_api_key: Gemini API key
            
        Returns:
            プラットフォーム別投稿文
        """
        try:
            generator = YouTubeContentGenerator(gemini_api_key)
            
            posts = generator.generate_social_media_posts(
                video_id=video_id,
                platforms=platforms
            )
            
            return {
                "success": True,
                "video_id": video_id,
                "posts": posts,
                "platforms": platforms,
                "message": f"{len(posts)}個のプラットフォーム用投稿文を生成しました"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"SNS投稿文生成に失敗: {e}"
            }
    
    @mcp.tool
    def analyze_video_content_for_optimization(
        video_id: str,
        gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        動画コンテンツを分析してSEO・エンゲージメント最適化の提案を生成
        
        Args:
            video_id: YouTube動画ID
            gemini_api_key: Gemini API key
            
        Returns:
            最適化提案と分析結果
        """
        try:
            generator = YouTubeContentGenerator(gemini_api_key)
            
            # コンテンツ分析
            content_result = generator.generate_video_description(video_id)
            if not content_result['success']:
                return content_result
            
            content_data = content_result['content_data']
            
            # 最適化分析
            optimization_suggestions = {
                "title_optimization": {
                    "suggestions": content_result['title_suggestions'],
                    "current_length": "（現在のタイトル長を確認してください）",
                    "recommendation": "60文字以内で検索キーワードを含める"
                },
                "description_optimization": {
                    "length": len(content_result['description']),
                    "recommended_length": "最初の125文字が重要（検索結果プレビュー）",
                    "has_chapters": "チャプター機能でユーザビリティ向上",
                    "call_to_action": content_data.get('call_to_action', '')
                },
                "hashtag_optimization": {
                    "count": len(content_result['hashtags']),
                    "recommended_count": "10-15個が最適",
                    "trending_analysis": "トレンドキーワードを含む",
                    "hashtags": content_result['hashtags']
                },
                "seo_analysis": {
                    "keywords": content_data.get('seo_keywords', []),
                    "target_audience": content_data.get('target_audience', ''),
                    "related_topics": content_data.get('related_topics', [])
                },
                "engagement_tips": [
                    "動画の最初の15秒で視聴者の興味を引く",
                    "チャプター機能で長い動画の視聴維持率を向上",
                    "終了画面で関連動画や登録を促す",
                    "コメント欄での視聴者との交流を促進"
                ]
            }
            
            return {
                "success": True,
                "video_id": video_id,
                "content_analysis": content_data,
                "optimization_suggestions": optimization_suggestions,
                "message": "動画コンテンツの最適化分析が完了しました"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"最適化分析に失敗: {e}"
            }
    
    @mcp.tool
    def batch_update_channel_videos(
        channel_video_ids: List[str],
        update_descriptions: bool = True,
        update_tags: bool = True,
        dry_run: bool = True,
        gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        チャンネルの複数動画を一括で最適化
        
        Args:
            channel_video_ids: 更新対象の動画IDリスト
            update_descriptions: 説明文を更新するか
            update_tags: タグを更新するか  
            dry_run: プレビューのみ（実際には更新しない）
            gemini_api_key: Gemini API key
            
        Returns:
            一括更新結果
        """
        try:
            generator = YouTubeContentGenerator(gemini_api_key)
            results = {}
            successful_updates = 0
            
            for video_id in channel_video_ids:
                try:
                    result = generator.update_video_metadata_with_generated_content(
                        video_id=video_id,
                        update_title=False,  # 一括更新ではタイトルは更新しない
                        update_description=update_descriptions,
                        update_tags=update_tags,
                        dry_run=dry_run
                    )
                    
                    results[video_id] = result
                    if result['success']:
                        successful_updates += 1
                        
                except Exception as e:
                    results[video_id] = {
                        "success": False,
                        "error": str(e)
                    }
            
            return {
                "success": True,
                "total_videos": len(channel_video_ids),
                "successful_updates": successful_updates,
                "failed_updates": len(channel_video_ids) - successful_updates,
                "dry_run": dry_run,
                "detailed_results": results,
                "message": f"{successful_updates}/{len(channel_video_ids)}個の動画を{'プレビュー' if dry_run else '更新'}しました"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"一括更新に失敗: {e}"
            }
    
    @mcp.tool
    def generate_youtube_thumbnail_suggestions(
        video_id: str,
        gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        動画内容に基づいてサムネイル提案を生成
        
        Args:
            video_id: YouTube動画ID
            gemini_api_key: Gemini API key
            
        Returns:
            サムネイル提案とデザインガイド
        """
        try:
            generator = YouTubeContentGenerator(gemini_api_key)
            
            # コンテンツ分析
            content_result = generator.generate_video_description(video_id)
            if not content_result['success']:
                return content_result
            
            content_data = content_result['content_data']
            
            # サムネイル提案
            thumbnail_suggestions = {
                "design_concepts": [
                    {
                        "concept": "技術解説型",
                        "description": "コードやツールのスクリーンショットを背景に、説明文をオーバーレイ",
                        "colors": ["青", "白", "グレー"],
                        "text_suggestions": content_data['key_points'][:2]
                    },
                    {
                        "concept": "人物中心型", 
                        "description": "講師や話者を中心に配置し、興味を引くタイトルテキスト",
                        "colors": ["暖色系", "コントラスト強"],
                        "text_suggestions": ["これ知ってる？", "必見！"]
                    },
                    {
                        "concept": "Before/After型",
                        "description": "変化や結果を視覚的に表現",
                        "colors": ["緑", "赤", "対比色"],
                        "text_suggestions": ["改善前→改善後", "旧→新"]
                    }
                ],
                "text_recommendations": {
                    "main_title": content_data['short_description'][:20],
                    "subtitle_options": content_data['key_points'][:3],
                    "keywords_for_text": content_data.get('seo_keywords', [])[:5]
                },
                "visual_elements": {
                    "recommended_colors": ["#FF4444", "#4444FF", "#44FF44"],
                    "font_suggestions": ["太字", "読みやすいサンフォント"],
                    "layout_tips": [
                        "左上または右上にメインテキスト",
                        "人物は左右どちらかに配置",
                        "背景は動画内容を表現する画像"
                    ]
                },
                "ab_testing_variations": [
                    "テキストありバージョン",
                    "テキストなしバージョン", 
                    "人物ありバージョン",
                    "人物なしバージョン"
                ]
            }
            
            return {
                "success": True,
                "video_id": video_id,
                "thumbnail_suggestions": thumbnail_suggestions,
                "content_context": {
                    "target_audience": content_data.get('target_audience'),
                    "main_topics": content_data.get('key_points', [])[:3]
                },
                "message": "サムネイル提案を生成しました"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"サムネイル提案生成に失敗: {e}"
            }
    
    # ツールは @mcp.tool デコレーターにより自動的にサーバーに登録されます