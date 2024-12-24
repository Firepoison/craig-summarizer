import json

import whisper

# Path to audio file to transcribe
audiofile_path = "src/data/10-09-24-FFEW.flac"

# Setting the transcription settings
transcriber = whisper.load_model("small")
transcription = transcriber.transcribe(audiofile_path)

# Save the dictionary to a JSON file
with open("src/data/transcription_results.json", "w") as f:
    json.dump(transcription, f, indent=4)
