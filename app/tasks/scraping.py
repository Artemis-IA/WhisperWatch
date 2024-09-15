# app/tasks/scraping.py
from kafka import KafkaConsumer
import json
from services.youtube_service import YouTubeService

consumer = KafkaConsumer('scrape_decisions',
                         bootstrap_servers='localhost:9092',
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))

def start_scraping():
    youtube_service = YouTubeService()
    new_videos = youtube_service.get_latest_videos()
    for video in new_videos:
        print(f"Scraping video: {video['title']}")

def listen_and_scrape():
    for message in consumer:
        decision = message.value
        if decision['action'] == 0:
            start_scraping()
        else:
            print("Skipping scraping based on RL agent's decision.")
