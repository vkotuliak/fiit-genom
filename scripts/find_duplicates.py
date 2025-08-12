import csv
import sys
from collections import Counter

csv.field_size_limit(10**7)


def find_duplicates(csv_file):
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        variation_ids = [row['VariationID'] for row in reader if 'VariationID' in row]
    counts = Counter(variation_ids)
    duplicates = [id for id, count in counts.items() if count > 1]
    print("Duplicate VariationIDs:")
    for id in duplicates:
        print(f"{id} (count: {counts[id]})")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_duplicates.py <csv_file>")
        sys.exit(1)
    find_duplicates(sys.argv[1])