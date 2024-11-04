import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(module)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger("NotebookLM")


def check_file_content(file_path):
    path = Path(file_path)

    if not path.exists:
        print(f"{file_path} not exist.")
        return None

    try:
        content = path.read_text(encoding='utf-8')
        if not content.strip():
            print(f"{file_path} is empty.")
            return None
        else:
            return content
    except IOError as e:
        print(f"读取文件时出错: {e}")
        return None


def read_file_to_string(filename):
    # Try UTF-8 first (most common encoding for text files)
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except UnicodeDecodeError:
        # If UTF-8 fails, try with other common encodings
        encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as file:
                    content = file.read()
                print(f"Successfully read file using {encoding} encoding.")
                return content
            except UnicodeDecodeError:
                continue

        print(f"Error: Could not decode file '{filename}' with any common encoding.")
        return None
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except IOError:
        print(f"Error: Could not read file '{filename}'.")
        return None
