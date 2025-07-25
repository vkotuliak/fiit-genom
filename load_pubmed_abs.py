import requests
import xml.etree.ElementTree as ET
import csv


def fetch_pubmed_abstract(pmids):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    root = ET.fromstring(response.text)

    abstracts = []
    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID")
        abstract_texts = article.findall(".//AbstractText")
        abstract = " ".join([el.text or "" for el in abstract_texts])
        abstracts.append((pmid, abstract))

    return abstracts


with open('test.csv', newline='', encoding='utf-8') as f_in, open('pubmed_abstracts.csv', 'w', newline='', encoding='utf-8') as f_out:
    writer = csv.writer(f_out)
    writer.writerow(['VariationID', 'VariationName', 'Abstract'])

    reader = csv.DictReader(f_in)
    for row in reader:
        pmid = row.get('Citations')
        variation_id = row.get('VariationID')
        variation_name = row.get('VariationName')
        if pmid:
            abstracts = fetch_pubmed_abstract([pmid])
            writer.writerow([variation_id, variation_name, abstracts])

