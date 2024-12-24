# Craig Summarizer
This application is a simple application utilzing LLMs to summarize a long Discord transcription from an audio source, in this case an audio recording saved by the Craig bot within Discord. Ideally, used for meetings etc.

## Installation and Usage
Right now, testing is being done by manually downloading the audio from craig, and inserting it into a data file. This file will be saved under `src/data/` and then pointed at by the `audiofile_path` variable in main.py.

Run main.py and it will say a full transcription JSON from whisper in `src/data` as transcription_results.json.

## Transcriber
Utilizing whisper, we will transcribe the entire audio and save it into its JSON format. For now here, we import whisper and utilize the small model, asi t should be plenty for our needs while still being quite accurate.

#### Future Features:
- Ingestion of audio as they are saved (ideally in a working server).
- Breaking apart transcription by speaker.
- Picking up on questions specifically, to send individually for the LLM to summarize.

## Summarizer
Utilizing Gemini, we will summarize the transcription in whole. The prompt given will focus on a holistic summary for people to look over, including bullet points and a Q&A section.

#### Future Features:
- Implementing Gemini via the API
- Separate prompts/calls for summary, bullet points, and Q&A
- Automatic detection of primary lead/speakers and their duration of speaking.