import yt_dlp
#yt_dlp is a Python library used to download videos and audio from websites.

from pydub import AudioSegment 
#library for manipulating audio. Think of it as
# "OpenCV for audio."

import os

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url :str) ->str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
    return filename 


# This function standardizes the audio - because speech recognition models require a very specific WAV format.
def convert_to_wav(input_path: str)-> str:
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path) #detects file format, mp3, mp4, wav
    audio = audio.set_channels(1).set_frame_rate(16000) #monoaudio(1) + 16khz frequency
    audio.export(output_path, format='wav')
    return output_path


def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str)->list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected youtube url. downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. converting to wav...")
        wav_path = convert_to_wav(source)

    print("chunking audio...")
    chunks = chunk_audio(wav_path)
    return chunks



