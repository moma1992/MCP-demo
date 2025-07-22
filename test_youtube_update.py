#!/usr/bin/env python3
"""
YouTube動画更新機能の詳細テスト
エラーの原因を特定するためのデバッグスクリプト
"""

import os
from dotenv import load_dotenv
from src.custom_mcp.youtube_content_generator import YouTubeContentGenerator

# .envファイルを読み込み
load_dotenv()

def test_youtube_oauth_status():
    """YouTube OAuth認証状態を確認"""
    print("🔐 YouTube OAuth認証状態確認")
    print("=" * 60)
    
    try:
        from src.custom_mcp.youtube_auth import YouTubeAuthManager
        
        auth_manager = YouTubeAuthManager()
        
        # 認証ファイルの存在確認
        credentials_path = os.path.expanduser("~/.youtube_mcp/credentials.json")
        token_path = os.path.expanduser("~/.youtube_mcp/token.pickle")
        
        print(f"認証ファイル: {'✅ 存在' if os.path.exists(credentials_path) else '❌ 未設定'}")
        print(f"トークンファイル: {'✅ 存在' if os.path.exists(token_path) else '❌ 未設定'}")
        
        # 認証情報の取得テスト
        try:
            credentials = auth_manager.get_credentials()
            print(f"認証情報取得: ✅ 成功")
            print(f"有効期限チェック: {'✅ 有効' if credentials.valid else '❌ 期限切れ'}")
            
            # YouTube APIアクセステスト
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # 自分のチャンネル情報取得テスト
            request = youtube.channels().list(part='snippet', mine=True)
            response = request.execute()
            
            if response.get('items'):
                channel = response['items'][0]
                print(f"チャンネル名: {channel['snippet']['title']}")
                print(f"YouTube API接続: ✅ 成功")
                return True
            else:
                print(f"YouTube API接続: ❌ チャンネル情報取得失敗")
                return False
                
        except Exception as e:
            print(f"認証エラー: ❌ {e}")
            return False
            
    except Exception as e:
        print(f"初期化エラー: ❌ {e}")
        return False

def test_video_metadata_read():
    """指定動画のメタデータ読み取りテスト"""
    print(f"\n📹 動画メタデータ読み取りテスト")
    print("=" * 60)
    
    video_id = "MlIxNOTYMcc"
    
    try:
        from src.custom_mcp.youtube_auth import YouTubeAuthManager
        from googleapiclient.discovery import build
        
        auth_manager = YouTubeAuthManager()
        credentials = auth_manager.get_credentials()
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # 動画情報取得
        request = youtube.videos().list(
            part='snippet,status',
            id=video_id
        )
        response = request.execute()
        
        if response.get('items'):
            video = response['items'][0]
            snippet = video['snippet']
            status = video['status']
            
            print(f"✅ 動画情報取得成功")
            print(f"タイトル: {snippet['title']}")
            print(f"チャンネル: {snippet['channelTitle']}")
            print(f"公開状態: {status.get('privacyStatus', 'unknown')}")
            print(f"説明文長: {len(snippet.get('description', ''))}文字")
            print(f"タグ数: {len(snippet.get('tags', []))}個")
            
            # 自分の動画かチェック
            my_channel_request = youtube.channels().list(part='id', mine=True)
            my_channel_response = my_channel_request.execute()
            
            if my_channel_response.get('items'):
                my_channel_id = my_channel_response['items'][0]['id']
                is_my_video = snippet['channelId'] == my_channel_id
                print(f"所有権: {'✅ 自分の動画' if is_my_video else '❌ 他人の動画'}")
                return is_my_video
            else:
                print(f"所有権: ❌ チャンネルID取得失敗")
                return False
                
        else:
            print(f"❌ 動画が見つかりません: {video_id}")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def test_content_generation():
    """コンテンツ生成テスト"""
    print(f"\n📝 コンテンツ生成テスト")
    print("=" * 60)
    
    video_id = "MlIxNOTYMcc"
    
    try:
        generator = YouTubeContentGenerator()
        
        # 説明文生成テスト
        result = generator.generate_video_description(
            video_id=video_id,
            include_chapters=False,  # チャプターなしで高速化
            tone="professional"
        )
        
        if result['success']:
            print(f"✅ コンテンツ生成成功")
            print(f"タイトル候補: {len(result['title_suggestions'])}個")
            print(f"説明文長: {len(result['description'])}文字")
            print(f"ハッシュタグ: {len(result['hashtags'])}個")
            
            # 生成された説明文のプレビュー
            print(f"\n📄 生成された説明文（最初の200文字）:")
            print(result['description'][:200] + "..." if len(result['description']) > 200 else result['description'])
            
            return result
        else:
            print(f"❌ コンテンツ生成失敗: {result['message']}")
            return None
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return None

