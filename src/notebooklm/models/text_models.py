import weave
from openai import OpenAI


class TextModel:

    def generate(self, system_prompt: str, content: str, max_output_tokens: int = 1024) -> str:
        pass


class OpenAITextModel(TextModel):
    model_id: str = "gpt-4o"
    prompt: str
    temperature: float = 0.0
    top_p = 0.9
    client: OpenAI

    def __init__(self, model_id: str, client: OpenAI):
        self.model_id = model_id
        self.client = client

    @weave.op()
    def generate(self, system_prompt: str, content: str, max_output_tokens: int = 1024) -> str:
        print(f"max_output_tokens: {max_output_tokens}")
        response = self.client.chat.completions.create(
            model=self.model_id,
            temperature=self.temperature,
            max_tokens=max_output_tokens,
            top_p=self.top_p,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ]
        )
        return response.choices[0].message.content
