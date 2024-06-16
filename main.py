import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pytube import Playlist, YouTube
import os
import threading
import queue
import subprocess

# Global variables
output_dir = os.path.join(os.path.expanduser('~'), 'Downloads')  # Change this to your desired output directory
download_queue = queue.Queue()
last_downloaded_path = None


def download_next_video():
    try:
        video_url, title = download_queue.get_nowait()
        download_video(video_url, title)
        download_queue.task_done()
    except queue.Empty:
        # Queue is empty, all downloads are complete
        messagebox.showinfo("Success", "Playlist download complete.")
        progress_bar["value"] = 0
        percent_label.config(text="0%")
        status_label.config(text="")
        root.update_idletasks()


def download_video(video_url, title):
    try:
        yt = YouTube(video_url, on_progress_callback=progress_function)

        # Get the highest resolution stream
        vs = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()

        if vs is None:
            status_label.config(text=f"No suitable stream found for {title}")
            return

        progress_bar["value"] = 0
        percent_label.config(text="0%")
        status_label.config(text=f"Downloading {title}...")

        # Download the video to the specified output directory
        vs.download(output_path=output_dir)
        status_label.config(text=f"Downloaded {title}")

        global last_downloaded_path
        last_downloaded_path = output_dir

        root.update_idletasks()

    except Exception as e:
        status_label.config(text="An error occurred.")
        messagebox.showerror("Error", f"An error occurred while downloading {title}: {str(e)}")


def download_playlist()
    try:
        playlist_url = url_entry.get()
        if not playlist_url:
            messagebox.showwarning("Input Error", "Please enter a YouTube Playlist URL")
            return

        playlist = Playlist(playlist_url)

        # Add all videos in the playlist to the download queue
        for video_url in playlist.video_urls:
            yt = YouTube(video_url)
            download_queue.put((video_url, yt.title))

        # Start downloading videos in a separate thread
        download_thread = threading.Thread(target=start_downloading)
        download_thread.start()

    except Exception as e:
        status_label.config(text="An error occurred.")
        messagebox.showerror("Error", f"An error occurred while fetching playlist: {str(e)}")


def start_downloading():
    while not download_queue.empty():
        download_next_video()


def progress_function(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    progress_bar["value"] = percentage_of_completion
    percent_label.config(text=f"{percentage_of_completion:.2f}%")
    root.update_idletasks()


def open_download_folder():
    try:
        if last_downloaded_path:
            if os.name == 'nt':  # Windows
                os.startfile(last_downloaded_path)
            elif os.name == 'posix':  # macOS or Linux
                subprocess.call(['open', last_downloaded_path])
            else:
                messagebox.showerror("Error", "Unsupported OS")
        else:
            messagebox.showwarning("Warning", "No download folder found")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


# Create the main window
root = tk.Tk()
root.title("YouTube Playlist Downloader")

# Create and place the URL entry
url_label = tk.Label(root, text="YouTube Playlist URL:")
url_label.pack(pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# Create and place the download button for playlist
download_button = tk.Button(root, text="Download Playlist", command=download_playlist)
download_button.pack(pady=10)

# Create and place the progress bar
progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
progress_bar.pack(pady=10)

# Create and place the percentage label
percent_label = tk.Label(root, text="0%")
percent_label.pack(pady=5)

# Create and place the status label
status_label = tk.Label(root, text="")
status_label.pack(pady=5)

# Create and place the open folder button
open_folder_button = tk.Button(root, text="Open Download Folder", command=open_download_folder)
open_folder_button.pack(pady=10)

# Run the application
root.mainloop()
