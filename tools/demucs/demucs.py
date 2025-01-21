import os
import shlex
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import cycle
import demucs.separate

def process_file(file_path, gpu_id):
    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    try:
        args = [
            "--mp3",
            "--two-stems", "vocals",
            "--segment", "7",
            "--overlap", "0.1",
            file_path
        ]
        demucs.separate.main(args)
        print(f"Successfully processed: {file_path} on GPU {gpu_id}")
    except Exception as e:
        print(f"Error processing {file_path} on GPU {gpu_id}: {e}")

def process_folder(folder_path, num_gpus, max_parallel):
    mp3_files = [
        os.path.join(folder_path, f) for f in os.listdir(folder_path)
        if f.lower().endswith('.mp3')
    ]
    
    gpu_cycle = cycle(range(num_gpus))
    with ProcessPoolExecutor(max_workers=max_parallel) as executor:
        futures = []
        for mp3_file in mp3_files:
            gpu_id = next(gpu_cycle)
            futures.append(executor.submit(process_file, mp3_file, gpu_id))
        
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Tiến trình gặp lỗi: {e}")

folder_path = '/home/user/data'
process_folder(folder_path,2,6)
