import pandas as pd

df = pd.read_csv("data/pubmed_abstracts.csv")

second_collumn = df.iloc[:, 1]

with open("dois.txt", "w") as f:
    for val in second_collumn:
        if pd.isna(val):
            continue
        else:
            clean_val = str(val).replace("https://doi.org/", "", 1)
            f.write(f"{clean_val}\n")
