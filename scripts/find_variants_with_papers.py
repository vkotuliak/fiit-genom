import ast
import pandas as pd
import os


"""
1. Take the citation from the clinvar_csv_dataset file.
2. Try to look it up in the pubmed_abstracts file.
3. If it exists in pubmed_abstracts, try getting its doi
4. Search paper by doi

Save list of PubMed ids, for which for all citations which have doi, the paper is downloaded
"""


def check_if_paper_exists(doi: str, pdf_dir: str) -> bool:
    """Checks if a PDF for a given DOI exists in the specified directory."""
    if not doi or not isinstance(doi, str):
        return False
    # Sanitize DOI to create a valid filename
    filename = doi.replace("https://doi.org/", "").replace("/", "%2F") + ".pdf"
    filepath = os.path.join(pdf_dir, filename)
    return os.path.exists(filepath)


def find_downloaded_papers() -> list:
    """
    Identifies PubMed IDs from ClinVar for which a corresponding PDF has been downloaded.
    """
    clinvar_df = pd.read_csv("data/clinvar_csv_dataset.csv", nrows=1000)
    pubmed_df = pd.read_csv("data/pubmed_abstracts.csv")

    pmids_w_downloaded = []
    counter = 1
    for pmed_ids, var_id in zip(clinvar_df["Citations"], clinvar_df["VariationID"]):

        if counter % 100 == 0:
            print(f"processing {counter}/10000")
        counter += 1

        all_downloaded = True
        check_further = True
        # if downloaded_no + not_in_csv_no == total_no then all the present articles which have pubmed id were downloaded
        total_no = len(ast.literal_eval(pmed_ids))
        downloaded_no = 0
        not_in_csv_no = 0

        for p_id in ast.literal_eval(pmed_ids):
            match = pubmed_df[
                (pubmed_df["PMID"] == int(p_id))
                & (pubmed_df["DOI"].notna())
                & (pubmed_df["DOI"] != "")
            ]
            if not match.empty:
                doi = match.iloc[0]["DOI"]
                if check_if_paper_exists(doi, "papers_by_doi"):
                    downloaded_no += 1
            
            elif match.empty:
                not_in_csv_no += 1
        
        # if downloaded_no + not_in_csv_no == total_no and downloaded_no > 0:
        #     pmids_w_downloaded.append(var_id)

        if downloaded_no == total_no and total_no >= 2:
            pmids_w_downloaded.append(var_id)

    return pmids_w_downloaded


if __name__ == "__main__":
    downloaded_pmids = find_downloaded_papers()
    print(f"Downloaded PMIDs: {downloaded_pmids}")
