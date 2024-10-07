from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.effects import normalize
import os

def shorten_silences(audio_segment, silence_thresh=-40, min_silence_len=1000, desired_silence_len=3000):
    chunks = split_on_silence(audio_segment,
                              min_silence_len=min_silence_len,
                              silence_thresh=silence_thresh,
                              keep_silence=desired_silence_len)
    processed_segment = chunks[0]
    for chunk in chunks[1:]:
        processed_segment += AudioSegment.silent(duration=desired_silence_len) + chunk
    return processed_segment

def enhance_audio_quality(audio_segment):
    normalized_audio = normalize(audio_segment)
    return normalized_audio

def process_audio_files(directory):
    """
    Process all MP3 files in the given directory to reduce silences and enhance audio quality.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".mp3"):
            file_path = os.path.join(directory, filename)
            audio = AudioSegment.from_file(file_path)

            # Process the audio to reduce silences to 3 seconds
            processed_audio = shorten_silences(audio)

            # Enhance audio quality
            enhanced_audio = enhance_audio_quality(processed_audio)

            # Define the output path
            output_path = os.path.join(directory, "p_" + filename)
            
            # Save the enhanced audio
            enhanced_audio.export(output_path, format="mp3")
            print(f"Enhanced audio saved successfully to {output_path}")

# Specify the directory containing your audio files
audio_directory = "/home/user/home/user/output"
process_audio_files(audio_directory)
