## Usage

To work with the **ClinVar** database you first need to download it through following [link](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/). After downloading, you can use file `clinvar_xml_to_csv.py` to turn it into csv (you will need to change the name of file to *clinvar_dataset.xml.gz* or change it in code).

To extract all the abstracts from PubMed database, which will also be used for training of the model, use file `fetch_pubmed_abstracts.py`. This will take all the unique pubmed references from the file `clinvar_csv_dataset.csv` and load abstract for each paper. We have decided to work only with PubMed articles, since they comprise majority of all the citations. To check this yourself, you can use file `analyze_citation_sources.py`.

You can use file `make_graphics.py` to draw different graphics about the csv with clinvar data.

There are also files `clinvar_preview.py` and `example.xml` which are just short snippets from the original xml saved in clinvar database.
