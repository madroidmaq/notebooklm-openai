import argparse
import os
from pathlib import Path

import weave
from dotenv import load_dotenv

from .audio import generate_audio
from .clean_text import read_and_clean_file
from .rewrite import rewrite
from .transcript import transcript
from .utils import logger


def build_parser():
    parser = argparse.ArgumentParser(description="generate podcast")
    parser.add_argument(
        "--input-file",
        type=str,
        help="input file",
    )

    parser.add_argument(
        "--output",
        type=str,
        help="input dir",
        default='.',
    )

    return parser


@weave.op()
def generate_podcast(input_file, output_dir):
    logger.info("clean text ...")
    clean_text = output_dir / "clean_text.txt"
    read_and_clean_file(input_file, clean_text)

    logger.info("transcripting ...")
    transcript_output = output_dir / "transcript.txt"
    transcript_model = os.getenv("TRANSCRIPT_MODEL")
    transcript(
        input_file=clean_text,
        output=transcript_output,
        model=transcript_model,
    )

    logger.info("rewrite transcript ...")
    rewrite_output = output_dir / "rewrite.json"
    rewrite_model = os.getenv("REWRITE_MODEL")
    rewrite(
        input_file=transcript_output,
        output=rewrite_output,
        model=rewrite_model,
    )

    logger.info("generating audio ...")
    generate_audio(input_file=rewrite_output, output=output_dir)


def main():
    project_root = Path(__file__).resolve().parents[2]
    env_path = Path(project_root) / '.env'
    load_dotenv(dotenv_path=env_path, override=True)

    name = os.getenv("WANDB_PROJECT")
    if name is not None:
        weave.init(name)

    parser = build_parser()
    args = parser.parse_args()

    input_file = args.input_file
    file_name = Path(input_file).stem
    output_dir = Path(args.output) / file_name
    output_dir.mkdir(parents=True, exist_ok=True)

    generate_podcast(input_file, output_dir)


if __name__ == "__main__":
    main()
