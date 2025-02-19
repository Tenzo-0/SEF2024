import os
import json
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
from slicer2 import Slicer
from multiprocessing import Pool, cpu_count

countt = 0  # Global variable to count the processed files

def process_audio(info):
    global countt  # Use the global countt variable
    dir, file_name_base, i, totall = info
    no_vocals_path = os.path.join(dir, "no_vocals", f"{file_name_base}_no_vocals.mp3")

    # Skip if the file doesn't exist
    if not os.path.exists(no_vocals_path):
        print(f"Skipping {file_name_base} because the file doesn't exist.")
        countt += 1  # Increment the global file counter to reflect progress
        return  # Skip the rest of the function for this file
    
    # Load audio using librosa (because Slicer expects numpy arrays)
    no_vocals_f, sr = librosa.load(no_vocals_path, sr=None, mono=False)
    
    # Process the enhanced audio
    print(f"Processing file: {file_name_base}")
    
    # Initialize Slicer (Use the sample rate from librosa)
    slicer = Slicer(
        sr=sr,
        threshold=-50,  # You can adjust threshold as needed
        min_length=15000,  # Minimum length of the slices in ms
        min_interval=10000,  # Minimum interval between slices in ms
        hop_size=10,  # The frame length in ms
        max_sil_kept=10  # Max silence length kept in ms
    )

    # Use slicer to slice the enhanced no vocals audio
    slices = slicer.slice(no_vocals_f)

    rename_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    def get_name(index):
        next_name = ''
        while index >= 0:
            next_name = rename_chars[index % len(rename_chars)] + next_name
            index = index // len(rename_chars) - 1
        return next_name

    for slicee in slices:
        name_no_vocals = f"[{get_name(i)}]_" + f"{file_name_base}_no_vocals.mp3"
        path_no_vocals = os.path.join(dir, "no_vocals", name_no_vocals)

        no_vocals_segment = AudioSegment(
            slicee.tobytes(), frame_rate=sr, sample_width=slicee.dtype.itemsize, channels=1
        )
        no_vocals_segment.export(path_no_vocals, format="mp3", bitrate="320k") 
        i += 1  # Increment the index, though it's not strictly necessary here
    
    countt += 1  # Increment the global file counter
    print(f"Processed {countt}/{totall} files")

    os.remove(no_vocals_path)


def read_from_json(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data

def process_audios(dir):
    files = read_from_json(os.path.join(dir, "d2.json"))
    print("total: ", len(files))
    audio_file_infos = [(dir, file, idx * 10, len(files)) for idx, file in enumerate(files)]
    
    with Pool(processes=cpu_count()) as pool:
        pool.map(process_audio, audio_file_infos)
    
    print("Finish")

directory = "/home/user/d2"
process_audios(directory)
