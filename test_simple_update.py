#!/usr/bin/env python3
"""
シンプルなYouTube動画更新テスト
"""

import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def test_simple_update():
    """シンプルな動画更新テスト"""
    print("🔧 シンプルなYouTube動画更新テスト")
    print("=" * 60)
    
    video_id = "MlIxNOTYMcc"
    
    try:
        from src.custom_mcp.youtube_content_generator import YouTubeContentGenerator
        
        generator = YouTubeContentGenerator()
        
        print("📝 コンテンツ生成中...")
        # シンプルなコンテンツ生成（チャプターなしで高速化）
        content_result = generator.generate_video_description(
            video_id=video_id,
            include_chapters=False,
            include_summary=True,
            include_hashtags=True,
            tone="professional"
        )
        
        if not content_result['success']:
            print(f"❌ コンテンツ生成失敗: {content_result['message']}")
            return False
        
        print(f"✅ コンテンツ生成成功")
        
        # 実際の更新（説明文のみ）
        print("🔄 説明文更新中...")
        update_result = generator.update_video_metadata_with_generated_content(
            video_id=video_id,
            update_title=False,  # タイトルは更新しない
            update_description=True,  # 説明文のみ更新
            update_tags=False,  # タグは更新しない
            dry_run=False  # 実際に更新
        )
        
        if update_result['success']:
            print(f"✅ 動画更新成功!")
            print(f"更新されたフィールド: {update_result.get('updated_fields', [])}")
            return True
        else:
            print(f"❌ 動画更新失敗: {update_result['message']}")
            print(f"エラー詳細: {update_result.get('error', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_simple_update()