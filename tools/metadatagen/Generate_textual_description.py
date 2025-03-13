import librosa
import os
from openai import OpenAI
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

def GPT_description(trans) :
    client = OpenAI(
        api_key="your_api_key"
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là một nhạc sĩ đờn ca tài tử nam bộ Việt Nam"},
            {
                "role": "user",
            "content": f"tôi sẽ cho bạn lời nhạc, việc của bạn là nhận biết bối cảnh của đoạn nhạc và viết cho tôi một đoạn mô tả không cách dòng viết liền khoảng 100 từ bằng tiếng anh, sau khi viết xong mô tả, xuống dòng và viết cho tôi một vài keywords liên quan đến mô tả, lời nhạc:\n {trans}"
            }
        ]
    )
    res = completion.choices[0].message.content
    message, keywords = res.strip().split("\n\n", 1)
    keywords = keywords.replace("Keywords: ", "").strip()
    return message, keywords

# Function to generate dataset entry with adjusted moods and keywords
def generate_dataset_entry(audio_file, audio_path, moods, keywords, trans):
    duration, tempo, sample_rate = extract_audio_features(audio_path)
    exclude_terms = {"Don ca tai tu", "Vietnamese Northside traditional music"}

    # Filter specific terms from moods
    filtered_moods = [mood for mood in moods if mood not in exclude_terms]
    mood_list = ', '.join(filtered_moods)

    description_chatgpt, keywords_chatgpt = GPT_description(trans)
    enhanced_keywords = keywords + [keywords_chatgpt] + list(exclude_terms)

    description = f"A {duration:.1f} seconds long song at {tempo} BPM with moods like {mood_list}. {description_chatgpt}"


    entry = {
        "key": "",
        "artist": "",
        "sample_rate": sample_rate,
        "file_extension": audio_file.split('.')[-1],
        "description": description,
        "keywords": ', '.join(enhanced_keywords),
        "duration": duration,
        "bpm": tempo,
        "genre": "Cai Luong",
        "title": audio_file.split('.')[0],
        "name": audio_file.split('.')[0],
        "instrument": "Mix",
        "moods": filtered_moods
    }
    return entry

# Helper function to make data JSON serializable
def make_serializable(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: make_serializable(value) for key, value in obj.items()}
    else:
        return obj

# Function to save dataset to JSON
def save_to_json(entry, output_filename):
    serializable_entry = make_serializable(entry)
    with open(output_filename, 'w') as f:
        json.dump(serializable_entry, f, indent=4)

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

# Updated function to get top 3 moods with filtering unwanted moods
def get_top_moods(probabilities):
    labels = [
        "action", "adventure", "advertising", "background", "ballad", "calm", "children", "christmas", "commercial",
        "cool", "corporate", "dark", "deep", "documentary", "drama", "dramatic", "dream", "emotional", "energetic",
        "epic", "fast", "film", "fun", "funny", "game", "groovy", "happy", "heavy", "holiday", "hopeful", "inspiring",
        "love", "meditative", "melancholic", "melodic", "motivational", "movie", "nature", "party", "positive",
        "powerful", "relaxing", "retro", "romantic", "sad", "sexy", "slow", "soft", "soundscape", "space", "sport",
        "summer", "trailer", "travel", "upbeat", "uplifting"
    ]
    exclude_moods = {"christmas", "ballad", "game", "retro", "space", "sport", "trailer", "travel", "action", "adventure", "advertising", "children", "commercial", "corporate", "holiday", "party", "soundcape", "sexy", "summer", "background", "drama", "documentary", "movie", "motivational", "nature", "party", "powerful"}
    label_probabilities = list(zip(labels, probabilities))
    filtered_moods = [label for label, prob in sorted(label_probabilities, key=lambda x: x[1], reverse=True) if label not in exclude_moods][:3]
    return filtered_moods, filtered_moods

# Function to process dataset
def process_dataset(audio_dir, trans_dir):
    with open(trans_dir, 'r') as file:
        data = json.load(file)

    for audio_file in os.listdir(audio_dir):
        if audio_file.endswith(".wav") or audio_file.endswith(".mp3"):
            audio_path = os.path.join(audio_dir, audio_file)
            embeddings = extract_embeddings(audio_path)
            if len(embeddings) == 0:
                print(f"Skipping {audio_file} due to extraction issues.")
                continue

            predictions = predict_moods(embeddings)
            moods, keywords = get_top_moods(predictions)
            entry = generate_dataset_entry(audio_file, audio_path, moods, keywords, data[audio_file])
            json_filename = os.path.join(audio_dir, f"{os.path.splitext(audio_file)[0]}_metadata.json")
            save_to_json(entry, json_filename)
            print(f"Metadata for {audio_file} saved to {json_filename}")

if __name__ == "__main__":
    audio_directory = "/home/user/d2"  # Update this path to your directory
    transcription_dir = "/home/user/d2_json.json"
    process_dataset(audio_directory,transcription_dir)
