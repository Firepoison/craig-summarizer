# Standard/Python imports
import os

# 3rd party imports
import google.generativeai as genai


class Summarizer():
    def __init__(self):
        self._gemini_model = None
        self._gemini_connect()


    def _gemini_connect(self):
        if self._gemini_model is None:
            # Get Gemini key from env
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set.")

            genai.configure(api_key=api_key)
            self._gemini_model = genai.GenerativeModel("gemini-1.5-pro")

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

        gemini = self._gemini_model
        prompt = self._prompt_builder(transcription)

        response = gemini.generate_content(prompt)

        return response.text

