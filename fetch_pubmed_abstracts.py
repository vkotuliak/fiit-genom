import csv
import pandas as pd
import ast
import requests
import xml.etree.ElementTree as ET
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import html

IN = "clinvar_csv_dataset.csv"
OUT = "pubmed_abstracts2.csv"
XML_DIR = "pubmed_xmls"


def collect_unique_pmids():
    """Collect unique PMIDs from the input CSV file."""
    all_pmids = set()
    df = pd.read_csv(IN)
    citations = df["Citations"]

    for cit in citations:
        if pd.isna(cit):
            continue
        try:
            cit = ast.literal_eval(cit)
            valid_pmids = [str(pmid) for pmid in cit if str(pmid).isdigit()]
            all_pmids.update(valid_pmids)
        except (ValueError, SyntaxError) as e:
            print(f"Error parsing citation: {cit}, Error: {e}")
            continue

    print(f"Collected {len(all_pmids)} unique PMIDs")
    return list(all_pmids)


def create_session():
    """Create a session with retry strategy"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def extract_text_content(element):
    """Extract all text content from an XML element, including nested elements"""
    if element.text:
        text = element.text
    else:
        text = ""

    # Get text from all child elements
    for child in element:
        if child.text:
            text += child.text
        if child.tail:
            text += child.tail

    # Decode HTML entities and normalize whitespace
    text = html.unescape(text)
    text = " ".join(text.split())

    return text


def load_abstracts(pmids: list, session: requests.Session, batch_number: int = None) -> list:
    """Function to load abstract from PubMed."""

    doi_counter = 0
    os.makedirs(XML_DIR, exist_ok=True)

    # Filter out empty or invalid PMIDs
    valid_pmids = [pmid for pmid in pmids if pmid and str(pmid).isdigit()]

    if not valid_pmids:
        print("No valid PMIDs to process")
        return []

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {"db": "pubmed", "id": ",".join(valid_pmids), "retmode": "xml"}

    try:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()

        # Handle encoding properly
        response.encoding = "utf-8"
        xml_content = response.text

        # Save each batch to separate file
        batch_filename = f"batch_{batch_number:04d}_{valid_pmids[0]}_to_{valid_pmids[-1]}.xml"
        xml_filepath = os.path.join(XML_DIR, batch_filename)
        
        with open(xml_filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        print(f"Saved XML batch to: {xml_filepath}")

        # Parse XML with proper error handling
        root = ET.fromstring(xml_content.encode("utf-8"))

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []
    except ET.ParseError as e:
        print(f"XML parsing failed: {e}")
        # Save problematic XML
        error_filename = f"error_batch_{batch_number:04d}.xml"
        error_filepath = os.path.join(XML_DIR, error_filename)
        with open(error_filepath, 'w', encoding='utf-8') as f:
            f.write(response.text if 'response' in locals() else 'No response data')
        print(f"Saved problematic XML to: {error_filepath}")
        return []

    abstracts = []
    articles_found = root.findall(".//PubmedArticle")

    print(f"Requested {len(valid_pmids)} PMIDs, found {len(articles_found)} articles")

    for article in articles_found:
        # article_xml_str = ET.tostring(article, encoding="unicode")
        # print(article_xml_str)
        pmid = article.findtext(".//PMID")
        abstract_texts = article.findall(".//AbstractText")
        doi = article.findtext(".//ELocationID[@EIdType='doi']")

        if abstract_texts:
            abstract_parts = []
            for el in abstract_texts:
                text_content = extract_text_content(el)
                if text_content:
                    abstract_parts.append(text_content)

            abstract = " ".join(abstract_parts)
        else:
            abstract = ""
            # print(f"No abstract found for PMID: {pmid}")

        if abstract:
            abstract = abstract.strip()

        if doi:
            # print(f"Found DOI: {doi} for PMID: {pmid}")
            doi_counter += 1
            doi = doi.strip()
            if not doi.startswith("http"):
                doi = f"https://doi.org/{doi}"
        else:
            # print(f"No DOI found for PMID: {pmid}")
            doi = ""

        abstracts.append((pmid, doi, abstract))

    # Check for missing PMIDs
    found_pmids = {str(pmid) for pmid, _, _ in abstracts}
    missing_pmids = set(str(pmid) for pmid in valid_pmids) - found_pmids
    if missing_pmids:
        print(f"Missing PMIDs (not found in PubMed): {len(missing_pmids)} PMIDs")
        print(f"Sample missing PMIDs: {list(missing_pmids)[:5]}")

    print(f"Total dois found: {doi_counter} out of {len(valid_pmids)-len(missing_pmids)}.")

    return abstracts


def all_abstracts_in_csv():
    """Main function to process all abstracts and write to CSV."""
    batch_size = 200
    delay = 0.34

    unique_pmids = collect_unique_pmids()
    if not unique_pmids:
        print("No PMIDs found to process")
        return

    session = create_session()
    all_data = []

    print(f"Processing {len(unique_pmids)} PMIDs in batches of {batch_size}")

    for i in range(0, len(unique_pmids), batch_size):
        batch = unique_pmids[i : i + batch_size]
        batch_number = i // batch_size + 1
        
        abstracts = load_abstracts(batch, session, batch_number)
        all_data.extend(abstracts)
        print(f"Processed {len(abstracts)} records, total so far: {len(all_data)}")

        if i + batch_size < len(unique_pmids):
            time.sleep(delay)

    # Write to CSV
    if all_data:
        df = pd.DataFrame(all_data, columns=["PMID", "DOI", "Abstract"])

        df.to_csv(
            OUT, index=False, encoding="utf-8", quoting=csv.QUOTE_ALL, escapechar="\\"
        )

        print(f"Successfully wrote {len(all_data)} records to {OUT}")

        empty_abstracts = df[df["Abstract"] == ""].shape[0]
        print(f"Records with empty abstracts: {empty_abstracts}")
    else:
        print("No data to write")


if __name__ == "__main__":
    all_abstracts_in_csv()

    # For testing purposes, we can run the function with a smaller set
    # session = create_session()
    # df = pd.read_csv('pubmed_abstracts.csv')
    # empty_abstracts = df[df['Abstract'].isnull() | (df['Abstract'].str.strip() == '')]
    # pmid_list = empty_abstracts['PMID'].astype(str).tolist()
    # load_abstracts(pmid_list, session)
