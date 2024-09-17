# app/services/download_service.py
import yt_dlp
import os
import re
import logging
import soundfile as sf

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

                # Vérifier que le fichier existe
                if not os.path.exists(audio_file):
                    raise Exception(f"Audio file not found after download: {audio_file}")
                
                # Vérifier si le fichier audio est valide
                try:
                    with sf.SoundFile(audio_file) as f:
                        logging.info(f"Audio file is valid with format {f.format}")
                except Exception as e:
                    raise Exception(f"Invalid audio file: {e}")

                return audio_file

        except yt_dlp.utils.DownloadError as e:
            logging.error(f"Failed to download audio: {e}")
            return None
        except Exception as e:
            logging.error(f"Error processing audio file: {e}")
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
