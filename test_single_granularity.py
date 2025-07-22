#!/usr/bin/env python3
"""
単一粒度のテストスクリプト（カスタムプロンプト例）
"""

import os
from dotenv import load_dotenv
from src.custom_mcp.gemini_analyzer import GeminiTranscriptAnalyzer

# .envファイルを読み込み
load_dotenv()

def test_custom_granularity():
    """カスタムプロンプトでのセマンティック分析テスト"""
    
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY環境変数が設定されていません")
        return False
    
    video_id = "MlIxNOTYMcc"
    analyzer = GeminiTranscriptAnalyzer()
    
    print("🎬 カスタム粒度テスト - 初心者向け詳細分析")
    print("=" * 80)
    
    custom_prompt = """
この動画を初心者エンジニア向けに最適化して分析してください：

1. 専門用語は分かりやすく説明されている箇所を重視
2. 実践的なデモや具体例がある部分を明確に
3. 理解の順序として適切な流れになるよう構成
4. 各セクションに「学習ポイント」を含める
5. タイトルは「〜について学ぶ」「〜の基礎」など学習者向けに

要約は80文字以内で、そのセクションで何が学べるかを明確に記載してください。
"""
    
    try:
        # 詳細分析（3分セグメント）
        print("🔍 カスタムプロンプトで分析中...")
        chapters_data = analyzer.generate_semantic_chapters(
            video_id,
            segment_duration=180,  # 3分セグメント
            granularity="custom",
            custom_prompt=custom_prompt
        )
        
        # 結果表示
        print(f"\n✅ 分析完了!")
        print(f"動画時間: {chapters_data['total_duration_formatted']}")
        print(f"チャプター数: {chapters_data['total_chapters']}")
        
        print(f"\n📋 初心者向けチャプター:")
        for i, chapter in enumerate(chapters_data['chapters'], 1):
            print(f"\n{i}. {chapter['start_timestamp']} {chapter['title']}")
            print(f"   カテゴリー: {chapter['topic_category']}")
            print(f"   学習内容: {chapter['summary']}")
            print(f"   レベル: {chapter['technical_level']}")
            if chapter.get('key_points'):
                print(f"   学習ポイント: {', '.join(chapter['key_points'])}")
        
        # YouTube説明欄用生成
        description = analyzer.format_for_youtube_description(chapters_data)
        
        print(f"\n📝 YouTube説明欄用（初心者向け）:")
        print("-" * 60)
        print(description[:1000] + "..." if len(description) > 1000 else description)
        
        # 結果保存
        with open("semantic_custom_beginner.json", 'w', encoding='utf-8') as f:
            import json
            json.dump(chapters_data, f, ensure_ascii=False, indent=2)
        
        with open("youtube_description_beginner.txt", 'w', encoding='utf-8') as f:
            f.write(description)
        
        print(f"\n💾 保存完了:")
        print("  - semantic_custom_beginner.json")
        print("  - youtube_description_beginner.txt")
        
    except Exception as e:
        print(f"❌ エラー: {e}")


def test_coarse_granularity():
    """大まかな粒度でのテスト（高速）"""
    
    video_id = "MlIxNOTYMcc"
    analyzer = GeminiTranscriptAnalyzer()
    
    print("\n\n🎬 大まかな粒度テスト - エグゼクティブサマリー")
    print("=" * 80)
    
    try:
        # 大まかな分析（15分セグメント）
        print("🔍 大まかな分析中...")
        chapters_data = analyzer.generate_semantic_chapters(
            video_id,
            segment_duration=900,  # 15分セグメント
            granularity="coarse"
        )
        
        print(f"\n✅ 分析完了!")
        print(f"チャプター数: {chapters_data['total_chapters']} (主要セクションのみ)")
        
        print(f"\n📋 主要セクション:")
        for i, chapter in enumerate(chapters_data['chapters'], 1):
            print(f"{i}. {chapter['start_timestamp']} {chapter['title']} - {chapter['summary']}")
        
    except Exception as e:
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    # カスタムプロンプトテスト
    test_custom_granularity()
    
    # 大まかな分析テスト
    test_coarse_granularity()