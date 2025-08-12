import pandas as pd
import ast


def safe_literal_eval(s):
    """Safely evaluate a string to a Python literal, handling NaNs and errors."""
    if pd.isna(s):
        return []
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return []

def aggregate_data(variation_id: int) -> str:
    """Aggregate data from comments, abstracts, and citations for a given variation ID."""
    outcome = ''

    # TODO - do not use ast on whole column, but rather on each row
    clinvar_df = pd.read_csv('data/clinvar_csv_dataset.csv', converters={'Citations': safe_literal_eval})
    clinvar_df_filtered = clinvar_df[clinvar_df['VariationID'] == variation_id]
    
    comment = clinvar_df_filtered['Comment'].values[0]
    if pd.notna(comment):
        outcome += str(comment) + '\n'

    abstracts_df = pd.read_csv('data/pubmed_abstracts.csv')
    pubmed_ids = clinvar_df_filtered['Citations'].values[0]
    
    for pubmed_id in pubmed_ids:
        abstract_info = abstracts_df.loc[abstracts_df['PMID'] == int(pubmed_id), 'Abstract']
        if not abstract_info.empty:
            outcome += str(abstract_info.values[0]) + '\n'
    
    return outcome

print(aggregate_data(287))

