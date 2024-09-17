# app/services/download_service.py

import yt_dlp
import os
import re
import logging
from db.s3 import S3

class DownloadService:
    YOUTUBE_URL_REGEX = re.compile(r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')

    def __init__(self, download_path='downloads'):
        self.download_path = download_path
        self.s3 = S3()  # Initialize S3 service
        
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
                
                # Upload the file to S3/MinIO
                object_name = f"audio/{os.path.basename(audio_file)}"
                file_url = self.s3.upload_file(audio_file, object_name)
                
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                
                return file_url  # Return the file URL from S3/MinIO
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Failed to download audio: {e}")
            return None

    def consume_and_download(self, video_url):
        """Download videos based on URL input."""
        logging.info(f"Downloading video: {video_url}")
        if self.YOUTUBE_URL_REGEX.match(video_url):
            audio_url = self.download_audio(video_url)
            if audio_url:
                logging.info(f"Audio successfully downloaded and stored: {audio_url}")
            else:
                logging.error(f"Failed to download audio from URL: {video_url}")
        else:
            logging.error(f"Invalid video URL: {video_url}")
