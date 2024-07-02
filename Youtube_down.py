from pytube import YouTube
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time

def get_file_path():
    file_path = filedialog.askdirectory()
    threading.Thread(target=update_entry2, args=(file_path,)).start()

def update_entry2(file_path):
    entry2.delete(0, tk.END)
    entry2.insert(0,file_path)
def get_and_download():
    url = entry1.get()
    file_path = entry2.get()
    threading.Thread(target=down_video, args=(url,file_path,)).start()

def down_video(url,file_path):
    yt = YouTube(url, on_progress_callback=data_bar)
    ytvh = yt.streams.get_highest_resolution()
    ytvh.download(file_path)
    entry1.delete(0, tk.END)
    down_message(url)

def down_message(url):
    messagebox.showinfo("Download Complete", f"Title: {YouTube(url).title} \nViews: {YouTube(url).views}")
    down_bar["value"] = 0

def data_bar(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    completion = (bytes_downloaded / total_size) * 100

    while down_bar["value"] < completion:
        down_bar["value"] += 1
        main_window.update_idletasks()
        time.sleep(0.05)

try:
    main_window = tk.Tk()
    main_window.geometry("450x175+600+200")  # +y+x
    main_window.resizable(width=False, height=False)
    main_window.title("YouTube Video Downloader")

    down_bar = ttk.Progressbar(main_window, orient="horizontal", length=300, mode="determinate")
    down_bar.grid(row=0, column=1, pady=10)

    label1 = tk.Label(main_window, text="YouTube Url:", font="Helvetica 11")
    label1.grid(row=1, column=0)

    entry1 = tk.Entry(main_window, width=45)
    entry1.grid(row=1, column=1)

    label2 = tk.Label(main_window, text="File Path:", font="Helvetica 11")
    label2.grid(row=2, column=0)

    entry2 = tk.Entry(main_window, width=45)
    entry2.grid(row=2, column=1)

    button1 = tk.Button(main_window, text="File Path", font="Helvetica 8" ,command=get_file_path)
    button1.grid(row=2, column=2)

    download_button = tk.Button(main_window, text="Download", command=get_and_download, width=8, height=2)
    download_button.grid(row=3, column=1)

    exit_button = tk.Button(main_window, text="Exit", command=main_window.quit)
    exit_button.grid(row=4, column=1)

    label3 = tk.Label(main_window, text="made by Emirhan Oğuz", font="Helvetica 7")
    label3.grid(row=5, column=0)

    main_window.mainloop()
except Exception as e:
    print("An error occurred:", str(e))