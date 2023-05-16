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


def get_audio(url:str) -> str:
    """Get .wav file from given url
    Args:
        url (str): Path to youtube link.
    Returns:
        str: Path to full audio data.
    """

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


def get_transcript(url:str, lang:str) -> tuple(list, bool):
    """Get transcript using video id from given url
    Args:
        url (str): Path to youtube link.
        lang (str): Designated language for transcript.
    Returns:
        tuple(list, bool): Tuple consists of full transcription and handcrafted flag.
    """

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


def make_chunks(a_path:str, t_result:tuple(list, bool), d_path:str):
    """Divide raw data into multiple chunks and save them into csv format
    Args:
        a_path (str): Path returned from get_audio() method.
        t_result (tuple): Tuple returned from get_transcript() method.
        d_path (str): Path to destination.
    """

    transcript, generated = t_result
    df = pd.DataFrame()

    for i, chunk in tqdm(enumerate(transcript)):
        t1 = chunk['start'] * 1000                      # works in milliseconds
        t2 = t1 + chunk['duration'] * 1000
        new_aud = AudioSegment.from_wav(a_path)
        new_aud = new_aud[t1:t2]
        new_path = f'{a_path}_{i}'
        new_aud.export(new_path, format="wav")          # exports to a wav file in the current path.

        df['audio'] = new_path
        df['text'] = chunk['text']
    
    df['handcrafted'] = not generated

    if os.path.isfile(d_path):               # Updata data file if it exists
        data = pd.read_csv(d_path)
        data = pd.concat([data, df])
        data.to_csv(d_path)
    else:                                       # Make data file if it doesn't exist
        os.makedirs(d_path)
        df.to_csv(d_path)
    pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, default='sw_test_nonfreeze')    # Project name for wandb
    parser.add_argument('--language', type=str, default='en')    # Project name for wandb
    parser.add_argument('--data_path', type=str, default='./Data/data.csv')
    args = parser.parse_args()
    url  = args.url
    lang = args.language
    d_path = args.data_path

    if not isinstance(url, (str, list)):
        raise TypeError("Wrong url type is given. Try str for single url or list for multiple instead.")

    a_path = get_audio(url)
    t_result = get_transcript(url, lang)
    make_chunks(a_path, t_result, d_path)
