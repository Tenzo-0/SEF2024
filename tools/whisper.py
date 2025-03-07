import os
import json
import multiprocessing
import whisper
import torch  # Needed to check available GPUs

# Global variable to be set in each worker process
model = None

# Output file to store transcriptions
output_file = 'transcriptions.json'

def init_worker():
    """
    Initializer for each worker process.
    Determines a unique GPU for this worker based on its index,
    sets the CUDA_VISIBLE_DEVICES variable, and loads the Whisper model.
    """
    # Determine worker index using the process name (e.g., "ForkPoolWorker-1")
    proc_name = multiprocessing.current_process().name
    try:
        worker_index = int(proc_name.split("-")[-1]) - 1
    except Exception:
        worker_index = 0

    # Determine number of available GPUs
    num_gpus = torch.cuda.device_count()
    if num_gpus > 0:
        # Cycle through GPUs if number of workers exceeds number of GPUs
        gpu_id = worker_index % num_gpus
        os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
        print(f"{proc_name} using GPU {gpu_id}")
    else:
        print(f"{proc_name} found no GPU, using CPU.")

    global model
    model = whisper.load_model("medium")  # Use "small", "medium", "large" as needed

def transcribe_audio(file_path):
    result = model.transcribe(file_path, language="vi")  # Set language to Vietnamese    
    return result['text']

def process_file(file_path):
    """
    Worker function for processing a single file.
    Returns a tuple of (file_path, transcription).
    """
    transcription = transcribe_audio(file_path)
    return file_path, transcription

def process_folder(folder_path, remove_previous=False):
    # Optionally remove the previous output file (if you want a fresh start)
    if remove_previous and os.path.exists(output_file):
        os.remove(output_file)
        print("Removed previous transcription file.")

    # Load existing transcriptions if the file exists
    transcriptions = {}
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            transcriptions = json.load(f)

    mp3_files = []
    # Walk through the folder and its subfolders to find MP3 files
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mp3"):
                file_path = os.path.join(root, file)
                mp3_files.append(file_path)

    # Filter out files that have already been processed
    files_to_process = [f for f in mp3_files if f not in transcriptions]
    total_files = len(files_to_process)
     
    if total_files == 0:
        print("No new MP3 files to process.")
        return

    print(f"Found {total_files} new MP3 files. Processing with 4 processes...")

    # Use a multiprocessing pool with 4 processes and an initializer to load the model in each process
    with multiprocessing.Pool(processes=4, initializer=init_worker) as pool:
        # imap_unordered returns results as they become available
        for idx, result in enumerate(pool.imap_unordered(process_file, files_to_process), start=1):
            file_path, transcription = result
            transcriptions[file_path] = transcription

            # Write the updated transcriptions incrementally
            with open(output_file, 'w', encoding='utf-8') as json_file:
                json.dump(transcriptions, json_file, ensure_ascii=False, indent=4)

            print(f"Processed {idx}/{total_files}: {file_path}")

    print(f"All transcriptions saved to {output_file}")

# Folder containing your MP3 files
folder_path = '/home/user/d1'  # Replace with the path to your folder containing MP3 files

# Set remove_previous to True if you want to delete previous results and process everything anew;
# set to False if you want to resume and skip already processed files.
process_folder(folder_path, remove_previous=False)
