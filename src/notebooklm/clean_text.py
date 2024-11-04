import os
from pathlib import Path
from typing import Optional

import PyPDF2
import weave
from tqdm import tqdm

from notebooklm.models.models import load_clean_text_model, load_prompt
from .utils import check_file_content, logger


def validate_pdf(file_path: str) -> bool:
    if not os.path.exists(file_path):
        print(f"Error: File not found at path: {file_path}")
        return False
    if not file_path.lower().endswith('.pdf'):
        print("Error: File is not a PDF")
        return False
    return True


def extract_text_from_pdf(file_path: str, max_chars: int = 100000) -> Optional[str]:
    if not validate_pdf(file_path):
        return None

    try:
        with open(file_path, 'rb') as file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(file)

            # Get total number of pages
            num_pages = len(pdf_reader.pages)
            print(f"Processing PDF with {num_pages} pages...")

            extracted_text = []
            total_chars = 0

            # Iterate through all pages
            for page_num in range(num_pages):
                # Extract text from page
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                # Check if adding this page's text would exceed the limit
                if total_chars + len(text) > max_chars:
                    # Only add text up to the limit
                    remaining_chars = max_chars - total_chars
                    extracted_text.append(text[:remaining_chars])
                    print(f"Reached {max_chars} character limit at page {page_num + 1}")
                    break

                extracted_text.append(text)
                total_chars += len(text)
                print(f"Processed page {page_num + 1}/{num_pages}")

            final_text = '\n'.join(extracted_text)
            print(f"\nExtraction complete! Total characters: {len(final_text)}")
            return final_text

    except PyPDF2.PdfReadError:
        print("Error: Invalid or corrupted PDF file")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None


# Get PDF metadata
def get_pdf_metadata(file_path: str) -> Optional[dict]:
    if not validate_pdf(file_path):
        return None

    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            metadata = {
                'num_pages': len(pdf_reader.pages),
                'metadata': pdf_reader.metadata
            }
            return metadata
    except Exception as e:
        print(f"Error extracting metadata: {str(e)}")
        return None


def pdf2txt(file: str, output: str, verbose: bool = True) -> str:
    if verbose:
        print("Extracting metadata...")
        metadata = get_pdf_metadata(file)
        if metadata:
            print("\nPDF Metadata:")
            print(f"Number of pages: {metadata['num_pages']}")
            print("Document info:")
            for key, value in metadata['metadata'].items():
                print(f"{key}: {value}")

    # Extract text
    print("\nExtracting text...")
    extracted_text = extract_text_from_pdf(file)

    if verbose:
        # Display first 500 characters of extracted text as preview
        if extracted_text:
            print("\nPreview of extracted text (first 500 characters):")
            print("-" * 50)
            print(extracted_text[:500])
            print("-" * 50)
            print(f"\nTotal characters extracted: {len(extracted_text)}")

        # Optional: Save the extracted text to a file
        if extracted_text:
            output_file = Path(output) / 'extracted_text.txt'
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print(f"\nExtracted text has been saved to {output_file}")

    return extracted_text


def create_word_bounded_chunks(text, target_chunk_size):
    """
    Split text into chunks at word boundaries close to the target chunk size.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1  # +1 for the space
        if current_length + word_length > target_chunk_size and current_chunk:
            # Join the current chunk and add it to chunks
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


@weave.op()
def clean_text(content: str, output: str, verbose=False) -> str:
    CHUNK_SIZE = 1000  # Adjust chunk size if needed

    chunks = create_word_bounded_chunks(content, CHUNK_SIZE)
    num_chunks = len(chunks)

    client = load_clean_text_model()
    prompt = load_prompt("clean.txt")

    processed_text = ""
    with open(output, 'w', encoding='utf-8') as out_file:
        for chunk_num, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
            # Process chunk and append to complete text
            processed_chunk = processed_text = client.generate(
                system_prompt=prompt,
                content=chunk,
            )
            processed_text += processed_chunk + "\n"

            # Write chunk immediately to file
            out_file.write(processed_chunk + "\n")
            out_file.flush()

    return processed_text


def read_and_clean_file(file: str, output, verbose: False = True) -> str:
    content = check_file_content(output)
    if content is not None:
        logger.info(f"clean file: {output}")
        return content

    if file.endswith(".pdf"):
        content = pdf2txt(file, output.parent, verbose=verbose)

    if content:
        content = clean_text(content, output)

    return content
