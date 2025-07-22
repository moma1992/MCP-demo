#!/usr/bin/env python3
"""
粒度調整パラメータのテストスクリプト
"""

import os
from dotenv import load_dotenv
from src.custom_mcp.gemini_analyzer import GeminiTranscriptAnalyzer

# .envファイルを読み込み
load_dotenv()

def test_different_granularities():
    """異なる粒度でのセマンティック分析テスト"""
    
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY環境変数が設定されていません")
        return False
    
    video_id = "MlIxNOTYMcc"
    analyzer = GeminiTranscriptAnalyzer()
    
    # テストケース定義
    test_cases = [
        {
            "name": "詳細分析 (fine)",
            "granularity": "fine",
            "segment_duration": 180,  # 3分
            "custom_prompt": None
        },
        {
            "name": "標準分析 (medium)",
            "granularity": "medium", 
            "segment_duration": 300,  # 5分
            "custom_prompt": None
        },
        {
            "name": "大まか分析 (coarse)",
            "granularity": "coarse",
            "segment_duration": 600,  # 10分
            "custom_prompt": None
        },
        {
            "name": "カスタム分析 (教育的観点)",
            "granularity": "custom",
            "segment_duration": 300,
            "custom_prompt": """
この動画を教育的な観点から分析してください：
- 学習目標となるトピックを明確に
- 初学者が理解しやすい順序で整理
- 実践的な内容とデモを区別
- 各セクションの難易度を明示
タイトルは学習の観点から分かりやすく命名してください。
"""
        },
        {
            "name": "カスタム分析 (ビジネス向け)",
            "granularity": "custom",
            "segment_duration": 300,
            "custom_prompt": """
この動画をビジネス観点から分析してください：
- ビジネス価値やROIに関連する内容を重視
- 技術的詳細より概念的理解を優先
- 意思決定に役立つ情報を抽出
- エグゼクティブサマリーに適した形式で
"""
        }
    ]
    
    print(f"🎬 動画 {video_id} の粒度別セマンティック分析テスト")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 テストケース {i}/{len(test_cases)}: {test_case['name']}")
        print("-" * 60)
        
        try:
            # セマンティック分析実行
            chapters_data = analyzer.generate_semantic_chapters(
                video_id,
                test_case['segment_duration'],
                test_case['granularity'],
                test_case['custom_prompt']
            )
            
            # 結果表示
            print(f"✅ 分析完了")
            print(f"  - チャプター数: {chapters_data['total_chapters']}")
            print(f"  - セグメント長: {chapters_data['segment_duration']}秒")
            print(f"  - 粒度: {chapters_data['granularity']}")
            
            # 最初の3チャプターを表示
            print(f"\n  生成されたチャプター（最初の3個）:")
            for j, chapter in enumerate(chapters_data['chapters'][:3], 1):
                print(f"  {j}. {chapter['start_timestamp']} {chapter['title']}")
                if test_case['granularity'] == "custom":
                    print(f"     → {chapter['summary']}")
            
            if len(chapters_data['chapters']) > 3:
                print(f"  ... 他 {len(chapters_data['chapters']) - 3} チャプター")
            
            # 結果を保存
            filename = f"semantic_{video_id}_{test_case['granularity']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                import json
                json.dump(chapters_data, f, ensure_ascii=False, indent=2)
            print(f"\n  💾 結果を保存: {filename}")
            
        except Exception as e:
            print(f"❌ エラー: {e}")
    
    print(f"\n🎯 粒度比較テスト完了")
    print("=" * 80)
    print("\n📊 粒度による違い:")
    print("  - fine: より多くの詳細なチャプター、短い区間")
    print("  - medium: バランスの取れた分割")
    print("  - coarse: 主要トピックのみ、長い区間")
    print("  - custom: 特定の観点からの分析")


def compare_chapter_counts():
    """生成されたチャプター数の比較"""
    import json
    import glob
    
    print("\n📈 チャプター数の比較:")
    print("-" * 40)
    
    files = glob.glob("semantic_MlIxNOTYMcc_*.json")
    for file in sorted(files):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            granularity = data.get('granularity', 'unknown')
            chapters = data.get('total_chapters', 0)
            print(f"{granularity:10} : {chapters:2} チャプター")
        except:
            pass


if __name__ == "__main__":
    test_different_granularities()
    compare_chapter_counts()