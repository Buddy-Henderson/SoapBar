import moviepy.editor as mp
from pydub import AudioSegment
import os
from vosk import Model, KaldiRecognizer
import wave
import json
import subprocess

# Static paths
BAD_WORDS_PATH = "path/to/bad_words.txt"

# Function to extract audio from video
def extract_audio_from_video(video_path, update_terminal):
    try:
        update_terminal(f"Extracting audio from video at path: {video_path}")
        audio_path = "extracted_audio.wav"
        
        # Use ffmpeg to extract audio in WAV, mono, PCM format
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vn",  # Disable video recording
            "-ac", "1",  # Mono channel
            "-acodec", "pcm_s16le",  # PCM 16-bit encoding
            audio_path
        ]
        subprocess.run(command, check=True)

        update_terminal(f"Audio extracted to: {audio_path}")
        return audio_path
    
    except Exception as e:
        update_terminal(f"An error occurred while extracting audio: {e}")
        return None

# Function to transcribe audio using Vosk
def transcribe_audio_vosk(audio_path, model_path, update_terminal):
    try:
        update_terminal("Loading Vosk model...")
        # Load the Vosk model
        model = Model(model_path)
        
        # Open the audio file using a context manager to ensure it is properly closed
        with wave.open(audio_path, "rb") as wf:
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            words_info = []

            update_terminal("Transcribing audio...")
            # Process the audio file in chunks
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
                            start_time = word_info["start"] * 1000  # Convert to milliseconds
                            end_time = word_info["end"] * 1000  # Convert to milliseconds
                            words_info.append((word, start_time, end_time))

            # Process the final result
            final_result = rec.FinalResult()
            result_dict = json.loads(final_result)
            if "result" in result_dict:
                for word_info in result_dict["result"]:
                    word = word_info["word"]
                    start_time = word_info["start"] * 1000  # Convert to milliseconds
                    end_time = word_info["end"] * 1000  # Convert to milliseconds
                    words_info.append((word, start_time, end_time))

        update_terminal("Audio transcription completed.")
        return words_info

    except Exception as e:
        update_terminal(f"An error occurred during transcription: {e}")
        return []

# Function to replace bad words with a custom sound
def custom_sound_replace(audio_segment, start_ms, end_ms, custom_sound_path, update_terminal):
    beep_duration = end_ms - start_ms
    update_terminal(f"Creating custom sound from {start_ms}ms to {end_ms}ms ({beep_duration}ms)")

    # Load the custom sound and adjust its duration to match the segment
    custom_sound = AudioSegment.from_file(custom_sound_path)
    
    # Ensure the custom sound matches the duration of the segment
    if len(custom_sound) < beep_duration:
        custom_sound = custom_sound + AudioSegment.silent(duration=(beep_duration - len(custom_sound)))
    else:
        custom_sound = custom_sound[:beep_duration]

    update_terminal(f"Replacing audio from {start_ms}ms to {end_ms}ms with custom sound")

    # Replace the specified segment with the custom sound
    return audio_segment[:start_ms] + custom_sound + audio_segment[end_ms:]

# Function to replace bad words in the audio
def replace_bad_words(audio_path, bad_words, model_path, custom_sound_path, update_terminal):
    # Load the audio file
    audio_segment = AudioSegment.from_wav(audio_path)
    # Transcribe the audio to get word timings
    words_info = transcribe_audio_vosk(audio_path, model_path, update_terminal)

    # Print transcribed words and their timings for debugging
    update_terminal("Transcribed words and their timings:")
    for word, start_time, end_time in words_info:
        update_terminal(f"Word: {word}, Start time: {start_time}, End time: {end_time}")
        # Replace bad words with custom sound
        if word.lower() in bad_words:
            update_terminal(f"Beeping out: {word}")
            audio_segment = custom_sound_replace(audio_segment, start_time, end_time, custom_sound_path, update_terminal)

    # Export the edited audio to a new file
    edited_audio_path = "edited_audio.wav"
    audio_segment.export(edited_audio_path, format="wav")

    # Verify the audio by reloading and checking the segment length
    reloaded_audio_segment = AudioSegment.from_wav(edited_audio_path)
    update_terminal(f"Length of original audio: {len(audio_segment)}")
    update_terminal(f"Length of edited audio: {len(reloaded_audio_segment)}")

    # Return the path to the edited audio file
    return edited_audio_path

# Function to combine edited audio with the original video
def combine_audio_with_video(video_path, audio_path, output_dir, update_terminal):
    try:
        video = mp.VideoFileClip(video_path)
        audio = mp.AudioFileClip(audio_path)
        new_video = video.set_audio(audio)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Add "censored" to the original file name
        base_name = os.path.basename(video_path)
        name, ext = os.path.splitext(base_name)
        output_path = os.path.join(output_dir, f"{name} censored{ext}")

        update_terminal(f"Combining audio with video, saving to: {output_path}")
        new_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        return output_path
    except Exception as e:
        update_terminal(f"An error occurred: {e}")
        return None
    finally:
        video.reader.close()
        video.audio.reader.close_proc()
        audio.reader.close_proc()

# Function to process the video: extract audio, replace bad words, and recombine
def process_video(video_path, bad_words, output_dir, model_path, custom_sound_path, update_terminal):
    # Extract the audio from the video
    audio_path = extract_audio_from_video(video_path, update_terminal)
    if not audio_path:
        return None
    
    # Replace bad words in the audio
    edited_audio_path = replace_bad_words(audio_path, bad_words, model_path, custom_sound_path, update_terminal)
    
    # Combine the edited audio with the original video
    output_video_path = combine_audio_with_video(video_path, edited_audio_path, output_dir, update_terminal)
    
    # Delete temporary audio files
    if os.path.exists(audio_path):
        os.remove(audio_path)
    if os.path.exists(edited_audio_path):
        os.remove(edited_audio_path)

    # Return the path to the output video
    return output_video_path

# Function to load bad words from a file
def load_bad_words(file_path):
    try:
        with open(file_path, 'r') as file:
            bad_words = [line.strip().lower() for line in file.readlines() if line.strip()]
        return bad_words
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
