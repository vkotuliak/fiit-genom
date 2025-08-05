import gzip
from lxml import etree


def analyze_sources(in_file):
    """Analyze the ratio of PubMed citations to other sources in the XML file."""

    pubmed = 0
    other = 0

    with gzip.open(in_file, "rb") as f:
        context = etree.iterparse(f, events=("end",))
        count = 0

        for _, elem in context:
            if elem.tag == "VariationArchive":
                germline_class = elem.find(".//Classifications/GermlineClassification")
                if germline_class is not None:
                    citation_elems = germline_class.findall("./Citation")
                    for cit in citation_elems:
                        id_elem = cit.find("./ID")
                        if id_elem is not None:
                            source = id_elem.get("Source")
                            if source and source.lower() == "pubmed":
                                pubmed += 1
                            else:
                                other += 1

                count += 1

                if count % 1000 == 0:
                    print(f"Processed {count} elements")

                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
        del context
        print(f"Done. Total {count} elements processed")
        print(f"PubMed citations: {pubmed}")
        print(f"Other citations: {other}")

"""
Results:
PubMed citations: 1019311
Other citations: 2728
Ratio of PubMed to other sources: 373:1
"""

def count_all_occurences(in_file):
    """Count all occurrences of citations in the XML file."""
    count = 0
    with gzip.open(in_file, "rb") as f:
        context = etree.iterparse(f, events=("end",))

        pubmed_arcs = set()
        other_arcs = set()

        for _, elem in context:
            if elem.tag == "VariationArchive":
                citation_elems = elem.findall(".//Citation")
                for cit in citation_elems:
                    id_elems = cit.findall("./ID")
                    for id_elem in id_elems:
                        source = id_elem.get("Source")
                        if source and source.lower() == "pubmed":
                            pubmed_arcs.add(id_elem.text)
                        else:
                            other_arcs.add(id_elem.text)

                count += 1
                if count % 1000 == 0:
                    print(f"Processed {count} elements")

                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
        del context
        print(f"Done. Total {count} elements processed")
        print(f"Total unique PubMed citations: {len(pubmed_arcs)}")
        print(f"Total unique Other citations: {len(other_arcs)}")
    return count

"""
Results:
Total 3595245 elements processed
Total unique PubMed citations: 128471
Total unique Other citations: 1864
Ratio of PubMed to other sources: 69:1
"""

if __name__ == "__main__":
    in_file = "clinvar_dataset.xml.gz"
    # in_file = "example.xml"
    # analyze_sources(in_file)
    count_all_occurences(in_file)
