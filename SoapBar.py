import moviepy.editor as mp
from pydub import AudioSegment
import os
from vosk import Model, KaldiRecognizer
import wave
import json

def extract_audio_from_video(video_path):
    print(f"Extracting audio from video at path: {video_path}")
    video = mp.VideoFileClip(video_path)
    audio_path = "extracted_audio.wav"
    video.audio.write_audiofile(audio_path)
    return audio_path

def transcribe_audio_vosk(audio_path, model_path):
    print(f"Loading Vosk model from path: {model_path}")
    if not os.path.isdir(model_path):
        raise FileNotFoundError(f"Model directory not found: {model_path}")
    
    model = Model(model_path)
    wf = wave.open(audio_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    words_info = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = rec.Result()
            result_dict = json.loads(result)
            if "result" in result_dict:
                for word_info in result_dict["result"]:
                    word = word_info["word"]
                    start_time = word_info["start"] * 1000  # convert to milliseconds
                    end_time = word_info["end"] * 1000  # convert to milliseconds
                    words_info.append((word, start_time, end_time))

    final_result = rec.FinalResult()
    result_dict = json.loads(final_result)
    if "result" in result_dict:
        for word_info in result_dict["result"]:
            word = word_info["word"]
            start_time = word_info["start"] * 1000
            end_time = word_info["end"] * 1000
            words_info.append((word, start_time, end_time))

    wf.close()
    return words_info

def beep_replace(audio_segment, start_ms, end_ms):
    beep = AudioSegment.sine(1000, duration=(end_ms - start_ms))
    return audio_segment[:start_ms] + beep + audio_segment[end_ms:]

def replace_bad_words(audio_path, bad_words, model_path):
    audio_segment = AudioSegment.from_wav(audio_path)
    words_info = transcribe_audio_vosk(audio_path, model_path)

    for word, start_time, end_time in words_info:
        if word.lower() in bad_words:
            audio_segment = beep_replace(audio_segment, start_time, end_time)

    edited_audio_path = "edited_audio.wav"
    audio_segment.export(edited_audio_path, format="wav")
    return edited_audio_path

def combine_audio_with_video(video_path, audio_path, output_dir):
    video = mp.VideoFileClip(video_path)
    audio = mp.AudioFileClip(audio_path)
    new_video = video.set_audio(audio)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, "Finals #1 Edited.mp4")
    new_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    return output_path

def process_video(video_path, bad_words, output_dir, model_path):
    audio_path = extract_audio_from_video(video_path)
    edited_audio_path = replace_bad_words(audio_path, bad_words, model_path)
    output_video_path = combine_audio_with_video(video_path, edited_audio_path, output_dir)
    return output_video_path

def load_bad_words(file_path):
    with open(file_path, 'r') as file:
        bad_words = [line.strip().lower() for line in file.readlines()]
    return bad_words

# Example usage
bad_words_file = r"C:\Users\buddy\Desktop\Code Projects\SoapBar\BadWordList.txt"
output_directory = r"C:\Users\buddy\Desktop\Code Projects\Clippy\Test Video"
video_path = r"C:\Users\buddy\Desktop\Code Projects\Clippy\Test Video\Finals #1.mov"
model_path = r"C:\Users\buddy\Desktop\Code Projects\SoapBar\VoskModels\vosk-model-en-us-0.22\vosk-model-en-us-0.22"  # Path to the Vosk model

bad_words_list = load_bad_words(bad_words_file)

# Debugging: Print current working directory and check file existence
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")
absolute_video_path = os.path.abspath(video_path)
print(f"Absolute video path: {absolute_video_path}")
print(f"File exists: {os.path.exists(absolute_video_path)}")

# Check if the model directory contains the expected files
print(f"Contents of the model directory ({model_path}): {os.listdir(model_path)}")

output_video = process_video(video_path, bad_words_list, output_directory, model_path)
print(f"Processed video saved to {output_video}")