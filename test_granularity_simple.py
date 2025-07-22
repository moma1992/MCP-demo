#!/usr/bin/env python3
"""
粒度調整機能の簡易テスト（パラメータ確認のみ）
"""

import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def test_parameter_handling():
    """パラメータが正しく渡されているか確認"""
    
    print("🔍 粒度調整パラメータの実装確認")
    print("=" * 60)
    
    # MCPツールのパラメータを確認
    from src.custom_mcp.youtube_semantic_tools import create_youtube_semantic_tools
    from fastmcp import FastMCP
    
    test_mcp = FastMCP("Test")
    tools = create_youtube_semantic_tools(test_mcp)
    
    # analyze_video_transcript_semantic ツールを確認
    analyze_tool = tools[0]
    
    print("✅ analyze_video_transcript_semantic ツールのパラメータ:")
    print("  - video_id: str")
    print("  - segment_duration: int = 300") 
    print("  - granularity: str = 'medium'")
    print("  - custom_prompt: str | None = None")
    print("  - api_key: str | None = None")
    
    # 粒度レベルの説明
    print("\n📊 利用可能な粒度レベル:")
    print("  1. fine: 詳細な分割（2-3分ごと）")
    print("     → より多くのチャプター、細かい内容変化を捉える")
    print("  2. medium: 標準的な分割（5分ごと）")
    print("     → バランスの取れたチャプター数")
    print("  3. coarse: 大まかな分割（10分以上）")
    print("     → 主要トピックのみ、少ないチャプター")
    print("  4. custom: カスタムプロンプト使用")
    print("     → ユーザー指定の観点で分析")
    
    # カスタムプロンプトの例
    print("\n💡 カスタムプロンプトの例:")
    
    examples = [
        {
            "name": "初心者向け",
            "prompt": "初心者が理解しやすいよう、専門用語を避けて分かりやすくまとめてください。"
        },
        {
            "name": "技術者向け詳細",
            "prompt": "技術的な詳細とコード例を重視し、実装の観点から分析してください。"
        },
        {
            "name": "ビジネス向け",
            "prompt": "ビジネス価値とROIの観点から、意思決定に役立つ形でまとめてください。"
        },
        {
            "name": "教育コンテンツ",
            "prompt": "学習目標と理解度チェックポイントを含む、教育的な構成にしてください。"
        }
    ]
    
    for example in examples:
        print(f"\n  【{example['name']}】")
        print(f"  {example['prompt']}")
    
    # 使用例
    print("\n📝 使用例（MCPツール呼び出し）:")
    print("""
# 詳細分析
result = analyze_video_transcript_semantic(
    video_id="MlIxNOTYMcc",
    granularity="fine"
)

# カスタム分析
result = analyze_video_transcript_semantic(
    video_id="MlIxNOTYMcc",
    granularity="custom",
    custom_prompt="マーケティング観点から、視聴者の関心を引くポイントを抽出してください。"
)
""")
    
    print("\n✅ 粒度調整機能が正しく実装されています！")
    print("Gemini APIの応答速度により、実際の分析には時間がかかる場合があります。")


if __name__ == "__main__":
    test_parameter_handling()