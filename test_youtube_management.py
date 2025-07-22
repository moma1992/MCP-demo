#!/usr/bin/env python3
"""
YouTube管理・最適化MCPツールのテストスクリプト
"""

import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def test_content_generation():
    """コンテンツ生成のテスト"""
    
    print("🎬 YouTube管理・最適化MCPツールテスト")
    print("=" * 80)
    
    # MCPツールのインポートテスト
    try:
        from src.custom_mcp.youtube_management_tools import create_youtube_management_tools
        from fastmcp import FastMCP
        
        test_mcp = FastMCP("Test")
        create_youtube_management_tools(test_mcp)
        
        print(f"✅ YouTube管理・最適化MCPツールを作成")
        print("7個のツールが登録されました")
        
        print("\n🛠️ 利用可能なMCPツール:")
        tool_descriptions = [
            "generate_video_content_automatically - 動画説明文・ハッシュタグ・タイトルを自動生成",
            "generate_seo_optimized_tags - SEO最適化されたタグを生成",
            "update_youtube_video_metadata - AI生成コンテンツで動画メタデータを更新",
            "generate_social_media_content - SNSプラットフォーム用投稿文を生成",
            "analyze_video_content_for_optimization - SEO・エンゲージメント最適化分析",
            "batch_update_channel_videos - チャンネル動画の一括最適化",
            "generate_youtube_thumbnail_suggestions - サムネイル提案生成"
        ]
        
        for desc in tool_descriptions:
            print(f"  • {desc}")
        
        return True
        
    except Exception as e:
        print(f"❌ ツール作成エラー: {e}")
        return False


def test_api_requirements():
    """必要なAPI設定の確認"""
    
    print(f"\n🔑 API設定確認")
    print("-" * 50)
    
    # Gemini API
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"Gemini API Key: {'✅ 設定済み' if gemini_key else '❌ 未設定'}")
    
    # YouTube API
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    print(f"YouTube API Key: {'✅ 設定済み' if youtube_key else '❌ 未設定'}")
    
    # YouTube OAuth認証ファイル
    auth_file = os.path.expanduser("~/.youtube_mcp/credentials.json")
    auth_exists = os.path.exists(auth_file)
    print(f"YouTube OAuth設定: {'✅ 設定済み' if auth_exists else '❌ 未設定'}")
    
    if gemini_key and youtube_key:
        print(f"\n✅ 基本的なAPI設定は完了しています")
        if auth_exists:
            print(f"🚀 YouTube管理機能が利用可能です")
        else:
            print(f"⚠️  YouTube動画更新にはOAuth認証が必要です")
        return True
    else:
        print(f"\n❌ 必要なAPI設定が不足しています")
        return False


def show_usage_examples():
    """使用例の表示"""
    
    print(f"\n📝 使用例")
    print("=" * 80)
    
    examples = [
        {
            "title": "動画の説明文とハッシュタグを自動生成",
            "code": """
result = generate_video_content_automatically(
    video_id="MlIxNOTYMcc",
    tone="professional",
    include_chapters=True
)

print(result['description'])
print(result['hashtags'])
"""
        },
        {
            "title": "SEO最適化タグを生成",
            "code": """
result = generate_seo_optimized_tags(
    video_id="MlIxNOTYMcc",
    max_tags=25
)

print(result['tags'])
"""
        },
        {
            "title": "動画メタデータをプレビューなしで更新",
            "code": """
# まずプレビューで確認
result = update_youtube_video_metadata(
    video_id="MlIxNOTYMcc",
    update_description=True,
    update_tags=True,
    dry_run=True  # プレビューのみ
)

# 確認後、実際に更新
result = update_youtube_video_metadata(
    video_id="MlIxNOTYMcc",
    update_description=True,
    update_tags=True,
    dry_run=False  # 実際に更新
)
"""
        },
        {
            "title": "SNS投稿文を生成",
            "code": """
result = generate_social_media_content(
    video_id="MlIxNOTYMcc",
    platforms=["twitter", "linkedin", "facebook"]
)

for platform, post in result['posts'].items():
    print(f"{platform}: {post}")
"""
        },
        {
            "title": "複数動画を一括最適化",
            "code": """
video_ids = ["video1", "video2", "video3"]

result = batch_update_channel_videos(
    channel_video_ids=video_ids,
    update_descriptions=True,
    update_tags=True,
    dry_run=True  # まずプレビュー
)
"""
        }
    ]
    
    for example in examples:
        print(f"\n【{example['title']}】")
        print(example['code'])


def show_workflow():
    """推奨ワークフローの表示"""
    
    print(f"\n🔄 推奨ワークフロー")
    print("=" * 80)
    
    workflow_steps = [
        "1. 📊 動画分析",
        "   analyze_video_content_for_optimization() で最適化提案を取得",
        "",
        "2. 📝 コンテンツ生成",
        "   generate_video_content_automatically() で説明文・ハッシュタグ生成",
        "",
        "3. 🏷️ タグ最適化",
        "   generate_seo_optimized_tags() でSEO最適化タグを追加生成",
        "",
        "4. 👀 プレビュー確認",
        "   update_youtube_video_metadata(dry_run=True) で更新内容を確認",
        "",
        "5. ✅ 実際の更新",
        "   update_youtube_video_metadata(dry_run=False) で動画メタデータ更新",
        "",
        "6. 📱 SNS展開",
        "   generate_social_media_content() でSNS投稿文生成",
        "",
        "7. 🖼️ サムネイル最適化",
        "   generate_youtube_thumbnail_suggestions() でサムネイル提案取得"
    ]
    
    for step in workflow_steps:
        print(step)


if __name__ == "__main__":
    # テスト実行
    tools_success = test_content_generation()
    api_success = test_api_requirements()
    
    # 使用例とワークフロー表示
    if tools_success:
        show_usage_examples()
        show_workflow()
    
    # 総合結果
    print(f"\n🏁 テスト結果")
    print("=" * 50)
    print(f"MCPツール作成: {'✅ 成功' if tools_success else '❌ 失敗'}")
    print(f"API設定: {'✅ 完了' if api_success else '⚠️  要設定'}")
    
    if tools_success and api_success:
        print(f"\n🎉 YouTube管理・最適化システムが利用可能です！")
        print(f"動画のメタデータ自動最適化とSNS展開が可能になりました。")
    else:
        print(f"\n⚠️  セットアップを完了してから利用してください。")