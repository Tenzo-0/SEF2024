import os
from pydub import AudioSegment

def split_audio_files(folder_path, segment_length_ms=60000):  # Default to 60000ms which is 1 minute
    char_map = [str(i) for i in range(10)] + [chr(i) for i in range(ord('A'), ord('Z') + 1)]

    # Ensure the folder exists
    if not os.path.exists(folder_path):
        print("Folder does not exist.")
        return

    # Process each file in the directory
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3") or filename.endswith(".wav"):  # Check for audio files
            file_path = os.path.join(folder_path, filename)
            audio = AudioSegment.from_file(file_path)

            # Calculate the number of segments
            duration = len(audio)
            num_segments = (duration // segment_length_ms) + (1 if duration % segment_length_ms else 0)

            # Split and export each segment
            for i in range(num_segments):
                start_time = i * segment_length_ms
                end_time = min((i + 1) * segment_length_ms, duration)
                segment = audio[start_time:end_time]

                segment_filename = f"{char_map[i % len(char_map)]}.wav"  # Wrap around if more than 36 segments
                segment_path = os.path.join(folder_path, segment_filename)
                segment.export(segment_path, format="wav")
                print(f"Exported {segment_path}")

            # Optionally delete the original file to save space, uncomment the next line if needed
            # os.remove(file_path)

if __name__ == "__main__":
    directory = "/path/to/your/audio/folder"  # Change this to your directory
    split_audio_files(directory)
