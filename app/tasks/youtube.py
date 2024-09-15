# app/tasks/youtube.py
from kafka import KafkaProducer
import json
from services.youtube_service import YouTubeService

producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def monitor_new_videos():
    youtube_service = YouTubeService()
    new_videos = youtube_service.get_latest_videos()
    for video in new_videos:
        producer.send('new_videos', video)
        print(f"Published video: {video['title']} to Kafka")
