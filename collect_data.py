from __future__ import unicode_literals
import os
import argparse
from tqdm import tqdm

import pandas as pd
import numpy as np
import pafy
from pydub import AudioSegment
import moviepy.editor as moviepy
import yt_dlp as youtube_dl
from scipy.io.wavfile import read as read_wav
from youtube_transcript_api import YouTubeTranscriptApi

#### get .wav file from given url ####
def get_audio(url):
    if isinstance(url, str):
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '16',                                               # convert video into mp3 file w/ 16kHz bitrate.
            }],
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        path = f'./Data/wav/{vid.title}'
        assert not os.path.isfile(path), "Given url is already converted into audio."   # raise error if file already exists

        # rate = aud.rawbitrate
        # assert rate >= 16000, "Sampling rate for given audio is not sufficient."        # raise error if sampling rate is below 16kHz

        #TODO: 이게 되는지 확인 -> 안되면 aud를 webm로 저장 이후 파일 경로 사용 후 바로 삭제
        aud_seg = AudioSegment.from_file(aud)
        aud_seg.export(path, format='wav')

    #TODO: url list 로 주어질 경우 고려 필요
    else:           
        pass

    print(f"Audio for {vid.title} is successfully downloaded w/ rate : {rate}, size : {aud.get_filesize()}")
    return path

#### get transcript using video id from given url ####
def get_transcript(url, lang):
    if isinstance(url, str):
        id = url.split('/')[-1]
        transcript_list = YouTubeTranscriptApi.list_transcripts(id)
        try:
            transcript = transcript_list.find_manually_created_transcript([lang])
        except:
            transcript = transcript_list.find_generated_transcript([lang])
    else:
        ids = [i.split('/')[-1] for i in url]
        transcript = YouTubeTranscriptApi.get_transcript(ids, languages=[lang])
        #TODO
        pass

    return transcript.fetch(), transcript.is_generated             # is_generated : True if it has been generated automatically or False otherwise (manually created).
    

#### divide raw data into multiple chunks and save them into csv format ####
def make_chunks(path, transcript):
    
    # Save them into csv file (update file it already exists)
    pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, default='sw_test_nonfreeze')    # Project name for wandb
    parser.add_argument('--language', type=str, default='en')    # Project name for wandb
    args = parser.parse_args()
    url  = args.url
    lang = args.language

    if not isinstance(url, (str, list)):
        raise TypeError("Wrong url type is given. Try str for single url or list for multiple instead.")

    aud_path = get_audio(url)
    transcript, generated = get_transcript(url, lang)
    make_chunks(aud_path, transcript)
    