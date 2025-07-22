"""
Gemini APIを使用したセマンティック分析とチャプター生成
YouTube動画のトランスクリプトを意味のある目次に変換
"""

import json
import os
import re
from datetime import timedelta
from typing import Any

import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi


class GeminiTranscriptAnalyzer:
    """Gemini APIを使用したトランスクリプト分析クラス"""

    def __init__(self, api_key: str | None = None):
        """
        初期化
        
        Args:
            api_key: Gemini API key (環境変数 GEMINI_API_KEY からも取得可能)
        """
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError("Gemini API key が必要です。環境変数 GEMINI_API_KEY を設定するか、api_key パラメータを指定してください。")

        # Gemini API設定
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def format_timestamp(self, seconds: float) -> str:
        """秒をタイムスタンプ形式（HH:MM:SS）に変換"""
        td = timedelta(seconds=int(seconds))
        hours, remainder = divmod(td.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_transcript(self, video_id: str) -> list[dict[str, Any]]:
        """YouTube動画のトランスクリプトを取得"""
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en'])
            return transcript
        except Exception as e:
            raise Exception(f"トランスクリプト取得エラー: {e}")

    def create_segments_for_analysis(self, transcript: list[dict], segment_duration: int = 300) -> list[dict]:
        """
        分析用にトランスクリプトをセグメントに分割
        
        Args:
            transcript: YouTubeトランスクリプト
            segment_duration: セグメントの長さ（秒）デフォルト5分
        """
        segments = []
        current_segment = {
            "start_time": 0,
            "end_time": 0,
            "text": "",
            "transcript_entries": []
        }

        for entry in transcript:
            start_time = entry['start']
            text = entry['text']

            # 新しいセグメントの開始判定
            if start_time - current_segment["start_time"] >= segment_duration:
                if current_segment["text"]:
                    current_segment["end_time"] = start_time
                    segments.append(current_segment.copy())

                # 新しいセグメント開始
                current_segment = {
                    "start_time": start_time,
                    "end_time": start_time,
                    "text": text,
                    "transcript_entries": [entry]
                }
            else:
                current_segment["text"] += " " + text
                current_segment["transcript_entries"].append(entry)
                current_segment["end_time"] = start_time + entry.get('duration', 0)

        # 最後のセグメントを追加
        if current_segment["text"]:
            segments.append(current_segment)

        return segments

    def analyze_segment_with_gemini(
        self, 
        segment: dict[str, Any],
        granularity: str = "medium",
        custom_prompt: str | None = None
    ) -> dict[str, Any]:
        """
        Geminiを使用してセグメントの内容を分析
        
        Args:
            segment: 分析対象のセグメント
            
        Returns:
            分析結果（トピック、概要、キーワード等）
        """

        # カスタムプロンプトが指定されている場合
        if custom_prompt:
            prompt = f"""
以下のYouTube動画トランスクリプトを分析してください：

トランスクリプト:
「{segment['text']}」

時間: {self.format_timestamp(segment['start_time'])} - {self.format_timestamp(segment['end_time'])}

{custom_prompt}

回答は必ずJSON形式で以下の項目を含めてください：
- topic_category: 内容カテゴリー
- title: タイトル
- summary: 要約
- key_points: 重要ポイント（配列）
- technical_level: 技術レベル
- contains_demo: デモの有無
- contains_code: コードの有無
"""
        else:
            # 粒度に応じたプロンプト調整
            title_length = {
                "fine": 20,
                "medium": 15,
                "coarse": 10
            }.get(granularity, 15)
            
            summary_length = {
                "fine": 100,
                "medium": 50,
                "coarse": 30
            }.get(granularity, 50)
            
            key_points_count = {
                "fine": 5,
                "medium": 3,
                "coarse": 2
            }.get(granularity, 3)
            
            granularity_instruction = {
                "fine": "非常に詳細に分析し、細かなトピックの変化も捉えてください。",
                "medium": "主要なトピックと概念を抽出してください。",
                "coarse": "最も重要な主題のみを抽出してください。"
            }.get(granularity, "")

            prompt = f"""
以下は YouTube 動画の一部分のトランスクリプトです。{granularity_instruction}
以下の情報をJSON形式で返してください：

トランスクリプト:
「{segment['text']}」

時間: {self.format_timestamp(segment['start_time'])} - {self.format_timestamp(segment['end_time'])}

分析してほしい項目:
1. topic_category: このセグメントの内容カテゴリー（例: "導入", "技術解説", "デモ", "質疑応答", "まとめ" など）
2. title: セグメントの簡潔なタイトル（{title_length}文字以内、YouTube目次に適した形）
3. summary: 内容の要約（{summary_length}文字以内）
4. key_points: 重要なポイント（配列、最大{key_points_count}個）
5. technical_level: 技術レベル（"beginner", "intermediate", "advanced", "general"）
6. contains_demo: デモンストレーションが含まれているか（true/false）
7. contains_code: コードの説明が含まれているか（true/false）

回答は必ずJSON形式のみで返してください。説明文は不要です。

例:
{{
  "topic_category": "技術解説",
  "title": "AWS Lambda基礎",
  "summary": "サーバーレス関数の基本概念と使用方法を説明",
  "key_points": ["サーバーレス", "Lambda関数", "実行環境"],
  "technical_level": "beginner",
  "contains_demo": false,
  "contains_code": true
}}
"""

        try:
            response = self.model.generate_content(prompt)

            # JSONレスポンスをパース
            response_text = response.text.strip()

            # レスポンスからJSON部分を抽出（念のため）
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                analysis = json.loads(json_str)
            else:
                analysis = json.loads(response_text)

            return analysis

        except Exception as e:
            print(f"Gemini分析エラー: {e}")
            # フォールバック分析
            return {
                "topic_category": "その他",
                "title": "セクション",
                "summary": segment['text'][:50] + "..." if len(segment['text']) > 50 else segment['text'],
                "key_points": [],
                "technical_level": "general",
                "contains_demo": False,
                "contains_code": False
            }

    def generate_semantic_chapters(
        self, 
        video_id: str, 
        segment_duration: int = 300,
        granularity: str = "medium",
        custom_prompt: str | None = None
    ) -> dict[str, Any]:
        """
        セマンティック分析による意味のあるチャプターを生成
        
        Args:
            video_id: YouTube動画ID
            segment_duration: セグメント長（秒）
            granularity: 粒度レベル ("fine", "medium", "coarse", "custom")
                - fine: 詳細な分割（2-3分ごと）
                - medium: 標準的な分割（5分ごと）
                - coarse: 大まかな分割（10分以上）
                - custom: カスタムプロンプト使用
            custom_prompt: カスタム分析指示（granularity="custom"時に使用）
            
        Returns:
            チャプター情報を含む辞書
        """
        # 粒度に応じたセグメント長の調整
        if granularity == "fine":
            segment_duration = min(segment_duration, 180)  # 3分以下
        elif granularity == "coarse":
            segment_duration = max(segment_duration, 600)  # 10分以上
        elif granularity == "custom" and not custom_prompt:
            raise ValueError("custom_promptが必要です（granularity='custom'の場合）")
        print(f"🎬 動画 {video_id} のセマンティック分析開始...")

        # トランスクリプト取得
        transcript = self.get_transcript(video_id)
        print(f"✅ {len(transcript)}セグメント取得完了")

        # 分析用セグメントに分割
        segments = self.create_segments_for_analysis(transcript, segment_duration)
        print(f"📊 {len(segments)}個の分析セグメントに分割")

        # 各セグメントをGeminiで分析
        analyzed_chapters = []
        for i, segment in enumerate(segments):
            print(f"🔍 セグメント {i+1}/{len(segments)} 分析中...")

            analysis = self.analyze_segment_with_gemini(segment, granularity, custom_prompt)

            chapter = {
                "index": i + 1,
                "start_seconds": segment["start_time"],
                "end_seconds": segment["end_time"],
                "start_timestamp": self.format_timestamp(segment["start_time"]),
                "end_timestamp": self.format_timestamp(segment["end_time"]),
                "duration_seconds": segment["end_time"] - segment["start_time"],
                "original_text": segment["text"],
                **analysis
            }

            analyzed_chapters.append(chapter)
            print(f"   ✅ {chapter['title']} ({chapter['topic_category']})")

        # 動画の総時間
        total_duration = transcript[-1]['start'] + transcript[-1]['duration']

        result = {
            "video_id": video_id,
            "total_duration_seconds": total_duration,
            "total_duration_formatted": self.format_timestamp(total_duration),
            "total_chapters": len(analyzed_chapters),
            "analysis_method": "gemini_semantic",
            "segment_duration": segment_duration,
            "granularity": granularity,
            "custom_prompt_used": custom_prompt is not None,
            "chapters": analyzed_chapters
        }

        return result

    def format_for_youtube_description(self, chapters_data: dict[str, Any]) -> str:
        """
        YouTube説明欄用のフォーマットされた目次を生成
        
        Args:
            chapters_data: generate_semantic_chapters()の戻り値
            
        Returns:
            YouTube説明欄にそのまま貼り付け可能なテキスト
        """

        lines = []
        lines.append("📋 目次 / Table of Contents")
        lines.append("=" * 40)
        lines.append("")

        # カテゴリ別グループ化
        category_groups = {}
        for chapter in chapters_data['chapters']:
            category = chapter['topic_category']
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(chapter)

        # カテゴリ順序
        category_order = ["導入", "技術解説", "デモ", "実装", "質疑応答", "まとめ", "その他"]

        for category in category_order:
            if category in category_groups:
                lines.append(f"## {category}")
                for chapter in category_groups[category]:
                    line = f"{chapter['start_timestamp']} {chapter['title']}"
                    if chapter['summary']:
                        line += f" - {chapter['summary']}"
                    lines.append(line)
                lines.append("")

        # その他のカテゴリ
        for category, chapters in category_groups.items():
            if category not in category_order:
                lines.append(f"## {category}")
                for chapter in chapters:
                    line = f"{chapter['start_timestamp']} {chapter['title']}"
                    if chapter['summary']:
                        line += f" - {chapter['summary']}"
                    lines.append(line)
                lines.append("")

        # 技術レベル表示
        tech_levels = set(ch['technical_level'] for ch in chapters_data['chapters'])
        if tech_levels:
            lines.append("🎯 技術レベル:")
            level_names = {
                "beginner": "初心者向け",
                "intermediate": "中級者向け",
                "advanced": "上級者向け",
                "general": "一般向け"
            }
            for level in tech_levels:
                lines.append(f"  • {level_names.get(level, level)}")
            lines.append("")

        # 自動生成の注記
        lines.append("---")
        lines.append("🤖 この目次はAIによって自動生成されました")
        lines.append(f"📺 動画時間: {chapters_data['total_duration_formatted']}")
        lines.append(f"📊 チャプター数: {chapters_data['total_chapters']}")

        return "\n".join(lines)

    def save_results(self, video_id: str, chapters_data: dict[str, Any]):
        """結果をファイルに保存"""

        # 1. 詳細分析結果をJSON保存
        with open(f"semantic_chapters_{video_id}.json", 'w', encoding='utf-8') as f:
            json.dump(chapters_data, f, ensure_ascii=False, indent=2)

        # 2. YouTube説明欄用テキスト保存
        youtube_description = self.format_for_youtube_description(chapters_data)
        with open(f"youtube_description_{video_id}.txt", 'w', encoding='utf-8') as f:
            f.write(youtube_description)

        # 3. 簡易チャプターリスト保存
        with open(f"simple_chapters_{video_id}.txt", 'w', encoding='utf-8') as f:
            for chapter in chapters_data['chapters']:
                f.write(f"{chapter['start_timestamp']} {chapter['title']}\n")

        print("\n💾 結果を保存しました:")
        print(f"  - semantic_chapters_{video_id}.json (詳細分析)")
        print(f"  - youtube_description_{video_id}.txt (YouTube説明欄用)")
        print(f"  - simple_chapters_{video_id}.txt (簡易リスト)")


def main():
    """テスト実行"""

    # 環境変数チェック
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY 環境変数が設定されていません")
        print("Google AI Studio (https://aistudio.google.com/) でAPIキーを取得してください")
        return

    video_id = "MlIxNOTYMcc"

    try:
        analyzer = GeminiTranscriptAnalyzer()

        # セマンティック分析実行
        chapters_data = analyzer.generate_semantic_chapters(video_id, segment_duration=300)

        # 結果保存
        analyzer.save_results(video_id, chapters_data)

        # 結果表示
        print("\n🎉 セマンティック分析完了!")
        print(f"動画: {video_id}")
        print(f"時間: {chapters_data['total_duration_formatted']}")
        print(f"チャプター: {chapters_data['total_chapters']}個")

        print("\n📋 生成されたチャプター:")
        for chapter in chapters_data['chapters']:
            print(f"  {chapter['start_timestamp']} {chapter['title']} ({chapter['topic_category']})")

    except Exception as e:
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    main()
