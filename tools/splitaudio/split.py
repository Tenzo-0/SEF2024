import os
from multiprocessing import Pool
from pydub import AudioSegment

def split_audio_file(audio_file_info):
    input_folder, output_folder, audio_file, char_index_start = audio_file_info
    
    # Define characters for renaming files
    rename_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def get_next_name(index):
        name = ''
        while index >= 0:
            name = rename_chars[index % len(rename_chars)] + name
            index = index // len(rename_chars) - 1
        return name

    audio_path = os.path.join(input_folder, audio_file)
    audio = AudioSegment.from_file(audio_path)
    
    print(f"Processing file: {audio_file}")
    
    # Split audio into 30-second segments
    for i in range(0, len(audio), 30 * 1000):
        segment = audio[i:i + 30 * 1000]
        segment_name = get_next_name(char_index_start) + os.path.splitext(audio_file)[1]
        segment_path = os.path.join(output_folder, segment_name)
        segment.export(segment_path, format="mp3" if audio_file.endswith('.mp3') else "wav")
        
        print(f"Exported segment: {segment_name}")
        
        char_index_start += 1

def split_audio_files(input_folder, output_folder, num_processes=4):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Get all audio files in the input folder
    audio_files = [f for f in os.listdir(input_folder) if f.endswith('.mp3') or f.endswith('.wav')]

    # Prepare data for multiprocessing
    audio_file_infos = [(input_folder, output_folder, audio_file, idx * 100) for idx, audio_file in enumerate(audio_files)]
    
    # Use a pool of workers to process files in parallel
    with Pool(processes=num_processes) as pool:
        pool.map(split_audio_file, audio_file_infos)

# Example usage
split_audio_files('/home/user/output', '/home/user/dataset', num_processes=4)
