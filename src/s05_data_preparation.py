import pandas as pd
import ast
import nltk
import string

from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

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
    outcome += str(comment[0]) if comment else ""

    abstracts_df = pd.read_csv("data/pubmed_abstracts.csv")
    pubmed_ids = clinvar_df_filtered["Citations"].values[0]
    pubmed_ids = ast.literal_eval(pubmed_ids)

    for pubmed_id in pubmed_ids:
        abstract_info = abstracts_df.loc[
            abstracts_df["PMID"] == int(pubmed_id), "Abstract"
        ]
        if not abstract_info.empty:
            outcome += str(abstract_info.values[0])  # + '\n'

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
    variation_id = 569
    aggregated_data = aggregate_data(variation_id)
    # cleaned_data = remove_stopwords_and_lemmatize(aggregated_data)
    print(f"Cleaned Data for Variation ID {variation_id}:\n{aggregated_data}")


if __name__ == "__main__":
    main()
