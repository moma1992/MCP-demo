"""Test cases for YouTube tools using FastMCP library"""

import sys
import os
import pytest
from unittest.mock import patch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from custom_mcp.youtube_tools import (
    search_youtube_videos,
    get_video_details,
    analyze_youtube_videos,
    _parse_duration,
    _generate_insights
)


class TestYouTubeTools:
    """Test suite for YouTube tools functionality"""

    @pytest.fixture
    def mock_search_response(self):
        """Mock YouTube search API response"""
        return {
            "items": [
                {
                    "id": {"videoId": "test_video_1"},
                    "snippet": {
                        "title": "Test Video 1",
                        "description": "This is a test video",
                        "channelTitle": "Test Channel",
                        "publishedAt": "2023-01-01T00:00:00Z"
                    }
                },
                {
                    "id": {"videoId": "test_video_2"},
                    "snippet": {
                        "title": "Test Video 2",
                        "description": "Another test video",
                        "channelTitle": "Test Channel 2",
                        "publishedAt": "2023-01-02T00:00:00Z"
                    }
                }
            ]
        }

    @pytest.fixture
    def mock_video_details_response(self):
        """Mock YouTube video details API response"""
        return {
            "items": [
                {
                    "id": "test_video_1",
                    "snippet": {
                        "title": "Test Video 1",
                        "description": "This is a test video description",
                        "channelTitle": "Test Channel",
                        "publishedAt": "2023-01-01T00:00:00Z"
                    },
                    "statistics": {
                        "viewCount": "10000",
                        "likeCount": "500",
                        "commentCount": "50"
                    },
                    "contentDetails": {
                        "duration": "PT5M30S"
                    }
                },
                {
                    "id": "test_video_2",
                    "snippet": {
                        "title": "Test Video 2",
                        "description": "Another test video description",
                        "channelTitle": "Test Channel 2",
                        "publishedAt": "2023-01-02T00:00:00Z"
                    },
                    "statistics": {
                        "viewCount": "20000",
                        "likeCount": "1000",
                        "commentCount": "100"
                    },
                    "contentDetails": {
                        "duration": "PT10M15S"
                    }
                }
            ]
        }

    def test_search_youtube_videos_success(self, httpx_mock, mock_search_response):
        """Test successful YouTube video search"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/search",
                json=mock_search_response
            )
            
            result = search_youtube_videos("test query", max_results=2)
            
            assert "items" in result
            assert len(result["items"]) == 2
            assert result["items"][0]["snippet"]["title"] == "Test Video 1"

    def test_search_youtube_videos_no_api_key(self):
        """Test YouTube search without API key"""
        with patch.dict(os.environ, {}, clear=True):
            result = search_youtube_videos("test query")
            
            assert "error" in result
            assert "YouTube API key is required" in result["error"]

    def test_search_youtube_videos_parameter_validation(self, httpx_mock, mock_search_response):
        """Test parameter validation in YouTube search"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/search",
                json=mock_search_response
            )
            
            # Test max_results bounds
            result = search_youtube_videos("test", max_results=100)  # Should be capped at 50
            assert "items" in result
            
            # Test invalid order parameter
            result = search_youtube_videos("test", order="invalid_order")  # Should default to relevance
            assert "items" in result

    def test_get_video_details_success(self, httpx_mock, mock_video_details_response):
        """Test successful video details retrieval"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/videos",
                json=mock_video_details_response
            )
            
            result = get_video_details(["test_video_1", "test_video_2"])
            
            assert "items" in result
            assert len(result["items"]) == 2
            assert result["items"][0]["statistics"]["viewCount"] == "10000"

    def test_get_video_details_no_api_key(self):
        """Test video details without API key"""
        with patch.dict(os.environ, {}, clear=True):
            result = get_video_details(["test_video_1"])
            
            assert "error" in result
            assert "YouTube API key is required" in result["error"]

    def test_get_video_details_no_video_ids(self):
        """Test video details with empty video IDs"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            result = get_video_details([])
            
            assert "error" in result
            assert "At least one video ID is required" in result["error"]

    def test_get_video_details_too_many_ids(self, httpx_mock, mock_video_details_response):
        """Test video details with too many video IDs"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/videos",
                json=mock_video_details_response
            )
            
            # Test with 60 video IDs (should be limited to 50)
            video_ids = [f"video_{i}" for i in range(60)]
            result = get_video_details(video_ids)
            
            assert "items" in result

    def test_analyze_youtube_videos_success(self, httpx_mock, mock_search_response, mock_video_details_response):
        """Test successful YouTube video analysis"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            # Mock search API call
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/search",
                json=mock_search_response
            )
            
            # Mock video details API call
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/videos",
                json=mock_video_details_response
            )
            
            result = analyze_youtube_videos("test query", max_results=2)
            
            assert "query" in result
            assert "total_videos_analyzed" in result
            assert "metrics" in result
            assert "video_summaries" in result
            assert "insights" in result
            assert result["total_videos_analyzed"] == 2
            assert result["metrics"]["total_views"] == 30000  # 10000 + 20000

    def test_analyze_youtube_videos_search_error(self, httpx_mock):
        """Test analysis when search fails"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/search",
                status_code=403
            )
            
            result = analyze_youtube_videos("test query")
            
            assert "error" in result

    def test_analyze_youtube_videos_no_results(self, httpx_mock):
        """Test analysis with no search results"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/search",
                json={"items": []}
            )
            
            result = analyze_youtube_videos("nonexistent query")
            
            assert "error" in result
            assert "No videos found" in result["error"]

    def test_parse_duration(self):
        """Test YouTube duration parsing"""
        assert _parse_duration("PT5M30S") == 330  # 5*60 + 30
        assert _parse_duration("PT1H2M3S") == 3723  # 1*3600 + 2*60 + 3
        assert _parse_duration("PT45S") == 45
        assert _parse_duration("PT10M") == 600
        assert _parse_duration("PT2H") == 7200
        assert _parse_duration("PT0S") == 0
        assert _parse_duration("invalid") == 0

    def test_generate_insights(self):
        """Test insight generation"""
        mock_videos = [
            {
                "title": "Top Video",
                "views": 100000,
                "likes": 5000,
                "duration": "PT10M",
                "channel": "Popular Channel"
            },
            {
                "title": "Second Video", 
                "views": 50000,
                "likes": 2000,
                "duration": "PT5M",
                "channel": "Another Channel"
            }
        ]
        
        mock_keywords = [("python", 5), ("tutorial", 3)]
        mock_channels = [("Popular Channel", {"video_count": 1, "total_views": 100000})]
        
        insights = _generate_insights(mock_videos, mock_keywords, mock_channels, "python tutorial")
        
        assert len(insights) > 0
        assert any("Top Video" in insight for insight in insights)
        assert any("Popular Channel" in insight for insight in insights)
        assert any("python" in insight for insight in insights)

    def test_generate_insights_empty_data(self):
        """Test insight generation with empty data"""
        insights = _generate_insights([], [], [], "test")
        
        assert len(insights) == 1
        assert "No videos available" in insights[0]

    def test_api_error_handling(self, httpx_mock):
        """Test API error handling"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            # Test HTTP error
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/search",
                status_code=500
            )
            
            result = search_youtube_videos("test query")
            
            assert "error" in result
            assert "YouTube API error" in result["error"]

    def test_analysis_report_structure(self, httpx_mock, mock_search_response, mock_video_details_response):
        """Test analysis report structure completeness"""
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": "test_api_key"}):
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/search",
                json=mock_search_response
            )
            
            httpx_mock.add_response(
                method="GET",
                url="https://www.googleapis.com/youtube/v3/videos",
                json=mock_video_details_response
            )
            
            result = analyze_youtube_videos("test query")
            
            # Check all required fields are present
            required_fields = [
                "query", "analysis_date", "total_videos_analyzed",
                "metrics", "top_keywords", "top_channels", 
                "video_summaries", "insights"
            ]
            
            for field in required_fields:
                assert field in result, f"Missing field: {field}"
            
            # Check metrics structure
            metrics_fields = [
                "total_views", "total_likes", "total_comments",
                "average_views", "average_likes", "average_comments",
                "average_duration_minutes"
            ]
            
            for field in metrics_fields:
                assert field in result["metrics"], f"Missing metrics field: {field}"
            
            # Check video summary structure
            if result["video_summaries"]:
                video_fields = [
                    "title", "channel", "published", "views", 
                    "likes", "comments", "duration", "url", "description_preview"
                ]
                
                for field in video_fields:
                    assert field in result["video_summaries"][0], f"Missing video field: {field}"