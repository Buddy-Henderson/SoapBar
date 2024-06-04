import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import SoapBar
import sys

# Static paths for Vosk model and bad words list
MODEL_PATH = r"C:\Users\buddy\Desktop\Code Projects\SoapBar\VoskModels\vosk-model-en-us-0.22-lgraph\vosk-model-en-us-0.22-lgraph"
BAD_WORDS_PATH = r"C:\Users\buddy\Desktop\Code Projects\SoapBar\BadWordList.txt"

def browse_file(entry, filetypes=None):
    filename = filedialog.askopenfilename(initialdir="/", title="Select File", filetypes=filetypes)
    entry.delete(0, tk.END)
    entry.insert(0, filename)

def browse_directory(entry):
    directory = filedialog.askdirectory(initialdir="/", title="Select Directory")
    entry.delete(0, tk.END)
    entry.insert(0, directory)

class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()

    def flush(self):
        pass

def update_terminal(message):
    print(message)

def process_video():
    video_path = video_entry.get()
    output_directory = output_entry.get()
    custom_sound_path = custom_sound_entry.get()

    if not video_path or not os.path.exists(video_path):
        messagebox.showerror("Error", "Please select a valid video file.")
        return

    if not output_directory or not os.path.exists(output_directory):
        messagebox.showerror("Error", "Please select a valid output directory.")
        return

    if not custom_sound_path or not os.path.exists(custom_sound_path):
        messagebox.showerror("Error", "Please select a valid custom sound file.")
        return

    def run_processing():
        bad_words_list = SoapBar.load_bad_words(BAD_WORDS_PATH)
        output_video = SoapBar.process_video(video_path, bad_words_list, output_directory, MODEL_PATH, custom_sound_path, update_terminal)
        if output_video:
            messagebox.showinfo("Success", f"Processed video saved to {output_video}")
        else:
            messagebox.showerror("Error", "An error occurred while processing the video.")

    # Start the processing in a new thread
    processing_thread = threading.Thread(target=run_processing)
    processing_thread.start()

# Create main window
window = tk.Tk()
window.title("SoapBar Video Processor")

# Redirect stdout to the terminal text widget
terminal_text = ScrolledText(window, wrap=tk.WORD, height=20, width=80)
terminal_text.grid(row=7, column=0, columnspan=3, padx=10, pady=10)
sys.stdout = StdoutRedirector(terminal_text)

# Video path entry
video_label = tk.Label(window, text="Video Path:")
video_label.grid(row=0, column=0)
video_entry = tk.Entry(window, width=50)
video_entry.grid(row=0, column=1)
video_button = tk.Button(window, text="Browse", command=lambda: browse_file(video_entry, [("Video files", "*.mp4;*.mov;*.avi;*.mkv")]))
video_button.grid(row=0, column=2)

# Output directory entry
output_label = tk.Label(window, text="Output Directory:")
output_label.grid(row=1, column=0)
output_entry = tk.Entry(window, width=50)
output_entry.grid(row=1, column=1)
output_button = tk.Button(window, text="Browse", command=lambda: browse_directory(output_entry))
output_button.grid(row=1, column=2)

# Custom sound file entry
custom_sound_label = tk.Label(window, text="Custom Sound File:")
custom_sound_label.grid(row=2, column=0)
custom_sound_entry = tk.Entry(window, width=50)
custom_sound_entry.grid(row=2, column=1)
custom_sound_button = tk.Button(window, text="Browse", command=lambda: browse_file(custom_sound_entry, [("Audio files", "*.mp3;*.wav")]))
custom_sound_button.grid(row=2, column=2)

# Process video button
process_button = tk.Button(window, text="Process Video", command=process_video)
process_button.grid(row=3, column=0, columnspan=3, pady=10)

window.mainloop()
