import os
from pathlib import Path

from openai import OpenAI


class Model:

    def generate(self, text: str, max_output_tokens: int = 1024) -> str:
        pass


class OpenAIModel(Model):
    api_key: str
    base_url: str
    model_id: str = "gpt-4o"
    prompt: str
    temperature: float = 0.7
    top_p = 0.9
    client: OpenAI

    def __init__(self, model_id: str, api_key: str, base_url: str, prompt: str):
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url
        self.prompt = prompt

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=60 * 3
        )

    def generate(self, text: str, max_output_tokens: int = 1024) -> str:
        response = self.client.chat.completions.create(
            model=self.model_id,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": text},
            ]
        )
        return response.choices[0].message.content


def _load_prompt(file_name) -> str:
    with open(Path(file_name), 'r') as file:
        system_prompt = file.read()

    return system_prompt


def load_model_client() -> Model:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_API_BASE")
    base_url = "http://localhost:11434/v1"

    prompt = _load_prompt("prompts/clean.txt")

    openai_lm = OpenAIModel(
        model_id='qwen2.5:3b',
        base_url=base_url,
        api_key=api_key,
        prompt=prompt,
    )

    return openai_lm
