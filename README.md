# Craig Summarizer
This application is a simple application utilzing LLMs to summarize a long Discord transcription from an audio source, in this case an audio recording saved by the Craig bot within Discord. Ideally, used for meetings etc.

## Setup
This uses uv to manage the environment.

Install dependencies by running: `uv pip install -r requirements.txt`, or `uv sync`

## Installation and Usage
Right now, testing is being done by manually downloading the audio from craig, and inserting it into a data file as a FLAC, MP3, etc. This file will be saved under `src/data/audio/` and then selected in the CLI when you run the program.

Run main.py ( `uv run src/main.py` )
The CLI will guide you through selecting a file from `src/data/audio/` to transcribe and summarize.
It will then go through transcription first showing the progress, and will save the transcription results to `src/data/transcription_results.json`.
Finally, it will go through the summarization process, showing the progress of the LLM generating the summary in real time as the response is streamed, and then save that summary to `src/data/summary.md`. This should be formatted properly to insert directly into a Discord message (do not use the ```).

## Project Structure
```
src/
├── data/
│   ├── audio/
│   │   ├── 2026-05-01-22.52.29-Meeting.flac
│   │   └── ...
│   ├── transcription_results.json
│   └── summary.md
├── main.py
├── summarizer.py
└── transcriber.py
```

## Transcriber
Utilizing whisper, we will transcribe the entire audio and save it into its JSON format. For now here, we import whisper and utilize the small model, as it should be plenty for our needs while still being quite accurate.

#### Future Features:
- Ingestion of audio as they are saved (ideally in a working server).
- Breaking apart transcription by speaker.
- Picking up on questions specifically, to send individually for the LLM to summarize.

## Summarizer
Utilizing Gemini, we will summarize the transcription in whole. The prompt given will focus on a holistic summary for people to look over, including bullet points and a Q&A section.

#### Future Features:
- Separate prompts/calls for summary, bullet points, and Q&A
- Automatic detection of primary lead/speakers and their duration of speaking.