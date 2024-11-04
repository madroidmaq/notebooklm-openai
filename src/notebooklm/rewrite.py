import weave

from notebooklm.models.models import load_rewrite_model, load_prompt
from .utils import read_file_to_string, check_file_content, logger


@weave.op()
def rewrite(input_file, output, model: str):
    content = check_file_content(output)
    if content is not None:
        logger.info(f"rewrite transcript file: {output}")
        return content

    content = read_file_to_string(input_file)
    client = load_rewrite_model()
    prompt = load_prompt("rewrite.txt")

    response = client.generate(
        system_prompt=prompt,
        content=content,
        # max_output_tokens=1024,
        max_output_tokens=1024 * 10
    )

    output_file = output
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write(response + "\n")

    logger.info(f"rewrite transcript to {output_file}")

    return response
