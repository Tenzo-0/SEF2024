import os
import json
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
from slicer2 import Slicer
from multiprocessing import Pool, cpu_count

def process_audio(info):
    dir, out, file_name_base, totall = info
    no_vocals_path = os.path.join(dir, "no_vocals", f"{file_name_base}_no_vocals.mp3")
    vocals_path = os.path.join(dir, "vocals", f"{file_name_base}_vocals.mp3")

    # Skip if the file doesn't exist
    if not os.path.exists(no_vocals_path) or not os.path.exists(vocals_path):
        print(f"Skipping {file_name_base} because some file doesn't exist.")
        return  # Skip the rest of the function for this file
    
    # Load audio using librosa (because Slicer expects numpy arrays)
    no_vocals_f, sr = librosa.load(no_vocals_path, sr=None, mono=False)
    vocals_f = AudioSegment.from_file(vocals_path)
    
    # Process the enhanced audio
    print(f"Processing file: {file_name_base}")
    
    # Initialize Slicer (Use the sample rate from librosa)
    slicer = Slicer(
        sr=sr,
        threshold=-50,       # You can adjust threshold as needed
        min_length=15000,     # Minimum length of the slices in ms
        min_interval=10000,   # Minimum interval between slices in ms
        hop_size=10,          # The frame length in ms
        max_sil_kept=10       # Max silence length kept in ms
    )

    # Use slicer to slice the enhanced no vocals audio
    slices = slicer.slice(no_vocals_f)
    
    for i, (slicee, start_sample, end_sample) in enumerate(slices):
        name_no_vocals = f"[{i}]_{file_name_base}_no_vocals.mp3"
        name_vocals = f"[{i}]_{file_name_base}_vocals.mp3"
        
        path_no_vocals = os.path.join(out, "no_vocals", name_no_vocals)
        path_vocals = os.path.join(out, "vocals", name_vocals)

        if len(slicee.shape) > 1:
            slicee = slicee.T  # reshape to (samples, channels)
            channels = slicee.shape[1]
        else:
            channels = 1

        # Convert float32 audio in [-1, 1] to int16 PCM data.
        slicee_int16 = (np.clip(slicee, -1.0, 1.0) * 32767).astype(np.int16)

        # Create a pydub AudioSegment from the raw PCM data.
        audio_segment = AudioSegment(
            data=slicee_int16.tobytes(),
            sample_width=slicee_int16.dtype.itemsize,
            frame_rate=sr,
            channels=channels
        )
        # Export using MP3 with a bitrate of 320k
        audio_segment.export(path_no_vocals, format='mp3', bitrate="320k") 
        vocals_f[start_sample / sr * 1000: end_sample / sr * 1000].export(path_vocals, format='mp3', bitrate="320k")

    print(f'Exported: {file_name_base}')
    
    os.remove(no_vocals_path)
    os.remove(vocals_path)


def read_from_json(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data

def process_audios(dir, out):
    os.makedirs(out, exist_ok=True)
    os.makedirs(os.path.join(out, "no_vocals"), exist_ok=True)
    os.makedirs(os.path.join(out, "vocals"), exist_ok=True)
    
    files = read_from_json(os.path.join(dir, "d1.json"))
    audio_file_infos = [(dir, out, file, 1) for file in files]
    
    with Pool(processes=15) as pool:
        pool.map(process_audio, audio_file_infos)
    
    print("Finish")

directory = "/home/user/d2"
out = "/home/user/process"
process_audios(directory, out)
