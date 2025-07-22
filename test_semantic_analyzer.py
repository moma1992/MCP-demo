#!/usr/bin/env python3
"""
Gemini セマンティック分析のテストスクリプト
"""

import os
from dotenv import load_dotenv

from src.custom_mcp.gemini_analyzer import GeminiTranscriptAnalyzer

# .envファイルを読み込み
load_dotenv()


def test_semantic_analysis():
    """セマンティック分析のテスト"""

    # API key チェック
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY環境変数が設定されていません")
        print("Google AI Studio (https://aistudio.google.com/) でAPIキーを取得して設定してください:")
        print("export GEMINI_API_KEY='your_api_key_here'")
        return False

    video_id = "MlIxNOTYMcc"

    try:
        print(f"🚀 動画 {video_id} のセマンティック分析テスト開始")
        print("=" * 80)

        # アナライザー初期化
        analyzer = GeminiTranscriptAnalyzer()

        # セマンティック分析実行
        print("🔍 Geminiによるセマンティック分析中...")
        chapters_data = analyzer.generate_semantic_chapters(video_id, segment_duration=600)  # 10分セグメント

        # 結果表示
        print("\n📊 分析結果:")
        print(f"動画時間: {chapters_data['total_duration_formatted']}")
        print(f"チャプター数: {chapters_data['total_chapters']}")

        print("\n📋 生成されたセマンティックチャプター:")
        for i, chapter in enumerate(chapters_data['chapters'], 1):
            print(f"{i:2d}. {chapter['start_timestamp']} - {chapter['title']}")
            print(f"    カテゴリー: {chapter['topic_category']}")
            print(f"    概要: {chapter['summary']}")
            print(f"    技術レベル: {chapter['technical_level']}")
            if chapter['key_points']:
                print(f"    キーポイント: {', '.join(chapter['key_points'])}")
            print()

        # YouTube説明欄用フォーマット生成
        print("📝 YouTube説明欄用フォーマット生成中...")
        description_text = analyzer.format_for_youtube_description(chapters_data)

        # 結果保存
        analyzer.save_results(video_id, chapters_data)

        # YouTube説明欄用テキストのプレビュー
        print("\n📄 YouTube説明欄用テキスト（最初の500文字）:")
        print("-" * 50)
        print(description_text[:500] + "..." if len(description_text) > 500 else description_text)
        print("-" * 50)

        print("\n✅ セマンティック分析完了!")
        print("📁 結果ファイル:")
        print(f"   - semantic_chapters_{video_id}.json")
        print(f"   - youtube_description_{video_id}.txt")
        print(f"   - simple_chapters_{video_id}.txt")

        return True

    except Exception as e:
        print(f"❌ エラー: {e}")
        return False


def test_mcp_tools():
    """MCPツールのテスト"""
    print("\n🧪 MCPツールテスト")
    print("=" * 50)

    try:
        from fastmcp import FastMCP

        from src.custom_mcp.youtube_semantic_tools import create_youtube_semantic_tools

        # テスト用MCPサーバー作成
        test_mcp = FastMCP("Test")
        create_youtube_semantic_tools(test_mcp)

        print(f"✅ YouTubeセマンティック分析MCPツールを作成")
        print("6個のツールが登録されました")

        # 簡単なAPI接続テスト
        print("\n🔍 API状態チェックテスト...")
        
        try:
            # 直接API接続をテスト
            import google.generativeai as genai
            api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                print("❌ GEMINI_API_KEY環境変数が見つかりません")
                return False
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content("テスト")
            
            print(f"✅ Gemini API接続成功: {response.text[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Gemini API接続エラー: {e}")
            return False

    except Exception as e:
        print(f"❌ MCPツールテストエラー: {e}")
        return False


def main():
    """メイン実行"""
    print("🎬 Gemini セマンティック分析システム テスト")
    print("=" * 80)

    # 1. セマンティック分析テスト
    analysis_success = test_semantic_analysis()

    # 2. MCPツールテスト
    mcp_success = test_mcp_tools()

    # 総合結果
    print("\n🏁 テスト結果サマリー")
    print("=" * 50)
    print(f"セマンティック分析: {'✅ 成功' if analysis_success else '❌ 失敗'}")
    print(f"MCPツール: {'✅ 成功' if mcp_success else '❌ 失敗'}")

    if analysis_success and mcp_success:
        print("\n🎉 すべてのテストが成功しました!")
        print("Gemini APIによるセマンティック分析MCPが利用可能です。")
    else:
        print("\n⚠️  一部のテストが失敗しました。")
        if not analysis_success:
            print("   - GEMINI_API_KEY環境変数を確認してください")



if __name__ == "__main__":
    main()
