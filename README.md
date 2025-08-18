## Usage

To work with the **ClinVar** database you first need to download it through following [link](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/). After downloading, you can use file `src/s01_clinvar_xml_to_csv.py` to turn it into csv (you will need to change the name of file to *clinvar_dataset.xml.gz* or change it in code).

To extract all the abstracts from PubMed database, which will also be used for training of the model, use file `src/s03_fetch_pubmed_abstracts.py`. This will take all the unique pubmed references from the file `data/clinvar_csv_dataset.csv` and load abstract for each paper. We have decided to work only with PubMed articles, since they comprise majority of all the citations. To check this yourself, you can use file `src/s02_analyze_citation_sources.py`.

For training of the model, we will also use contents of all the linked pdfs. To download these, we used *PyPaperBot* with following command:

```
python3 -m PyPaperBot --doi-file="dois.txt" --dwn-dir="./papers_by_doi --use-doi-as-filename
```

DOIs can be saved into file `dois.txt` using file `scripts/make_doi_txt.py`, and using *--use-doi-as-filename* will make it easier for latter retrieval. 

To extract text from these PDFs there is file `src/s04_extract_pdfs.py`.
You can use `src/s05_data_preparation.py` to preprocess and organize the data from previous steps, making it ready for analysis and modeling. Once the data is prepared, `src/s06_LLM_analysis.py` can be used to perform analysis with large language models (LLMs) on the processed dataset. Run these scripts in sequence after extracting abstracts and PDF contents to complete the data pipeline.

---

You can use file `scripts/make_graphics.py` to draw different graphics about the csv with clinvar data.

There are also files `scripts/clinvar_preview.py` and `data/example.xml` which are just short snippets from the original xml saved in clinvar database.
