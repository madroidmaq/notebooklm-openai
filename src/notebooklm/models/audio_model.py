import base64
import os

import weave
from openai import OpenAI


class AudioModel:

    def generate_audio(self, system_prompt: str, voice: str, content: str, output_file):
        pass


def save_base64_audio(base64_data, output_file_path):
    try:
        audio_bytes = base64.b64decode(base64_data)
    except base64.binascii.Error as e:
        raise ValueError(f"Base64 decode filed: {e}")

    try:
        with open(output_file_path, "wb") as audio_file:
            audio_file.write(audio_bytes)
    except IOError as e:
        raise IOError(f"save audio fiel error: {e}")


class OpenAIAudioModel(AudioModel):
    model_id: str = "gpt-4o-audio-preview"
    prompt: str
    client: OpenAI

    def __init__(self, client: OpenAI, model_id: str = "gpt-4o-audio-preview"):
        self.model_id = model_id
        self.client = client

    @weave.op()
    def generate_audio(self, system_prompt: str, voice: str, content: str, output_file):
        response = self.client.chat.completions.create(
            model=self.model_id,
            modalities=["text", "audio"],
            audio={"voice": voice, "format": "wav"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content},
            ]
        )
        message = response.choices[0].message
        save_base64_audio(message.audio.data, output_file)


from f5_tts_mlx.generate import generate


class MlxAudioModel(AudioModel):
    model: str

    def __init__(self, model: str):
        self.model = model

    @weave.op()
    def generate_audio(self, system_prompt: str, voice: str, content: str, output_file):
        generate(
            generation_text=content,
            output_path=output_file,
            model_name=self.model
        )


def load_audio_model() -> AudioModel:
    model = os.getenv("AUDIO_MODEL")

    return MlxAudioModel(model)
