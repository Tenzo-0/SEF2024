from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.effects import normalize
import os
from multiprocessing import Pool, cpu_count

def enhance(audio):
    return normalize(audio)

def process_audio(info):
    input, output, audio, i = info
    audio_path = os.path.join(input, audio)
    audio_f = AudioSegment.from_file(audio_path)

    print(f"Processing file: {audio}")

    enhanced_audio = enhance(audio_f)
    splited_audios = split_on_silence(enhanced_audio, min_silence_len=3000, silence_thresh=-30)

    rename_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    def get_name(index):
        next_name = ''
        while index >= 0:
            next_name = rename_chars[index % len(rename_chars)] + next_name
            index = index // len(rename_chars) - 1
        return next_name

    for splited_audio in splited_audios:
        name = get_name(i) + os.path.splitext(audio)[1] 
        path = os.path.join(output, name)
        splited_audio.export(path, format="mp3", bitrate="128k")
        print(f"Exported segment: {name}")
        i += 1

def process_audios(input, output):
    os.makedirs(output, exist_ok=True)
    audio_files = [f for f in os.listdir(input) if f.endswith('.mp3') or f.endswith('.wav')]
    
    audio_file_infos = [(input, output, audio_file, idx * 100) for idx, audio_file in enumerate(audio_files)]
    
    with Pool(processes=cpu_count()) as pool:
        pool.map(process_audio, audio_file_infos)
    
    print("Finish")

input= "/home/tenzo/Desktop/test"
output= "/home/tenzo/Desktop/test"
process_audios(input, output)
