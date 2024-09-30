import os
from pydub import AudioSegment

def split_audio_files(input_folder, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Get all audio files in the input folder
    audio_files = [f for f in os.listdir(input_folder) if f.endswith('.mp3') or f.endswith('.wav')]
    
    # Characters for renaming files
    rename_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    char_index = 0

    def get_next_name(index):
        name = ''
        while index >= 0:
            name = rename_chars[index % len(rename_chars)] + name
            index = index // len(rename_chars) - 1
        return name

    for audio_file in audio_files:
        audio_path = os.path.join(input_folder, audio_file)
        audio = AudioSegment.from_file(audio_path)
        
        print(f"Processing file: {audio_file}")
        
        # Split audio into 1-minute segments
        for i in range(0, len(audio), 30 * 1000):
            segment = audio[i:i + 30 * 1000]
            segment_name = get_next_name(char_index) + os.path.splitext(audio_file)[1]
            segment_path = os.path.join(output_folder, segment_name)
            segment.export(segment_path, format="mp3" if audio_file.endswith('.mp3') else "wav")
            
            print(f"Exported segment: {segment_name}")
            
            char_index += 1

# Example usage
split_audio_files('/path/to/your/input_folder', '/path/to/your/output_folder')
