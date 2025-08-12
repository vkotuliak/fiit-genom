import gzip
import xml.etree.ElementTree as ET

def quick_preview(filename):
    with gzip.open(filename, 'rt') as f:
        sample = f.read(30000)
        print("First 30KB of XML structure:")
        print(sample)

quick_preview('clinvar_dataset.xml.gz')