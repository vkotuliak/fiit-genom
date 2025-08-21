import pandas as pd
import ast
import nltk
from pathlib import Path
import sys

from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from s04_extract_pdfs import extract_pdf_content
from unstructured.cleaners.core import group_broken_paragraphs

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.append(project_root)

from scripts.structure_data import clean_raw_text

# nltk.download('punkt')
# nltk.download('punkt_tab')
# nltk.download('stopwords')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger_eng')


def safe_literal_eval(s):
    """Safely evaluate a string to a Python literal, handling NaNs and errors."""
    if pd.isna(s):
        return []
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return []


def aggregate_data(variation_id: int) -> str:
    """Aggregate data from comments, abstracts, and citations for a given variation ID."""
    outcome = ""

    clinvar_df = pd.read_csv("data/clinvar_csv_dataset.csv")
    clinvar_df_filtered = clinvar_df[clinvar_df["VariationID"] == variation_id]

    comment = clinvar_df_filtered["Comment"].values[0]
    comment = ast.literal_eval(comment)
    outcome += "COMMENT:" + "\n"
    outcome += str(comment[0]) if comment else "" + "\n"

    outcome += "\n" + "---" + "\n"

    abstracts_df = pd.read_csv("data/pubmed_abstracts.csv")
    pubmed_ids = clinvar_df_filtered["Citations"].values[0]
    pubmed_ids = ast.literal_eval(pubmed_ids)

    counter = 0
    for pubmed_id in pubmed_ids:
        outcome += f"PAPER {counter + 1}" + "\n"
        counter += 1
        row = abstracts_df.loc[
            abstracts_df["PMID"] == int(pubmed_id), ["Abstract", "DOI"]
        ]

        if not row["DOI"].empty:
            doi = (
                str(row["DOI"].values[0])
                .replace("https://doi.org/", "")
                .replace("/", "%2F")
                + ".pdf"
            )
            doi = "papers_by_doi/" + doi
            pdf_content = extract_pdf_content(doi)
            pdf_content = group_broken_paragraphs(pdf_content)
            pdf_content = clean_raw_text(pdf_content)
            if pdf_content == "Not Provided \n" and not row["Abstract"].empty:
                outcome += "ABSTRACT:" + "\n"
                outcome += str(row["Abstract"].values[0]) + "\n"
            else:
                outcome += "FULL PAPER TEXT:" + "\n"
                outcome += pdf_content + "\n"
        else:
            outcome += "ABSTRACT:" + "\n"
            if not row["Abstract"].empty:
                outcome += str(row["Abstract"].values[0]) + "\n"

    with open(f"aggregated_data_{variation_id}.txt", "w", encoding="utf-8") as f:
        f.write(outcome)
    return outcome


def get_wordnet_pos(treebank_tag):
    """Convert treebank tags to wordnet tags."""
    if treebank_tag.startswith("J"):
        return wordnet.ADJ  # adjective
    elif treebank_tag.startswith("V"):
        return wordnet.VERB  # verb
    elif treebank_tag.startswith("N"):
        return wordnet.NOUN  # noun
    elif treebank_tag.startswith("R"):
        return wordnet.ADV  # adverb
    else:
        return wordnet.NOUN  # default to noun


def remove_stopwords_and_lemmatize(text: str) -> str:
    """Remove stopwords from a given text and lemmatize the remaining words."""

    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words("english"))

    tokens = word_tokenize(text)
    tagged_tokens = nltk.pos_tag(tokens)
    filtered_and_lemmatized_tokens = []

    for word, tag in tagged_tokens:
        clean_word = word.lower()  # TODO: this might lower accuracy of model
        if clean_word.isalpha() and clean_word not in stop_words:
            pos = get_wordnet_pos(tag)
            lemmatized_word = lemmatizer.lemmatize(clean_word, pos)
            filtered_and_lemmatized_tokens.append(lemmatized_word)

    return " ".join(filtered_and_lemmatized_tokens)


def main():
    variation_id = 3254
    aggregated_data = aggregate_data(variation_id)
    # cleaned_data = remove_stopwords_and_lemmatize(aggregated_data)
    print(f"Cleaned Data for Variation ID {variation_id}:\n{aggregated_data}")


if __name__ == "__main__":
    main()
