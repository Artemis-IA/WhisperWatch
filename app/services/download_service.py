# app/services/download_service.py
import yt_dlp
import os
import re
from services.kafka_manager import KafkaManager

class DownloadService:
    YOUTUBE_URL_REGEX = re.compile(r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')

    def __init__(self, download_path='downloads', kafka_topic='new_videos'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        # Initialize KafkaManager to consume video URLs
        self.kafka_manager = KafkaManager(kafka_topic)

    def download_audio(self, youtube_url):
        """Download only the audio from a YouTube video."""
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_path, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            audio_file = ydl.prepare_filename(info_dict)
            audio_file = os.path.splitext(audio_file)[0] + '.mp3'
            return audio_file

    def download_video(self, youtube_url):
        """Download the full video from YouTube."""
        ydl_opts = {
            'format': 'bestvideo+bestaudio',
            'outtmpl': os.path.join(self.download_path, '%(id)s.%(ext)s'),
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            video_file = ydl.prepare_filename(info_dict)
            return video_file

    def consume_and_download(self):
        """Consume messages from Kafka and download videos."""
        for message in self.kafka_manager.consume_messages():
            video_url = message.value.decode('utf-8')
            print(f"Downloading video: {video_url}")
            if self.YOUTUBE_URL_REGEX.match(video_url):
                self.download_video(video_url)
            else:
                print(f"Invalid video URL: {video_url}")
