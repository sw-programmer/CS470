from __future__ import unicode_literals
import os
import argparse
from tqdm import tqdm
import wave

import pandas as pd
import numpy as np
import pafy
from pydub import AudioSegment
import moviepy.editor as moviepy
import yt_dlp as youtube_dl
# import youtube_dl
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
        with youtube_dl.YoutubeDL({}) as ydl:                   # get metadata to designate output path
            meta = ydl.extract_info(url, download=False) 
        path = f"./Data/wav/{meta['title']}.{meta['format']}"

        ydl_opts = {                                            # get audio(.wav w/ 16kHz sampling rate) into designated output path
            'format': 'bestaudio/best',
            'outtmpl': path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav'
            }],
            'postprocessor_args': [
                '-ar', '16000'
            ]
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        path += '.wav'
        assert wave.open(path, "rb").getframerate() == 16000

    else:   #TODO
        pass

    return path


def get_transcript(url:str, lang:str) -> tuple((list, bool)):
    """Get transcript using video id from given url
    Args:
        url (str): Path to youtube link.
        lang (str): Designated language for transcript.
    Returns:
        tuple((list, bool)): Tuple consists of full transcription and handcrafted flag.
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


def make_chunks(a_path:str, t_result:tuple((list, bool)), d_path:str):
    """Divide raw data into multiple chunks and save them into csv format
    Args:
        a_path (str): Path returned from get_audio() method.
        t_result (tuple): Tuple returned from get_transcript() method.
        d_path (str): Path to destination.
    """
    transcript, generated = t_result
    d_list = []
    for chunk in tqdm(transcript):
        d_list.append([a_path, chunk['text'], chunk['start'], chunk['duration']])

    df = pd.DataFrame(d_list, columns =['audio', 'text', 'start', 'duration'])
    df['handcrafted'] = not generated
    df['handcrafted'] = df['handcrafted'].astype(int)

    if os.path.isfile(d_path):          # updata data file if it exists
        df_0 = pd.read_csv(d_path)
        df_0 = pd.concat([df_0, df])
        df_0.to_csv(d_path)
    else:                               # make data file if it doesn't exist
        df.to_csv(d_path)

    return


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, default='sw_test_nonfreeze')
    parser.add_argument('--language', type=str, default='en')               
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
