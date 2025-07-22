"""Slack integration tools for bulk DM sending"""

import os
from typing import Any

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def send_slack_bulk_dm(user_ids: list[str], message: str) -> dict[str, Any]:
    """Send direct messages to multiple Slack users
    
    Args:
        user_ids: List of Slack user IDs to send messages to
        message: Message text to send
        
    Returns:
        Dictionary with success/failure results for each user
    """
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        return {"error": "SLACK_BOT_TOKEN environment variable is required"}

    if not user_ids:
        return {"error": "At least one user ID is required"}

    if not message:
        return {"error": "Message text is required"}

    client = WebClient(token=slack_token)

    results = {
        "successful_sends": [],
        "failed_sends": [],
        "total_users": len(user_ids),
        "success_count": 0,
        "failure_count": 0
    }

    for user_id in user_ids:
        try:
            # First, open a DM channel with the user
            dm_response = client.conversations_open(users=user_id)
            channel_id = dm_response["channel"]["id"]

            # Send the message
            message_response = client.chat_postMessage(
                channel=channel_id,
                text=message
            )

            results["successful_sends"].append({
                "user_id": user_id,
                "channel_id": channel_id,
                "timestamp": message_response["ts"]
            })
            results["success_count"] += 1

        except SlackApiError as e:
            results["failed_sends"].append({
                "user_id": user_id,
                "error": f"Slack API error: {e.response['error']}"
            })
            results["failure_count"] += 1
        except Exception as e:
            results["failed_sends"].append({
                "user_id": user_id,
                "error": f"Unexpected error: {e}"
            })
            results["failure_count"] += 1

    return results


def get_slack_users(limit: int = 100) -> dict[str, Any]:
    """Get list of Slack users
    
    Args:
        limit: Maximum number of users to retrieve (default: 100)
        
    Returns:
        Dictionary containing user list and metadata
    """
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        return {"error": "SLACK_BOT_TOKEN environment variable is required"}

    client = WebClient(token=slack_token)

    try:
        response = client.users_list(limit=min(limit, 1000))  # Slack API max is 1000

        users = []
        for member in response["members"]:
            # Filter out bots and deleted users
            if not member.get("deleted", False) and not member.get("is_bot", False):
                users.append({
                    "id": member["id"],
                    "name": member.get("name", ""),
                    "real_name": member.get("real_name", ""),
                    "display_name": member.get("profile", {}).get("display_name", ""),
                    "email": member.get("profile", {}).get("email", ""),
                    "is_admin": member.get("is_admin", False),
                    "is_owner": member.get("is_owner", False),
                    "tz": member.get("tz", "")
                })

        return {
            "users": users,
            "total_count": len(users),
            "has_more": response.get("response_metadata", {}).get("next_cursor", "") != ""
        }

    except SlackApiError as e:
        return {"error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}


def send_slack_channel_message(channel: str, message: str) -> dict[str, Any]:
    """Send a message to a Slack channel
    
    Args:
        channel: Channel ID or name (with # prefix)
        message: Message text to send
        
    Returns:
        Dictionary with message sending result
    """
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    if not slack_token:
        return {"error": "SLACK_BOT_TOKEN environment variable is required"}

    if not channel:
        return {"error": "Channel is required"}

    if not message:
        return {"error": "Message text is required"}

    client = WebClient(token=slack_token)

    try:
        response = client.chat_postMessage(
            channel=channel,
            text=message
        )

        return {
            "success": True,
            "channel": response["channel"],
            "timestamp": response["ts"],
            "message": response.get("message")
        }

    except SlackApiError as e:
        return {"error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        return {"error": f"An error occurred: {e}"}
