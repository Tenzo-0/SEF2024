import yt_dlp
import os
import concurrent.futures
import threading

# Function to download a single video as MP3 with the best quality
def download_video(url, count_lock, count_value):
    ydl_opts = {
        'format': 'bestaudio/best',  # Ensure we download the best audio format available
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',  # Download at 320 kbps for highest quality
        }],
        'outtmpl': 'downloads/%(title)s.%(ext)s',  # Save files in the 'downloads' folder
        'quiet': False,  # Set to True to suppress log output
        'clean': true,
        'cookies': '/home/user/your_cookies_file.txt'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Update the count of downloaded files in real-time
    with count_lock:
        count_value[0] += 1
        print(f"Total downloaded MP3 files: {count_value[0]}")

# Function to get the list of video URLs from a YouTube playlist
def get_playlist_urls(playlist_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  # Do not download the videos, just extract the URLs
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)
        if 'entries' in result:
            return [entry['url'] for entry in result['entries']]
        return []

# Main function to download all videos in parallel using ThreadPoolExecutor
def download_playlist(playlist_url):
    print("Fetching video URLs from the playlist...")
    video_urls = get_playlist_urls(playlist_url)

    if not video_urls:
        print("No videos found in the playlist.")
        return

    # Create the downloads directory if it doesn't exist
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    print(f"Found {len(video_urls)} videos. Starting parallel download...")

    # Shared count value (using a list to make it mutable)
    count_value = [0]

    # Use a lock for thread safety when updating the count
    count_lock = threading.Lock()

    # Create a ThreadPoolExecutor to handle downloads in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit each download task to the ThreadPoolExecutor
        futures = [executor.submit(download_video, url, count_lock, count_value) for url in video_urls]

        # Wait for all the download tasks to complete
        concurrent.futures.wait(futures)

    print("Download complete!")

# Replace this with your YouTube playlist URL
playlist_url = 'https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID'
download_playlist(playlist_url)
