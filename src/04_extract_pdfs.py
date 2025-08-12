import pymupdf
import pathlib


def extract_pdf_content(file):
    """
    Extract text and images from a PDF file.

    Args:
        file (str): Path to the PDF file.
    """

    # Create a directory for the output based on the PDF file name
    file_stem = pathlib.Path(file).stem
    output_dir = pathlib.Path("pdf_contents") / file_stem
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_file = pymupdf.open(file)

    text_content = ""

    for page_index in range(len(pdf_file)):
        page = pdf_file.load_page(page_index)
        text_content += page.get_text()

        image_list = page.get_images(full=True)

        if image_list:
            print(f"Found {len(image_list)} images on page {page_index}")
        else:
            print(f"No images found on page {page_index}")

        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]

            image_filename = f"image_page_{page_index}_img_{image_index}.{image_ext}"
            with open(output_dir / image_filename, "wb") as image_file:
                image_file.write(image_bytes)

    pdf_file.close()

    with open(output_dir / "extracted_text.txt", "w", encoding="utf-8") as text_file:
        text_file.write(text_content)


if __name__ == "__main__":
    """
    Eventual real use case for extracting text from PDFs.

    pdf_files = list(pathlib.Path("downloaded_papers").glob("*.pdf"))
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}")
        extract_pdf_content(pdf_file)
    print("PDF content extraction completed.")
    """

    # Example usage
    example_pdf = "A burden of rare variants in BMPR2 and KCNK3 contributes to a risk of familial pulmonary arterial hypertension.pdf"
    extract_pdf_content(example_pdf)
