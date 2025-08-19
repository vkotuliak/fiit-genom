from pathlib import Path
import sys

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.append(project_root)

from src.s04_extract_pdfs import extract_pdf_content


def process_first_n_papers(dir_path="papers_by_doi", n=1000):
    """
    Check the first n papers in the directory papers_by_doi.
    See if they can be read and have more than 10 words.
    
    Args:
        dir_path (str): Path to the directory containing PDF files.
        n (int): Number of files to process.
    """

    p = Path(dir_path)
    if not p.exists():
        raise FileNotFoundError(f"Directory not found: {dir_path}")
    files = [f for f in p.iterdir() if f.is_file()][:n]

    results = {}
    counter = 1
    for f in files:
        print(f"Processing {f.name} ({counter}/{len(files)})")
        try:
            text = extract_pdf_content(f)
            if len(text.split()) < 10:
                print(f"Paper {f} has less than 10 words.")
            # else:
            #     print(f"Paper {f} has {len(text.split())} words.")
        except Exception as e:
            print(f"Error processing {f}: {e}")
        counter += 1
    return results

if __name__ == "__main__":
    process_first_n_papers()