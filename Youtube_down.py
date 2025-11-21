import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import os
import glob

# Modern color scheme
BG_COLOR = "#2b2b2b"
FG_COLOR = "#ffffff"
ENTRY_BG = "#3c3c3c"
ENTRY_FG = "#ffffff"
BUTTON_BG = "#ff0000"
BUTTON_HOVER = "#cc0000"
BUTTON_SECONDARY = "#4a4a4a"
BUTTON_SECONDARY_HOVER = "#5a5a5a"
ACCENT_COLOR = "#00d4ff"
FRAME_BG = "#353535"

def get_file_path():
    file_path = filedialog.askdirectory()
    if file_path:
        threading.Thread(target=update_entry2, args=(file_path,)).start()

def update_entry2(file_path):
    entry2.delete(0, tk.END)
    entry2.insert(0, file_path)

def get_and_download():
    url = entry1.get().strip()
    file_path = entry2.get().strip()
    
    if not url:
        messagebox.showwarning("Warning", " Please enter a YouTube URL!")
        return
    
    if not file_path:
        messagebox.showwarning("Warning", "Please select a save location!")
        return
    
    download_button.config(state="disabled")
    status_label.config(text="Downloading...", fg=ACCENT_COLOR)
    threading.Thread(target=down_video, args=(url, file_path,)).start()

# Global variables for progress tracking
download_info = {'total_bytes': 0, 'downloaded_bytes': 0, 'filename': ''}

def progress_hook(d):
    try:
        if d['status'] == 'downloading':
            # Get total and downloaded bytes
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            
            # Store in global for file monitoring
            if total > 0:
                download_info['total_bytes'] = total
                download_info['downloaded_bytes'] = downloaded
                percent = min((downloaded / total) * 100, 100)
                down_bar["value"] = percent
                
                # Update status with speed
                speed = d.get('_speed_str', '')
                if speed:
                    status_label.config(text=f"Downloading... {speed}", fg=ACCENT_COLOR)
                else:
                    status_label.config(text="Downloading...", fg=ACCENT_COLOR)
                
                main_window.update_idletasks()
            else:
                # If no total_bytes, try to get from filename
                filename = d.get('filename', '')
                if filename and os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                    if file_size > download_info['downloaded_bytes']:
                        download_info['downloaded_bytes'] = file_size
                        # Estimate progress based on file growth
                        if download_info['total_bytes'] > 0:
                            percent = min((file_size / download_info['total_bytes']) * 100, 100)
                            down_bar["value"] = percent
                            main_window.update_idletasks()
        
        elif d['status'] == 'finished':
            down_bar["value"] = 100
            status_label.config(text="Processing...", fg=ACCENT_COLOR)
            main_window.update_idletasks()
    except:
        pass

def monitor_file_progress(expected_filename, total_size):
    """Monitor file size to update progress bar"""
    while download_button['state'] == 'disabled':
        try:
            if os.path.exists(expected_filename):
                current_size = os.path.getsize(expected_filename)
                if total_size > 0:
                    percent = min((current_size / total_size) * 100, 99)  # Max 99% until finished
                    down_bar["value"] = percent
                    main_window.update_idletasks()
            time.sleep(0.5)  # Check every 0.5 seconds
        except:
            pass

