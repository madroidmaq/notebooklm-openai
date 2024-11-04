from pathlib import Path

import weave
from pydub import AudioSegment
from tqdm import tqdm

from .models.audio_model import load_audio_model
from .models.audio_model import AudioModel

# from podcast.models import load_audio_model

SPEAK1 = """
As the first speaker in a podcast, generate audio based on the podcast script provided by the user.

# Tone and Style:

- Tone: Full of enthusiasm and engaging, like an experienced teacher communicating with students.
- Pace: Moderate, ensuring that the audience can clearly understand.
- Emotion: Show excitement and confidence when sharing anecdotes and analogies.
- Pauses: Appropriate pauses at key points and turns to enhance the expression effect.

# Notes

- When welcoming the audience, the tone should be particularly warm and friendly.
- When explaining complex concepts, use vivid intonation to help the audience understand.
- Generate audio content that is consistent with the script, do not be free in your interpretation.
"""

SPEAK2 = """
As the second speaker in a podcast, generate audio based on the podcast script provided by the user.

# Tone and Style:

- Tone: Full of curiosity, showing excitement or confusion, like a beginner eager to learn.
- Pace: Slightly fast, reflecting an urgent mood, but still clear.
- Emotion: When asking questions, show genuine interest or surprise.

Catchphrases: Appropriately insert interjections like "hm," "ah," etc., to reflect a natural conversation state.

# Notes:

- When the topic deviates, the tone can become more lively or curious.
- Generate audio content that is consistent with the script, do not be free in your interpretation.
"""


@weave.op()
def generate_speak1(model: AudioModel, content: str, output_file):
    model.generate_audio(
        system_prompt=SPEAK2,
        voice="ash",
        content=content,
        output_file=output_file,
    )


@weave.op()
def generate_speak2(model: AudioModel, content: str, output_file):
    model.generate_audio(
        system_prompt=SPEAK2,
        voice="nova",
        content=content,
        output_file=output_file,
    )


def load_transcript(input_file: str) -> list:
    import json

    # 读取 JSON 文件
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    return data


@weave.op()
def generate_audio(input_file, output):
    podcast_output_file = Path(output) / "audio.wav"
    if podcast_output_file.exists():
        print(F"audio path: {podcast_output_file}")
        return

    datas = load_transcript(input_file)
    audio_model = load_audio_model()

    output_path = Path(output)
    audio_dir = output_path / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    for index, data in tqdm(enumerate(datas, start=1), total=len(datas), desc="Generating Audio"):

        file_name = f"{index:03d}_{data['speaker']}.wav"
        file_path = audio_dir / file_name
        if data["speaker"] == "Speaker 1":
            generate_speak1(audio_model, data["dialogue"], file_path)

        if data["speaker"] == "Speaker 2":
            generate_speak1(audio_model, data["dialogue"], file_path)

    audio_files = sorted(audio_dir.glob("*.wav"))
    combined = AudioSegment.empty()
    for audio_file in tqdm(audio_files, desc="Merging Audio Files"):
        # 加载音频文件
        audio = AudioSegment.from_file(audio_file)
        combined += audio  # 追加到合并音频中

    combined.export(podcast_output_file, format="wav")
    print(f"所有音频文件已成功合并为: {podcast_output_file}")
