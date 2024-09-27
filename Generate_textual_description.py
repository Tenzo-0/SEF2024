import librosa
import os
import json
import numpy as np
from scipy.special import softmax
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs, TensorflowPredict2D

# Function to extract audio features
def extract_audio_features(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    duration = float(librosa.get_duration(y=y, sr=sr))
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return duration, tempo, sr

# Function to generate dataset entry
def generate_dataset_entry(audio_file, audio_path, moods, keywords):
    duration, tempo, sample_rate = extract_audio_features(audio_path)
    mood_list = ', '.join(moods)
    keywords += ["Cai Luong", "Don ca tai tu", "Vietnamese Northside traditional music"]  # Added keywords
    description = f"A {duration:.1f} seconds long song at {tempo} BPM with moods like {mood_list}."
    entry = {
        "key": "",
        "artist": "",
        "sample_rate": sample_rate,
        "file_extension": audio_file.split('.')[-1],
        "description": description,
        "keywords": ', '.join(keywords),
        "duration": duration,
        "bpm": tempo,
        "genre": "Cai Luong",
        "title": audio_file.split('.')[0],
        "name": audio_file.split('.')[0],
        "instrument": "Mix",
        "moods": moods
    }
    return entry

# Function to save dataset to JSON
def save_to_json(entry, output_filename):
    with open(output_filename, 'w') as f:
        json.dump(entry, f, indent=4)

# Function to extract embeddings using a trained model
def extract_embeddings(audio_path):
    try:
        audio = MonoLoader(filename=audio_path, sampleRate=16000, resampleQuality=4)()
        if audio.size == 0:
            print(f"Warning: Audio file {audio_path} is empty. Deleting the file.")
            os.remove(audio_path)
            return []
        
        embedding_model = TensorflowPredictEffnetDiscogs(graphFilename="discogs-effnet-bs64-1.pb", output="PartitionedCall:1")
        embeddings = embedding_model(audio)
        return np.array(embeddings) if isinstance(embeddings, list) else embeddings
    except RuntimeError as e:
        print(f"Error processing {audio_path}: {e}")
        return []

# Function to predict moods using embeddings
def predict_moods(embeddings):
    if len(embeddings) == 0 or (isinstance(embeddings, np.ndarray) and embeddings.size == 0):
        print("Warning: No embeddings provided for mood prediction.")
        return []
    model = TensorflowPredict2D(graphFilename="mtg_jamendo_moodtheme-discogs-effnet-1.pb")
    predictions = model(embeddings)
    probabilities = softmax(predictions, axis=1)[0]
    return probabilities

# Function to get top 5 moods from predictions
def get_top_moods(probabilities):
    labels = [
        "action", "adventure", "advertising", "background", "ballad", "calm", "children", "christmas", "commercial",
        "cool", "corporate", "dark", "deep", "documentary", "drama", "dramatic", "dream", "emotional", "energetic",
        "epic", "fast", "film", "fun", "funny", "game", "groovy", "happy", "heavy", "holiday", "hopeful", "inspiring",
        "love", "meditative", "melancholic", "melodic", "motivational", "movie", "nature", "party", "positive",
        "powerful", "relaxing", "retro", "romantic", "sad", "sexy", "slow", "soft", "soundscape", "space", "sport",
        "summer", "trailer", "travel", "upbeat", "uplifting"
    ]
    label_probabilities = list(zip(labels, probabilities))
    top_five = sorted(label_probabilities, key=lambda x: x[1], reverse=True)[:5]
    top_moods = [mood for mood, _ in top_five]
    top_keywords = [mood for mood, _ in top_five]
    return top_moods, top_keywords

# Function to process dataset
def process_dataset(audio_dir):
    for audio_file in os.listdir(audio_dir):
        if audio_file.endswith(".wav") or audio_file.endswith(".mp3"):
            audio_path = os.path.join(audio_dir, audio_file)
            embeddings = extract_embeddings(audio_path)
            if len(embeddings) == 0:
                print(f"Skipping {audio_file} due to extraction issues.")
                continue
            
            predictions = predict_moods(embeddings)
            moods, keywords = get_top_moods(predictions)
            entry = generate_dataset_entry(audio_file, audio_path, moods, keywords)
            json_filename = os.path.join(audio_dir, f"{os.path.splitext(audio_file)[0]}_metadata.json")
            save_to_json(entry, json_filename)
            print(f"Metadata for {audio_file} saved to {json_filename}")

if __name__ == "__main__":
    audio_directory = "/home/user/output"  # Update this path to your directory
    process_dataset(audio_directory)
