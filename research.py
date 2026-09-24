import json
import os
import requests


def load_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)


def search_youtube(api_key, topic, region="IN"):
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": topic,
        "type": "video",
        "order": "date",
        "regionCode": region,
        "maxResults": 10,
        "key": api_key
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json().get("items", [])


def main():
    config = load_config()

    api_key = os.environ.get("YOUTUBE_API_KEY")

    if not api_key:
        print("YouTube API key is not connected yet.")
        return

    topics = config["research"]["topics"]
    region = config["channel"]["region"]

    print("🔥 AI YouTube Studio")
    print("Starting trend research...\n")

    for topic in topics:
        print(f"\n===== {topic} =====")

        videos = search_youtube(
            api_key,
            topic,
            region
        )

        for video in videos:
            video_id = video["id"].get("videoId")

            if not video_id:
                continue

            title = video["snippet"]["title"]
            channel = video["snippet"]["channelTitle"]

            print(f"• {title}")
            print(f"  Channel: {channel}")
            print(
                f"  https://youtube.com/watch?v={video_id}"
            )


if __name__ == "__main__":
    main()
