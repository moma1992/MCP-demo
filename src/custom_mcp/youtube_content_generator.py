"""
YouTube動画の内容説明とハッシュタグ自動生成
Gemini APIを使用した高度なコンテンツ最適化
"""

import json
import re
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from .youtube_auth import YouTubeAuthManager
from .gemini_analyzer import GeminiTranscriptAnalyzer


class YouTubeContentGenerator:
    """YouTube動画コンテンツの自動生成クラス"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """初期化"""
        self.analyzer = GeminiTranscriptAnalyzer(gemini_api_key)
        self.auth_manager = YouTubeAuthManager()
        
    def generate_video_description(
        self,
        video_id: str,
        include_chapters: bool = True,
        include_summary: bool = True,
        include_hashtags: bool = True,
        custom_sections: Optional[List[str]] = None,
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        動画の説明文を自動生成
        
        Args:
            video_id: YouTube動画ID
            include_chapters: チャプターを含めるか
            include_summary: 要約を含めるか
            include_hashtags: ハッシュタグを含めるか
            custom_sections: カスタムセクション（例: ["関連リンク", "使用ツール"]）
            tone: トーン（professional, casual, educational, marketing）
            
        Returns:
            生成された説明文と関連情報
        """
        # トランスクリプト取得
        transcript = self.analyzer.get_transcript(video_id)
        
        # 全文テキスト作成
        full_text = " ".join([seg['text'] for seg in transcript])
        total_duration = transcript[-1]['start'] + transcript[-1]['duration']
        
        # Geminiプロンプト作成
        tone_instructions = {
            "professional": "プロフェッショナルで信頼性のある文体",
            "casual": "親しみやすくカジュアルな文体",
            "educational": "教育的で分かりやすい文体",
            "marketing": "魅力的でエンゲージメントを促す文体"
        }.get(tone, "プロフェッショナルな文体")
        
        prompt = f"""
以下のYouTube動画のトランスクリプトから、{tone_instructions}で動画説明文を生成してください。

トランスクリプト（最初の2000文字）:
{full_text[:2000]}...

動画時間: {self.analyzer.format_timestamp(total_duration)}

以下の形式でJSON形式で返してください：
{{
  "title_suggestions": ["改善されたタイトル案1", "タイトル案2", "タイトル案3"],
  "short_description": "動画の簡潔な説明（100文字以内）",
  "detailed_summary": "詳細な内容説明（300-500文字）",
  "key_points": ["重要ポイント1", "重要ポイント2", ...],
  "target_audience": "想定視聴者層",
  "learning_outcomes": ["この動画で学べること1", "学べること2", ...],
  "hashtags": ["#ハッシュタグ1", "#ハッシュタグ2", ...],
  "related_topics": ["関連トピック1", "関連トピック2", ...],
  "seo_keywords": ["SEOキーワード1", "キーワード2", ...],
  "call_to_action": "視聴者への行動喚起文",
  "timestamps_summary": "タイムスタンプ用の短い説明"
}}

ハッシュタグは以下の基準で生成：
- 動画の主要トピックを反映
- トレンドを考慮
- 日本語と英語を適切にミックス
- 最大15個まで
- 一般的すぎず、具体的すぎないバランス
"""
        
        try:
            response = self.analyzer.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # JSONパース
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                content_data = json.loads(json_match.group(0))
            else:
                content_data = json.loads(response_text)
            
            # 説明文の構築
            description_parts = []
            
            # 簡潔な説明
            if include_summary:
                description_parts.append(content_data['short_description'])
                description_parts.append("")
            
            # 詳細説明
            description_parts.append(content_data['detailed_summary'])
            description_parts.append("")
            
            # この動画で学べること
            if content_data.get('learning_outcomes'):
                description_parts.append("📚 この動画で学べること:")
                for outcome in content_data['learning_outcomes']:
                    description_parts.append(f"・{outcome}")
                description_parts.append("")
            
            # チャプター
            if include_chapters:
                chapters_data = self.analyzer.generate_semantic_chapters(
                    video_id, segment_duration=300, granularity="medium"
                )
                description_parts.append("📋 目次 / チャプター")
                description_parts.append("=" * 40)
                for chapter in chapters_data['chapters']:
                    description_parts.append(
                        f"{chapter['start_timestamp']} {chapter['title']}"
                    )
                description_parts.append("")
            
            # カスタムセクション
            if custom_sections:
                for section in custom_sections:
                    description_parts.append(f"【{section}】")
                    description_parts.append("（ここに内容を追加）")
                    description_parts.append("")
            
            # CTA
            if content_data.get('call_to_action'):
                description_parts.append("―" * 20)
                description_parts.append(content_data['call_to_action'])
                description_parts.append("")
            
            # ハッシュタグ
            if include_hashtags and content_data.get('hashtags'):
                description_parts.append("―" * 20)
                description_parts.append(" ".join(content_data['hashtags']))
            
            # 最終的な説明文
            final_description = "\n".join(description_parts)
            
            return {
                "success": True,
                "video_id": video_id,
                "description": final_description,
                "title_suggestions": content_data.get('title_suggestions', []),
                "hashtags": content_data.get('hashtags', []),
                "seo_keywords": content_data.get('seo_keywords', []),
                "target_audience": content_data.get('target_audience', ''),
                "content_data": content_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"コンテンツ生成エラー: {e}"
            }
    
    def generate_optimized_tags(
        self,
        video_id: str,
        max_tags: int = 30,
        include_trending: bool = True
    ) -> List[str]:
        """
        SEO最適化されたタグを生成
        
        Args:
            video_id: YouTube動画ID
            max_tags: 最大タグ数
            include_trending: トレンドタグを含めるか
            
        Returns:
            最適化されたタグリスト
        """
        # トランスクリプト取得
        transcript = self.analyzer.get_transcript(video_id)
        full_text = " ".join([seg['text'] for seg in transcript][:20])  # 最初の20セグメント
        
        prompt = f"""
以下の動画内容から、YouTube SEOに最適化されたタグを{max_tags}個生成してください。

動画内容:
{full_text[:1000]}...

タグ生成の基準:
1. 検索ボリュームが高そうなキーワード
2. 動画の内容を正確に表現
3. 競合が少なそうなロングテールキーワード
4. 日本語と英語の適切なバランス
5. 一般的なものから具体的なものまでバランスよく

カンマ区切りでタグのみを返してください。
"""
        
        try:
            response = self.analyzer.model.generate_content(prompt)
            tags_text = response.text.strip()
            
            # タグの抽出と整形
            tags = [tag.strip() for tag in tags_text.split(',')]
            tags = [tag for tag in tags if tag and len(tag) < 100]  # 空タグと長すぎるタグを除外
            
            return tags[:max_tags]
            
        except Exception as e:
            print(f"タグ生成エラー: {e}")
            return []
    
    def update_video_metadata_with_generated_content(
        self,
        video_id: str,
        update_title: bool = False,
        update_description: bool = True,
        update_tags: bool = True,
        title_index: int = 0,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        生成したコンテンツで動画メタデータを更新
        
        Args:
            video_id: YouTube動画ID
            update_title: タイトルを更新するか
            update_description: 説明を更新するか
            update_tags: タグを更新するか
            title_index: 使用するタイトル候補のインデックス
            dry_run: 実際に更新せずプレビューのみ
            
        Returns:
            更新結果
        """
        try:
            # コンテンツ生成
            content_result = self.generate_video_description(video_id)
            if not content_result['success']:
                return content_result
            
            # タグ生成
            tags = self.generate_optimized_tags(video_id) if update_tags else None
            
            # 更新データ準備
            update_data = {}
            
            if update_title and content_result.get('title_suggestions'):
                update_data['title'] = content_result['title_suggestions'][title_index]
            
            if update_description:
                update_data['description'] = content_result['description']
            
            if update_tags and tags:
                update_data['tags'] = tags
            
            # プレビューモード
            if dry_run:
                return {
                    "success": True,
                    "video_id": video_id,
                    "dry_run": True,
                    "preview": update_data,
                    "message": "更新内容のプレビュー（実際には更新されていません）"
                }
            
            # 実際の更新
            credentials = self.auth_manager.get_credentials()
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # 現在のメタデータ取得
            request = youtube.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return {
                    "success": False,
                    "error": "Video not found",
                    "message": f"動画が見つかりません: {video_id}"
                }
            
            current_snippet = response['items'][0]['snippet']
            
            # 更新用スニペット作成
            updated_snippet = current_snippet.copy()
            for key, value in update_data.items():
                updated_snippet[key] = value
            
            # 更新実行
            update_request = youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': updated_snippet
                }
            )
            update_response = update_request.execute()
            
            return {
                "success": True,
                "video_id": video_id,
                "updated_fields": list(update_data.keys()),
                "new_values": update_data,
                "message": "動画メタデータを更新しました"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"更新エラー: {e}"
            }
    
    def generate_social_media_posts(
        self,
        video_id: str,
        platforms: List[str] = ["twitter", "facebook", "linkedin"]
    ) -> Dict[str, str]:
        """
        各SNSプラットフォーム用の投稿文を生成
        
        Args:
            video_id: YouTube動画ID
            platforms: 対象プラットフォーム
            
        Returns:
            プラットフォーム別投稿文
        """
        # コンテンツ情報取得
        content_result = self.generate_video_description(video_id)
        if not content_result['success']:
            return {}
        
        content_data = content_result['content_data']
        
        posts = {}
        
        if "twitter" in platforms:
            # Twitter用（280文字制限）
            posts["twitter"] = f"""
{content_data['short_description']}

▶️ youtu.be/{video_id}

{' '.join(content_data['hashtags'][:5])}
"""
        
        if "facebook" in platforms:
            # Facebook用（より詳細）
            key_points = '\n'.join([f"✅ {point}" for point in content_data['key_points'][:3]])
            posts["facebook"] = f"""
{content_data['title_suggestions'][0]}

{content_data['detailed_summary']}

{key_points}

🎥 動画を見る: https://youtu.be/{video_id}

{' '.join(content_data['hashtags'][:8])}
"""
        
        if "linkedin" in platforms:
            # LinkedIn用（プロフェッショナル）
            posts["linkedin"] = f"""
【{content_data['title_suggestions'][0]}】

{content_data['detailed_summary']}

この動画では以下について解説しています：
{chr(10).join([f"• {outcome}" for outcome in content_data['learning_outcomes'][:3]])}

対象: {content_data['target_audience']}

▶️ 動画リンク: https://youtu.be/{video_id}

{' '.join([tag for tag in content_data['hashtags'] if not tag.startswith('#エンタメ')][:5])}
"""
        
        return posts


def main():
    """テスト実行"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY環境変数が設定されていません")
        return
    
    video_id = "MlIxNOTYMcc"
    generator = YouTubeContentGenerator()
    
    print(f"🎬 動画 {video_id} のコンテンツ生成テスト")
    print("=" * 80)
    
    # 説明文生成
    result = generator.generate_video_description(video_id)
    
    if result['success']:
        print(f"\n✅ コンテンツ生成成功!")
        print(f"\n📝 タイトル候補:")
        for i, title in enumerate(result['title_suggestions'], 1):
            print(f"{i}. {title}")
        
        print(f"\n📄 生成された説明文:")
        print("-" * 40)
        print(result['description'][:500] + "..." if len(result['description']) > 500 else result['description'])
        
        print(f"\n🏷️ ハッシュタグ:")
        print(" ".join(result['hashtags']))
        
        print(f"\n🎯 ターゲット層: {result['target_audience']}")
        
        # SNS投稿文生成
        posts = generator.generate_social_media_posts(video_id)
        
        print(f"\n📱 SNS投稿文:")
        for platform, post in posts.items():
            print(f"\n【{platform.upper()}】")
            print(post)
            print("-" * 40)
    
    else:
        print(f"❌ エラー: {result['message']}")


if __name__ == "__main__":
    main()