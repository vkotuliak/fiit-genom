from unstructured.cleaners.core import clean, replace_unicode_quotes


def clean_raw_text(raw_text: str) -> str:
    cleaned_text = clean(
        raw_text,
        extra_whitespace=True,
        dashes=True,
        bullets=False,
        trailing_punctuation=True,
        lowercase=False,
    )
    cleaned_text = replace_unicode_quotes(cleaned_text)

    # print(f"Successfully cleaned '{input_filename}' and saved it to '{output_filename}'.")
    return cleaned_text

input_filename = "aggregated_data_286.txt"
output_filename = "cleaned_data.txt"

