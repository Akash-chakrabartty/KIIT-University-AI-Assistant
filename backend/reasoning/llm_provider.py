"""Project responsibility: swappable LLM provider (adapter pattern).
pipeline.py only ever calls .generate(prompt) -- never touches Gemini
(or any other provider's) SDK directly."""


class LLMProvider:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str):
        from google import genai
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name

    def generate(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self._model_name, contents=prompt
        )
        return response.text
