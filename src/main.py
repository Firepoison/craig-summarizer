# Standard/Python imports
import json

# 3rd party imports
import whisper

# Project imports
from .summarizer import Summarizer


# Path to audio file to transcribe
audiofile_path = "src/data/10-09-24-FFEW.flac"

# Setting the transcription settings
transcriber = whisper.load_model("small")
transcription = transcriber.transcribe(audiofile_path)

# Setting the summarizer
summarizer = Summarizer()

# Save the dictionary to a JSON file
with open("src/data/transcription_results.json", "w") as f:
    json.dump(transcription, f, indent=4)

summarizer.summarize(transcription=transcription)
