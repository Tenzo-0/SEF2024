import librosa
import os
import json
import numpy as np

def extract_audio_features(audio_path):
    """Extract audio features such as duration and bpm."""
    y, sr = librosa.load(audio_path, sr=None)
    
    # Duration in seconds (convert to float)
    duration = float(librosa.get_duration(y=y, sr=sr))
    
    # Extract tempo (bpm)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    
    # Set default values for bpm if not available (convert to float)
    if isinstance(tempo, np.ndarray):
        tempo = float(tempo[0]) if len(tempo) > 0 else "unknown"
    elif isinstance(tempo, (float, int)):
        tempo = float(tempo)
    else:
        tempo = "unknown"
    
    return duration, tempo, sr

def generate_dataset_entry(audio_file, audio_path):
    """Generate a dataset entry based on audio file metadata."""
    # Extract audio features
    duration, tempo, sample_rate = extract_audio_features(audio_path)
    
    # Define the genre (this can be customized or made dynamic)
    genre = "cai luong, "  # Set a default genre or customize as needed
    
    # Generate textual description
    description = f"A {duration:.1f} seconds long {tempo} BPM {genre} song with uplifting and motivational moods."
    
    # Define the entry metadata
    entry = {
        "key": "",
        "artist": "",  # Customize or automate this field if needed
        "sample_rate": sample_rate,
        "file_extension": "mp3",
        "description": description,
        "keywords": "bright, pulsing, cool",  # Customize or automate this field if needed
        "duration": duration,
        "bpm": tempo,
        "genre": genre,  # Now genre is defined
        "title": audio_file.split('.')[0],  # Use the filename as the title by default
        "name": audio_file.split('.')[0],   # Use the filename as the name by default
        "instrument": "Mix",  # Customize or automate this field
        "moods": ["uplifting", "motivational"]  # Customize or automate this field
    }
    
    return entry

def process_dataset(audio_dir):
    """Process all audio files in the directory and generate JSON entries."""
    dataset = []

    # Process each audio file
    for audio_file in os.listdir(audio_dir):
        if audio_file.endswith(".wav") or audio_file.endswith(".mp3"):
            audio_path = os.path.join(audio_dir, audio_file)
            entry = generate_dataset_entry(audio_file, audio_path)
            dataset.append(entry)
    
    return dataset

def save_to_json(dataset, output_file):
    """Save the dataset to a JSON file."""
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=4)

if __name__ == "__main__":
    audio_directory = "/home/user"  # Replace with your audio dataset path
    output_json = "musicgen_dataset.json"

    # Generate the dataset
    dataset = process_dataset(audio_directory)

    # Save the dataset to JSON
    save_to_json(dataset, output_json)
    print(f"Dataset saved to {output_json}")
