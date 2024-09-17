# app/services/download_service.py
import yt_dlp
import os
import re
import logging

class DownloadService:
    YOUTUBE_URL_REGEX = re.compile(r'^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+$')

    def __init__(self, download_path='downloads'):
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
            logging.error(f"Failed to download audio: {e}")
            return None

    def download_video(self, youtube_url):
        """Download the full video from YouTube."""
        ydl_opts = {
            'format': 'bestvideo+bestaudio',
            'outtmpl': os.path.join(self.download_path, '%(id)s.%(ext)s'),
            'quiet': True,
            'PROXY': 'http://localhost:3128'
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(youtube_url, download=True)
                video_file = ydl.prepare_filename(info_dict)
                return video_file
        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Failed to download video: {e}")
            return None

    def consume_and_download(self, video_url):
        """Download videos based on URL input."""
        logging.info(f"Downloading video: {video_url}")
        if self.YOUTUBE_URL_REGEX.match(video_url):
            video_file = self.download_video(video_url)
            if video_file:
                logging.info(f"Video downloaded successfully: {video_file}")
            else:
                logging.error(f"Failed to download video from URL: {video_url}")
        else:
            logging.error(f"Invalid video URL: {video_url}")
