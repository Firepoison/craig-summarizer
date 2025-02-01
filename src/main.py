# Standard/Python imports
import json

# 3rd party imports
import whisper

# Project imports
from .summarizer import Summarizer


# Path to audio file to transcribe
audiofile_path = "src/data/01-26-25-FFEW.flac"

# Setting the transcription settings
transcriber = whisper.load_model("small")
transcription = transcriber.transcribe(audiofile_path)

# Setting the summarizer
summarizer = Summarizer()

# Save the dictionary to a JSON file, just to have on file.
with open("src/data/transcription_results.json", "w") as f:
    json.dump(transcription, f, indent=4)

summary = summarizer.summarize(transcription=transcription.get("text"))

# Save summary to a text file.
with open("src/data/summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)

