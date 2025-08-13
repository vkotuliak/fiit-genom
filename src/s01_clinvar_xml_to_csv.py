import gzip
import csv
from lxml import etree

def extract_variation_data(variation_elem):
    """Extract all variation data from a VariationArchive element"""
    record = {
        'VariationID': variation_elem.get('VariationID', ''),
        'VariationName': variation_elem.get('VariationName', ''),
        'AlleleID': '',
        'Type': variation_elem.get('VariationType', ''),
        'GeneSymbol': '',
        'ClinicalSignificance': '',
        'ReviewStatus': '',
        'Condition': '',
        'HGVS_c': '',
        'HGVS_p': '',
        'dbSNP_ID': '',
        'NumberOfSubmissions': '',
        'Comment': '',
        'Citations': []
    }
    
    simple_allele = variation_elem.find('.//SimpleAllele')
    if simple_allele is not None:
        record['AlleleID'] = simple_allele.get('AlleleID', '')

        gene_elem = simple_allele.find('.//Gene')
        if gene_elem is not None:
            record['GeneSymbol'] = gene_elem.get('Symbol', '')
        
        hgvs_coding = simple_allele.find('.//HGVS[@Type="coding"]/NucleotideExpression')
        if hgvs_coding is not None:
            record['HGVS_c'] = hgvs_coding.get('change', '')
        
        hgvs_protein = simple_allele.find('.//HGVS[@Type="coding"]/ProteinExpression')
        if hgvs_protein is not None:
            record['HGVS_p'] = hgvs_protein.get('change', '')
        
        dbsnp_xref = simple_allele.find('.//XRef[@DB="dbSNP"]')
        if dbsnp_xref is not None:
            record['dbSNP_ID'] = dbsnp_xref.get('ID', '')

    germline_class = variation_elem.find('.//Classifications/GermlineClassification')
    if germline_class is not None:
        desc_elem = germline_class.find('./Description')
        if desc_elem is not None:
            record['ClinicalSignificance'] = desc_elem.text or ''
        
        review_elem = germline_class.find('./ReviewStatus')
        if review_elem is not None:
            record['ReviewStatus'] = review_elem.text or ''
            
    classified_condition = variation_elem.find('.//ClassifiedCondition')
    if classified_condition is not None:
        record['Condition'] = classified_condition.text or ''

    number_of_submissions = variation_elem.find('.//Classifications/GermlineClassification')
    if number_of_submissions is not None:
        record['NumberOfSubmissions'] = number_of_submissions.get('NumberOfSubmissions', '') or ''
    
    comments = variation_elem.findall('.//Attribute[@Type="Description"]')
    other_comments = variation_elem.findall('.//Comment', '')
    record['Comment'] = []
    if comments:
        record['Comment'].extend([comment.text for comment in comments if comment.text])
    if other_comments:
        record['Comment'].extend([comment.text for comment in other_comments if comment.text])

    citations = variation_elem.findall('.//Citation')
    if citations:
        id_elems = [citation.find('.//ID[@Source="PubMed"]') for citation in citations]
        pubmed_ids = list(set([id_elem.text for id_elem in id_elems if id_elem is not None]))
        if pubmed_ids:
            record['Citations'] = pubmed_ids

    return record

with gzip.open('clinvar_dataset.xml.gz', 'rb') as f_in, open('clinvar_csv_dataset.csv', 'w', newline='', encoding='utf-8') as f_out:
    all_fields = [
        'VariationID',
        'VariationName',
        'AlleleID', 
        'Type',
        'GeneSymbol',
        'ClinicalSignificance',
        'ReviewStatus',
        'Condition',
        'HGVS_c',
        'HGVS_p',
        'dbSNP_ID',
        'NumberOfSubmissions',
        'Comment',
        'Citations'
    ]
    
    writer = csv.DictWriter(f_out, fieldnames=all_fields)
    writer.writeheader()
    
    context = etree.iterparse(f_in, events=('start', 'end'))
    count = 0
    
    for event, elem in context:
        if event == 'end' and elem.tag == 'VariationArchive':
            record = extract_variation_data(elem)
            writer.writerow(record)
            count += 1
            
            if count % 1000 == 0:
                print(f'Processed {count} elements')
            
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
    
    del context
    print(f'Done. Total {count} elements processed.')
    