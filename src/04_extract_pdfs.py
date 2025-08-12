import pymupdf


file = "3_-UTR variations and G6PD deficiency.pdf"

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

        with open(
            f"image_page_{page_index}_img_{image_index}.{image_ext}", "wb"
        ) as image_file:
            image_file.write(image_bytes)
            print(f"Saved image {image_index} from page {page_index} as {image_ext}")

pdf_file.close()

with open("extracted_text.txt", "w", encoding="utf-8") as text_file:
    text_file.write(text_content)
