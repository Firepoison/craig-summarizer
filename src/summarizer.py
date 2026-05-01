# Standard/Python imports
import os

# 3rd party imports
from google import genai
from google.genai import types


class Summarizer():
    def __init__(self, model_name="gemini-3-flash-preview"):
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

    def summarize(self, transcription):
        """
        Generates a summary of a given transcription using the Gemini model.

        Args:
            transcription (str): The transcription text to be summarized.

        Returns:
            str: The generated summary text.
        """

        prompt = self._prompt_builder(transcription)

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_level="medium")
        )

        response = self._client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config
        )

        return response.text

