Project Description

SoapBar is a Python-based application designed to automatically detect and censor inappropriate or bad words in video files. Utilizing state-of-the-art speech recognition technology with the Vosk speech-to-text engine, SoapBar extracts audio from video files, identifies predefined bad words, and replaces them with a beep sound. The final output is a video with edited audio that censors unwanted language, making it suitable for a wider audience.

Features
Audio Extraction: Extracts audio from video files (MOV, MP4) using MoviePy.
Speech Recognition: Transcribes audio to text using the Vosk speech-to-text engine.
Bad Word Detection: Scans the transcription for predefined bad words.
Censorship: Replaces detected bad words with a beep sound effect.
Output: Combines the edited audio with the original video and saves it to a user-defined output directory.
Customizable: Users can provide their own list of bad words via a text file.
