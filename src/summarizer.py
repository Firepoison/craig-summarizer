# Standard/Python imports
import os
import time

# 3rd party imports
from google import genai
from google.genai import types, errors
import httpx


class Summarizer():
    def __init__(self, model_name="gemini-3.5-flash"):
        self._client = None
        self.model_name = model_name
        self._gemini_connect()

    def _gemini_connect(self):
        if self._client is None:
            # Get Gemini key from env
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set.")

            self._client = genai.Client(api_key=api_key)

    def _prompt_builder(self, transcription) -> str:
        return (
        "You are an expert writer listening into Discord meeting of people within"
        + "an Eve Online Alliance. You are tasked with giving a thorough but brief"
        + "summary of what was discussed, established, and talked over within the"
        + "meeting. "
        + "\n\n"
        + "Given the following transcription:\n"
        + transcription
        + "\n\n"
        + "You will give a meeting topic at the heading of the summary, a brief summary"
        + "of the meeting, and then bullent points detailing major facts and discussion"
        + "points. Include any major decisions or action items that should be taken by"
        + "the alliance members. "
        + "\n\n"
        + "Summary:\n"
        )

    def summarize_stream(self, transcription):
        """
        Generates a summary of a given transcription using the Gemini model in a streaming fashion.

        Args:
            transcription (str): The transcription text to be summarized.

        Yields:
            str: Chunks of the generated summary text.
        """

        prompt = self._prompt_builder(transcription)

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="medium")
        )

        max_retries = 6
        for attempt in range(max_retries):
            chunks_yielded = 0
            try:
                response = self._client.models.generate_content_stream(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )

                for chunk in response:
                    if chunk.text:
                        chunks_yielded += 1
                        yield chunk.text
                break  # Success, exit retry loop
            except (errors.ServerError, httpx.RemoteProtocolError) as e:
                # Only retry if we haven't yielded any chunks yet to avoid duplicate text
                if chunks_yielded > 0:
                    raise e
                    
                if attempt < max_retries - 1:
                    # Sleep longer to wait out demand spikes: 6s, 7s, 9s, 13s, 21s...
                    time.sleep((2 ** attempt) + 5)
                else:
                    raise e

