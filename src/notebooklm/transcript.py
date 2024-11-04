import weave

from notebooklm.models.models import load_transcript_model, load_prompt
from .utils import read_file_to_string, check_file_content, logger


@weave.op()
def transcript(input_file, output, model: str) -> str:
    content = check_file_content(output)
    if content is not None:
        logger.info(f"transcript file: {output}")
        return content

    content = read_file_to_string(input_file)
    client = load_transcript_model()
    prompt = load_prompt("transcript.txt")
    response = client.generate(
        system_prompt=prompt,
        content=content,
        # max_output_tokens=1024,
        max_output_tokens=1024 * 8
    )

    with open(output, 'w', encoding='utf-8') as out_file:
        out_file.write(response + "\n")

    logger.info(f"write transcript to {output}")

    return response
