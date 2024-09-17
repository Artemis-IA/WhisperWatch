# app/services/download_service.py
import yt_dlp
import os
import re
import logging
from apscheduler.schedulers.background import BackgroundScheduler

class DownloadService:
    YOUTUBE_URL_REGEX = re.compile(r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')

    def __init__(self, download_path='downloads', kafka_topic='new_videos'):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)


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
            'PROXY': 'http://localhost:3128'

        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                audio_file = ydl.prepare_filename(info_dict)
                audio_file = os.path.splitext(audio_file)[0] + '.mp3'
                return audio_file
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Failed to download video: {e}")
            return None

    def consume_and_download(self, video_url):
        """Download videos based on URL input."""
        logging.info(f"Downloading video: {video_url}")
        if self.YOUTUBE_URL_REGEX.match(video_url):
            self.download_video(video_url)
        else:
            logging.error(f"Invalid video URL: {video_url}")
