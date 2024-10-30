from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.effects import normalize
import os
from multiprocessing import Pool, cpu_count

def process_audio_file(args):
    """Process a single audio file."""
    file_path, output_directory = args
    audio = AudioSegment.from_file(file_path)

    # Process the audio to reduce silences
    processed_audio = shorten_silences(audio)

    # Enhance audio quality
    enhanced_audio = enhance_audio_quality(processed_audio)

    # Define the output path, keeping the same filename in the output directory
    output_path = os.path.join(output_directory, "processed_" + os.path.basename(file_path))

    # Save the enhanced audio with lower bitrate for faster encoding
    enhanced_audio.export(output_path, format="mp3", bitrate="128k")
    return f"Enhanced audio saved successfully to {output_path}"

def shorten_silences(audio_segment, silence_thresh=-40, min_silence_len=1000, desired_silence_len=3000):
    chunks = split_on_silence(audio_segment, min_silence_len=min_silence_len, silence_thresh=silence_thresh, keep_silence=desired_silence_len)
    if not chunks:
        print("No silent segments detected, returning original audio segment.")
        return audio_segment
    processed_segment = chunks[0]
    for chunk in chunks[1:]:
        processed_segment += AudioSegment.silent(duration=desired_silence_len) + chunk
    return processed_segment

def enhance_audio_quality(audio_segment):
    return normalize(audio_segment)

def process_audio_files(input_directory, output_directory):
    """
    Process all MP3 files in the given input directory to reduce silences, 
    enhance audio quality, and save them in the output directory.
    """
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # Create a list of tuples (file_path, output_directory) for multiprocessing
    files = [(os.path.join(input_directory, f), output_directory) 
             for f in os.listdir(input_directory) if f.endswith('.mp3')]
    
    # Use a multiprocessing pool with the CPU count for efficiency
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(process_audio_file, files)
    
    # Print out the results for each processed file
    for result in results:
        print(result)

# Specify the input and output directories
input_directory = "/home/user/aaa"
output_directory = "/home/user/output"
process_audio_files(input_directory, output_directory)