def test_dry_run_update():
    """ドライラン更新テスト"""
    print(f"\n🔍 ドライラン更新テスト")
    print("=" * 60)
    
    video_id = "MlIxNOTYMcc"
    
    try:
        generator = YouTubeContentGenerator()
        
        # ドライラン（実際には更新しない）
        result = generator.update_video_metadata_with_generated_content(
            video_id=video_id,
            update_title=False,  # タイトルは更新しない（安全のため）
            update_description=True,
            update_tags=True,
            dry_run=True  # プレビューのみ
        )
        
        if result['success']:
            print(f"✅ ドライラン成功")
            print(f"プレビューモード: {result.get('dry_run', False)}")
            
            preview = result.get('preview', {})
            if 'description' in preview:
                print(f"説明文プレビュー: {len(preview['description'])}文字")
            if 'tags' in preview:
                print(f"タグプレビュー: {len(preview['tags'])}個")
                print(f"タグ例: {preview['tags'][:5]}")
            
            return True
        else:
            print(f"❌ ドライラン失敗: {result['message']}")
            print(f"エラー詳細: {result.get('error', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def test_actual_update():
    """実際の更新テスト（注意: 実際に動画が更新されます）"""
    print(f"\n⚠️  実際の更新テスト（実際に動画が更新されます）")
    print("=" * 60)
    
    # 安全確認
    print("この操作は実際にYouTube動画を更新します。")
    print("続行する場合は 'yes' と入力してください:")
    
    try:
        user_input = input("続行しますか？ (yes/no): ").strip().lower()
        if user_input != 'yes':
            print("❌ ユーザーによりキャンセルされました")
            return False
    except EOFError:
        print("❌ 対話モードで実行してください")
        return False
    
    video_id = "MlIxNOTYMcc"
    
    try:
        generator = YouTubeContentGenerator()
        
        # 実際の更新（説明文のみ、タイトルは変更しない）
        result = generator.update_video_metadata_with_generated_content(
            video_id=video_id,
            update_title=False,  # 安全のためタイトルは更新しない
            update_description=True,
            update_tags=False,  # まずは説明文のみ
            dry_run=False  # 実際に更新
        )
        
        if result['success']:
            print(f"✅ 更新成功!")
            print(f"更新されたフィールド: {result.get('updated_fields', [])}")
            return True
        else:
            print(f"❌ 更新失敗: {result['message']}")
            print(f"エラー詳細: {result.get('error', 'N/A')}")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

def main():
    """メイン実行"""
    print("🎬 YouTube動画更新機能 詳細テスト")
    print("=" * 80)
    
    # 1. OAuth認証確認
    auth_ok = test_youtube_oauth_status()
    
    # 2. 動画メタデータ読み取り
    if auth_ok:
        video_accessible = test_video_metadata_read()
    else:
        print("❌ 認証に失敗したため、以降のテストをスキップします")
        return
    
    # 3. コンテンツ生成
    if video_accessible:
        content_result = test_content_generation()
    else:
        print("❌ 動画アクセスに失敗したため、以降のテストをスキップします")
        return
    
    # 4. ドライラン
    if content_result:
        dry_run_ok = test_dry_run_update()
    else:
        print("❌ コンテンツ生成に失敗したため、以降のテストをスキップします")
        return
    
    # 5. 実際の更新（オプション）
    if dry_run_ok:
        print(f"\n🎯 診断結果:")
        print("=" * 50)
        print("✅ OAuth認証: 正常")
        print("✅ 動画アクセス: 可能")
        print("✅ コンテンツ生成: 正常")
        print("✅ ドライラン: 成功")
        print("\n実際の更新を試す場合は、以下を実行してください:")
        print("test_actual_update()")
    else:
        print(f"\n❌ 問題が検出されました")
        print("ドライランが失敗したため、実際の更新は推奨されません")

if __name__ == "__main__":
    main()