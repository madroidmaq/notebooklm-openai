import os
from importlib import resources

from openai import OpenAI

from .text_models import TextModel, OpenAITextModel


def load_prompt(file_name) -> str:
    with resources.open_text("notebooklm.prompts", file_name) as file:
        system_prompt = file.read()
    return system_prompt


def load_text_model(model) -> TextModel:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=10 * 60
    )

    openai_lm = OpenAITextModel(
        model_id=model,
        client=client
    )

    return openai_lm


def load_clean_text_model() -> TextModel:
    model_id = os.getenv("CLEAN_TEXT_MODEL")
    return load_text_model(model=model_id)


def load_transcript_model() -> TextModel:
    model_id = os.getenv("TRANSCRIPT_MODEL")
    return load_text_model(model=model_id)


def load_rewrite_model() -> TextModel:
    model_id = os.getenv("REWRITE_MODEL")
    return load_text_model(model=model_id)
