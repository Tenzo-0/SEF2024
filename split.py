import os
from pydub import AudioSegment

def generate_custom_filename(index):
    """
    Generate filenames like '00', '01', '0A', '0Z', '10', '1A', etc.
    Uses base-36 encoding to generate filenames.
    """
    char_map = [str(i) for i in range(10)] + [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    first_char = char_map[index // len(char_map)]  # Calculate first character
    second_char = char_map[index % len(char_map)]  # Calculate second character
    return first_char + second_char

def split_audio_files(input_folder_path, output_folder_path, segment_length_ms=60000):  # Default to 60000ms which is 1 minute
    # Ensure the input folder exists
    if not os.path.exists(input_folder_path):
        print("Input folder does not exist.")
        return

    # Ensure the output folder exists, if not create it
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
        print(f"Created output folder at {output_folder_path}")

    # Process each file in the input directory
    for filename in os.listdir(input_folder_path):
        if filename.endswith(".mp3") or filename.endswith(".wav"):  # Check for audio files
            file_path = os.path.join(input_folder_path, filename)
            audio = AudioSegment.from_file(file_path)

            # Calculate the number of segments
            duration = len(audio)
            num_segments = (duration // segment_length_ms) + (1 if duration % segment_length_ms else 0)

            # Split and export each segment
            for i in range(num_segments):
                start_time = i * segment_length_ms
                end_time = min((i + 1) * segment_length_ms, duration)
                segment = audio[start_time:end_time]

                # Generate the custom filename like '00', '01', '0A', '0Z'
                segment_filename = generate_custom_filename(i) + ".mp3"
                segment_path = os.path.join(output_folder_path, segment_filename)

                # Export the segment as MP3
                segment.export(segment_path, format="mp3")
                print(f"Exported {segment_path}")

            # Optionally delete the original file to save space, uncomment the next line if needed
            # os.remove(file_path)

if __name__ == "__main__":
    input_directory = "/home/user/SEF-2024-2025/dataset"  # Change this to your input directory
    output_directory = "/home/user/output"  # Change this to your output directory
    split_audio_files(input_directory, output_directory)
