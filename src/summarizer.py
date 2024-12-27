# Standard/Python imports
import os

# 3rd party imports
import google.generativeai as genai


class Summarizer():
    def __init__(self):
        self._gemini_model = None

    def _gemini_connect(self) -> genai.GenerativeModel:
        if self._gemini_model is None:
            # Get Gemini key from env
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set.")

            genai.configure(api_key=api_key)
            self._gemini_model = genai.GenerativeModel("gemini-1.5-pro")
        return self._gemini_model

    def _prompt_builder(self):
        return """
        You are an expert writer listening into Discord meeting of people within
        an Eve Online Alliance. You are tasked with giving a thorough but brief
        summary of what was discussed, established, and talked over within the
        meeting.

        You will give a meeting topic at the heading of the summary, a brief summary
        of the meeting, and then bullent points detailing major facts and discussion
        points. Include any major decisions or action items that should be taken by
        alliance members.

        Summary:
        """

    def summarize(self, transcription):
        gemini = self._gemini_model
        prompt = self._prompt_builder()

        response = gemini.generate_content([
            prompt,
            transcription
        ])

        print(response.text)