def down_video(url, file_path):
    global download_info
    try:
        # Reset progress bar and info
        down_bar["value"] = 0
        download_info = {'total_bytes': 0, 'downloaded_bytes': 0, 'filename': ''}
        status_label.config(text="Getting video info...", fg=ACCENT_COLOR)
        main_window.update_idletasks()
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(file_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info first
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            video_views = info.get('view_count', 0)
            
            # Get expected file size
            formats = info.get('formats', [])
            best_format = None
            for fmt in formats:
                if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                    best_format = fmt
                    break
            if not best_format:
                best_format = formats[-1] if formats else {}
            
            total_size = best_format.get('filesize') or best_format.get('filesize_approx', 0)
            download_info['total_bytes'] = total_size
            
            # Get expected filename
            filename_template = ydl_opts['outtmpl']
            safe_title = ydl.prepare_filename({'title': video_title, 'ext': 'mp4'})
            expected_filename = os.path.join(file_path, os.path.basename(safe_title))
            download_info['filename'] = expected_filename
            
            status_label.config(text="Starting download...", fg=ACCENT_COLOR)
            main_window.update_idletasks()
            
            # Start file monitoring thread
            if total_size > 0:
                monitor_thread = threading.Thread(target=monitor_file_progress, args=(expected_filename, total_size), daemon=True)
                monitor_thread.start()
            
            # Download the video
            ydl.download([url])
            
        entry1.delete(0, tk.END)
        down_message(video_title, video_views)
    except Exception as e:
        error_msg = str(e)
        if "HTTP Error 403" in error_msg or "HTTP Error 400" in error_msg:
            error_msg = "YouTube access denied. Please try again later or check your internet connection."
        messagebox.showerror("Error", f"An error occurred while downloading:\n{error_msg}")
        status_label.config(text="Error", fg="#ff4444")
        download_button.config(state="normal")
        down_bar["value"] = 0

def down_message(title, views):
    try:
        messagebox.showinfo("Download Complete", 
                          f"Title: {title}\nViews: {views:,}")
    except:
        messagebox.showinfo("Download Complete", "Video successfully downloaded!")
    
    down_bar["value"] = 0
    status_label.config(text="Ready", fg="#4caf50")
    download_button.config(state="normal")

def on_button_hover(event, button, hover_color):
    button.config(bg=hover_color)

def on_button_leave(event, button, original_color):
    button.config(bg=original_color)

def start_move(event):
    main_window.x = event.x
    main_window.y = event.y

def on_move(event):
    deltax = event.x - main_window.x
    deltay = event.y - main_window.y
    x = main_window.winfo_x() + deltax
    y = main_window.winfo_y() + deltay
    main_window.geometry(f"+{x}+{y}")

try:
    main_window = tk.Tk()
    main_window.geometry("600x500+500+200")
    main_window.resizable(width=False, height=False)
    main_window.overrideredirect(True)  # Remove title bar
    main_window.configure(bg=BG_COLOR)
    
    # Modern styling
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Modern.Horizontal.TProgressbar",
                    background=ACCENT_COLOR,
                    troughcolor=ENTRY_BG,
                    borderwidth=0,
                    lightcolor=ACCENT_COLOR,
                    darkcolor=ACCENT_COLOR)
    
    # Custom Title Bar Frame (draggable)
    title_bar = tk.Frame(main_window, bg=BG_COLOR, height=50)
    title_bar.pack(fill=tk.X)
    title_bar.pack_propagate(False)
    
    # Make title bar draggable
    title_bar.bind("<Button-1>", start_move)
    title_bar.bind("<B1-Motion>", on_move)
    
    # Title and close button container
    title_container = tk.Frame(title_bar, bg=BG_COLOR)
    title_container.pack(fill=tk.X, padx=15, pady=10)
    
    title_label = tk.Label(title_container, 
                          text="🎬 YouTube Video Downloader",
                          font=("Segoe UI", 16, "bold"),
                          bg=BG_COLOR,
                          fg=FG_COLOR,
                          cursor="hand2")
    title_label.pack(side=tk.LEFT)
    title_label.bind("<Button-1>", start_move)
    title_label.bind("<B1-Motion>", on_move)
    
    # Close button
    close_button = tk.Button(title_container,
                            text="✕",
                            font=("Segoe UI", 14, "bold"),
                            bg=BG_COLOR,
                            fg=FG_COLOR,
                            activebackground="#ff4444",
                            activeforeground=FG_COLOR,
                            relief=tk.FLAT,
                            bd=0,
                            width=3,
                            height=1,
                            cursor="hand2",
                            command=main_window.quit)
    close_button.pack(side=tk.RIGHT)
    close_button.bind("<Enter>", lambda e: close_button.config(bg="#ff4444"))
    close_button.bind("<Leave>", lambda e: close_button.config(bg=BG_COLOR))
    
    # Header Frame (spacing)
    header_frame = tk.Frame(main_window, bg=BG_COLOR, pady=10)
    header_frame.pack(fill=tk.X)
    
    # Main Container Frame
    main_frame = tk.Frame(main_window, bg=BG_COLOR, padx=30, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Progress Bar Frame
    progress_frame = tk.Frame(main_frame, bg=BG_COLOR)
    progress_frame.pack(fill=tk.X, pady=(0, 25))
    
    progress_label = tk.Label(progress_frame,
                              text="Progress:",
                              font=("Segoe UI", 10),
                              bg=BG_COLOR,
                              fg=FG_COLOR)
    progress_label.pack(anchor=tk.W, pady=(0, 5))
    
    down_bar = ttk.Progressbar(progress_frame,
                               orient="horizontal",
                               length=500,
                               mode="determinate",
                               style="Modern.Horizontal.TProgressbar")
    down_bar.pack(fill=tk.X)
    
    # URL Input Frame
    url_frame = tk.Frame(main_frame, bg=BG_COLOR)
    url_frame.pack(fill=tk.X, pady=(0, 15))
    
    label1 = tk.Label(url_frame,
                      text="YouTube URL:",
                      font=("Segoe UI", 11, "bold"),
                      bg=BG_COLOR,
                      fg=FG_COLOR)
    label1.pack(anchor=tk.W, pady=(0, 8))
    
    entry1 = tk.Entry(url_frame,
                      width=60,
                      font=("Segoe UI", 10),
                      bg=ENTRY_BG,
                      fg=ENTRY_FG,
                      insertbackground=FG_COLOR,
                      relief=tk.FLAT,
                      bd=3)
    entry1.pack(fill=tk.X, ipady=8)
    
    # File Path Frame
    path_frame = tk.Frame(main_frame, bg=BG_COLOR)
    path_frame.pack(fill=tk.X, pady=(0, 20))
    
    label2 = tk.Label(path_frame,
                      text="Save Location:",
                      font=("Segoe UI", 11, "bold"),
                      bg=BG_COLOR,
                      fg=FG_COLOR)
    label2.pack(anchor=tk.W, pady=(0, 8))
    
    path_input_frame = tk.Frame(path_frame, bg=BG_COLOR)
    path_input_frame.pack(fill=tk.X)
    
    entry2 = tk.Entry(path_input_frame,
                      width=60,
                      font=("Segoe UI", 10),
                      bg=ENTRY_BG,
                      fg=ENTRY_FG,
                      insertbackground=FG_COLOR,
                      relief=tk.FLAT,
                      bd=5)
    entry2.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
    
    button1 = tk.Button(path_input_frame,
                        text="📁 Select Folder",
                        font=("Segoe UI", 9),
                        bg=BUTTON_SECONDARY,
                        fg=FG_COLOR,
                        activebackground=BUTTON_SECONDARY_HOVER,
                        activeforeground=FG_COLOR,
                        relief=tk.FLAT,
                        bd=0,
                        padx=15,
                        pady=8,
                        cursor="hand2",
                        command=get_file_path)
    button1.pack(side=tk.LEFT, padx=(10, 0))
    button1.bind("<Enter>", lambda e: on_button_hover(e, button1, BUTTON_SECONDARY_HOVER))
    button1.bind("<Leave>", lambda e: on_button_leave(e, button1, BUTTON_SECONDARY))
    
    # Button Frame
    button_frame = tk.Frame(main_frame, bg=BG_COLOR)
    button_frame.pack(fill=tk.X, pady=(10, 0))
    
    download_button = tk.Button(button_frame,
                                text="⬇️ Download",
                                font=("Segoe UI", 12, "bold"),
                                bg=BUTTON_BG,
                                fg=FG_COLOR,
                                activebackground=BUTTON_HOVER,
                                activeforeground=FG_COLOR,
                                relief=tk.FLAT,
                                bd=0,
                                padx=40,
                                pady=12,
                                cursor="hand2",
                                command=get_and_download)
    download_button.pack(side=tk.LEFT, padx=(0, 10))
    download_button.bind("<Enter>", lambda e: on_button_hover(e, download_button, BUTTON_HOVER))
    download_button.bind("<Leave>", lambda e: on_button_leave(e, download_button, BUTTON_BG))
    
    
    
    # Status Label
    status_label = tk.Label(main_frame,
                           text="Ready",
                           font=("Segoe UI", 9),
                           bg=BG_COLOR,
                           fg="#4caf50")
    status_label.pack(pady=(15, 0))
    
    # Center window on screen
    main_window.update_idletasks()
    width = main_window.winfo_width()
    height = main_window.winfo_height()
    x = (main_window.winfo_screenwidth() // 2) - (width // 2)
    y = (main_window.winfo_screenheight() // 2) - (height // 2)
    main_window.geometry(f'{width}x{height}+{x}+{y}')
    
    main_window.mainloop()
except Exception as e:
    print("An error occurred:", str(e))