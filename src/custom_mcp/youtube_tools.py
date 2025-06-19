"""YouTube Data API v3 integration tools for video analysis"""

import os
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import httpx


def search_youtube_videos(
    query: str, 
    max_results: int = 10, 
    order: str = "relevance",
    published_after: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for YouTube videos using the YouTube Data API v3
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (1-50)
        order: Order of results (relevance, date, rating, viewCount, title)
        published_after: RFC 3339 formatted date-time (e.g., '2023-01-01T00:00:00Z')
    
    Returns:
        Dictionary containing search results or error message
    """
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    if not youtube_api_key:
        return {"error": "YouTube API key is required"}
    
    # Validate parameters
    if max_results < 1 or max_results > 50:
        max_results = 10
    
    valid_orders = ["relevance", "date", "rating", "viewCount", "title"]
    if order not in valid_orders:
        order = "relevance"
    
    # Build API request
    base_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": youtube_api_key,
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": order
    }
    
    if published_after:
        params["publishedAfter"] = published_after
    
    try:
        with httpx.Client() as client:
            response = client.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {"error": f"YouTube API error: {e}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


def get_video_details(video_ids: List[str]) -> Dict[str, Any]:
    """
    Get detailed information about YouTube videos
    
    Args:
        video_ids: List of video IDs to get details for
    
    Returns:
        Dictionary containing video details or error message
    """
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    if not youtube_api_key:
        return {"error": "YouTube API key is required"}
    
    if not video_ids:
        return {"error": "At least one video ID is required"}
    
    # Limit to 50 videos per request (API limit)
    if len(video_ids) > 50:
        video_ids = video_ids[:50]
    
    base_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "key": youtube_api_key,
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(video_ids)
    }
    
    try:
        with httpx.Client() as client:
            response = client.get(base_url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {"error": f"YouTube API error: {e}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


def analyze_youtube_videos(query: str, max_results: int = 10, order: str = "viewCount") -> Dict[str, Any]:
    """
    Search for YouTube videos and provide comprehensive analysis
    
    Args:
        query: Search query string
        max_results: Maximum number of results to analyze (1-50)
        order: Order of results (relevance, date, rating, viewCount, title)
    
    Returns:
        Dictionary containing analysis report
    """
    # Step 1: Search for videos
    search_results = search_youtube_videos(query, max_results, order)
    
    if "error" in search_results:
        return search_results
    
    if "items" not in search_results or not search_results["items"]:
        return {"error": "No videos found for the given query"}
    
    # Step 2: Extract video IDs
    video_ids = [item["id"]["videoId"] for item in search_results["items"]]
    
    # Step 3: Get detailed video information
    video_details = get_video_details(video_ids)
    
    if "error" in video_details:
        return video_details
    
    # Step 4: Analyze the data
    analysis = _generate_analysis_report(search_results, video_details, query)
    
    return analysis


def _generate_analysis_report(search_results: Dict, video_details: Dict, query: str) -> Dict[str, Any]:
    """Generate comprehensive analysis report from YouTube data"""
    
    videos = video_details.get("items", [])
    total_videos = len(videos)
    
    if total_videos == 0:
        return {"error": "No video details available for analysis"}
    
    # Initialize analysis metrics
    total_views = 0
    total_likes = 0
    total_comments = 0
    total_duration_seconds = 0
    channels = {}
    keywords = {}
    categories = {}
    publish_dates = []
    
    # Process each video
    for video in videos:
        snippet = video.get("snippet", {})
        statistics = video.get("statistics", {})
        content_details = video.get("contentDetails", {})
        
        # Extract metrics
        views = int(statistics.get("viewCount", 0))
        likes = int(statistics.get("likeCount", 0))
        comments = int(statistics.get("commentCount", 0))
        
        total_views += views
        total_likes += likes
        total_comments += comments
        
        # Parse duration (ISO 8601 format: PT#M#S)
        duration = content_details.get("duration", "PT0S")
        duration_seconds = _parse_duration(duration)
        total_duration_seconds += duration_seconds
        
        # Channel analysis
        channel_title = snippet.get("channelTitle", "Unknown")
        if channel_title in channels:
            channels[channel_title]["count"] += 1
            channels[channel_title]["total_views"] += views
        else:
            channels[channel_title] = {"count": 1, "total_views": views}
        
        # Keyword analysis from title and description
        title = snippet.get("title", "")
        description = snippet.get("description", "")
        text_content = f"{title} {description}".lower()
        
        # Extract keywords (simple word frequency)
        words = re.findall(r'\b\w+\b', text_content)
        for word in words:
            if len(word) > 3:  # Filter out short words
                keywords[word] = keywords.get(word, 0) + 1
        
        # Parse publish date
        published_at = snippet.get("publishedAt")
        if published_at:
            publish_dates.append(published_at)
    
    # Calculate averages
    avg_views = total_views / total_videos if total_videos > 0 else 0
    avg_likes = total_likes / total_videos if total_videos > 0 else 0
    avg_comments = total_comments / total_videos if total_videos > 0 else 0
    avg_duration = total_duration_seconds / total_videos if total_videos > 0 else 0
    
    # Get top performers
    top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
    top_channels = sorted(channels.items(), key=lambda x: x[1]["total_views"], reverse=True)[:5]
    
    # Create detailed video list
    video_summaries = []
    for video in videos:
        snippet = video.get("snippet", {})
        statistics = video.get("statistics", {})
        content_details = video.get("contentDetails", {})
        
        video_summary = {
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published": snippet.get("publishedAt", ""),
            "views": int(statistics.get("viewCount", 0)),
            "likes": int(statistics.get("likeCount", 0)),
            "comments": int(statistics.get("commentCount", 0)),
            "duration": content_details.get("duration", ""),
            "url": f"https://www.youtube.com/watch?v={video.get('id', '')}",
            "description_preview": snippet.get("description", "")[:200] + "..." if len(snippet.get("description", "")) > 200 else snippet.get("description", "")
        }
        video_summaries.append(video_summary)
    
    # Sort videos by views
    video_summaries.sort(key=lambda x: x["views"], reverse=True)
    
    # Generate analysis report
    analysis_report = {
        "query": query,
        "analysis_date": datetime.now().isoformat(),
        "total_videos_analyzed": total_videos,
        "metrics": {
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "average_views": round(avg_views, 2),
            "average_likes": round(avg_likes, 2),
            "average_comments": round(avg_comments, 2),
            "average_duration_minutes": round(avg_duration / 60, 2)
        },
        "top_keywords": [{"word": word, "frequency": freq} for word, freq in top_keywords],
        "top_channels": [
            {
                "channel": channel, 
                "video_count": data["count"], 
                "total_views": data["total_views"]
            } for channel, data in top_channels
        ],
        "video_summaries": video_summaries,
        "insights": _generate_insights(video_summaries, top_keywords, [
            {
                "channel": channel, 
                "video_count": data["count"], 
                "total_views": data["total_views"]
            } for channel, data in top_channels
        ], query)
    }
    
    return analysis_report


def _parse_duration(duration_str: str) -> int:
    """Parse YouTube duration format (PT#H#M#S) to seconds"""
    if not duration_str.startswith("PT"):
        return 0
    
    duration_str = duration_str[2:]  # Remove "PT"
    
    hours = 0
    minutes = 0
    seconds = 0
    
    # Parse hours
    if "H" in duration_str:
        hours_match = re.search(r'(\d+)H', duration_str)
        if hours_match:
            hours = int(hours_match.group(1))
    
    # Parse minutes
    if "M" in duration_str:
        minutes_match = re.search(r'(\d+)M', duration_str)
        if minutes_match:
            minutes = int(minutes_match.group(1))
    
    # Parse seconds
    if "S" in duration_str:
        seconds_match = re.search(r'(\d+)S', duration_str)
        if seconds_match:
            seconds = int(seconds_match.group(1))
    
    return hours * 3600 + minutes * 60 + seconds


def _generate_insights(videos: List[Dict], keywords: List[tuple], channels: List[tuple], query: str) -> List[str]:
    """Generate actionable insights from the analysis"""
    insights = []
    
    if not videos:
        return ["No videos available for insight generation."]
    
    # View count insights
    top_video = videos[0]
    insights.append(f"Most popular video: '{top_video['title']}' with {top_video['views']:,} views")
    
    # Channel insights
    if channels:
        top_channel = channels[0]
        channel_name = top_channel['channel']
        insights.append(f"Top performing channel: '{channel_name}' with {top_channel['video_count']} videos and {top_channel['total_views']:,} total views")
    
    # Keyword insights
    if keywords:
        top_keyword = keywords[0]
        insights.append(f"Most frequent keyword: '{top_keyword[0]}' appears {top_keyword[1]} times across video titles and descriptions")
    
    # Duration insights
    durations = [_parse_duration(v.get('duration', 'PT0S')) for v in videos]
    avg_duration = sum(durations) / len(durations) if durations else 0
    insights.append(f"Average video duration: {avg_duration/60:.1f} minutes")
    
    # Engagement insights
    total_views = sum(v['views'] for v in videos)
    total_likes = sum(v['likes'] for v in videos)
    if total_views > 0:
        engagement_rate = (total_likes / total_views) * 100
        insights.append(f"Overall engagement rate (likes/views): {engagement_rate:.2f}%")
    
    # Content strategy insights
    if len(videos) >= 3:
        view_ranges = {
            "high": [v for v in videos if v['views'] > 100000],
            "medium": [v for v in videos if 10000 <= v['views'] <= 100000],
            "low": [v for v in videos if v['views'] < 10000]
        }
        
        for range_name, range_videos in view_ranges.items():
            if range_videos:
                avg_duration = sum(_parse_duration(v.get('duration', 'PT0S')) for v in range_videos) / len(range_videos)
                insights.append(f"{range_name.capitalize()} performing videos (n={len(range_videos)}) average {avg_duration/60:.1f} minutes")
    
    return insights