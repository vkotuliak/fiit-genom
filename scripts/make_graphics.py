import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('clinvar_csv_dataset.csv')

# Display the 10 most common values in the 'ClinicalSignificance' column
column_name = 'ClinicalSignificance'

# Split the values in the column by semicolon since there are multiple values in one cell
all_values = df[column_name].dropna().apply(lambda x: [v.strip() for v in str(x).split(';')])
flat_values = [item for sublist in all_values for item in sublist]

value_counts = pd.Series(flat_values).value_counts()

print(value_counts)

top_10 = value_counts.head(10)

plt.figure(figsize=(10, 6))
top_10.plot(kind='barh')
plt.title(f'Top 10 Value Counts for "{column_name}"')
plt.xlabel('Frequency')
plt.ylabel('Values')
plt.tight_layout()
plt.show()


# Display the value count for the 'Type' column
type_counts = df['Type'].value_counts()
print(type_counts)

plt.figure(figsize=(10, 6))
type_counts.plot(kind='barh')
plt.title(f'Value Counts for Type')
plt.xlabel('Frequency')
plt.ylabel('Values')
plt.tight_layout()
plt.show()


# Display the top 20 value counts for the 'GeneSymbol' column
gene_symbol_counts = df['GeneSymbol'].value_counts()
print(gene_symbol_counts)

top_20_gene_symbols = gene_symbol_counts.head(20)

plt.figure(figsize=(10, 6))
top_20_gene_symbols.plot(kind='barh')
plt.title(f'Top 20 Value Counts for Gene Symbol')
plt.xlabel('Frequency')
plt.ylabel('Values')
plt.tight_layout()
plt.show()


# Display the value counts for the 'ReviewStatus' column
review_status_counts = df['ReviewStatus'].value_counts()
print(review_status_counts)

plt.figure(figsize=(10, 6))
review_status_counts.plot(kind='barh')
plt.title(f'Value Counts for Review Status')
plt.xlabel('Frequency')
plt.ylabel('Values')
plt.tight_layout()
plt.show()


# Display the top 50 value counts for the 'Condition' column
condition_counts = df['Condition'].value_counts()
print(condition_counts)

top_50_conditions = condition_counts.head(50)
print(top_50_conditions)

plt.figure(figsize=(10, 6))
top_50_conditions.plot(kind='barh')
plt.title(f'Top 50 Value Counts for Condition')
plt.xlabel('Frequency')
plt.ylabel('Values')
plt.tight_layout()
plt.show()


# Display the binned value counts for the 'NumberOfSubmissions' column
bins = [0, 1, 5, 10, 50, 100, 500, 1000, df['OriginCounts'].astype(int).max() + 1]
labels = ['1', '2-5', '6-10', '11-50', '51-100', '101-500', '501-1000', '1001+']
origin_counts_binned = pd.cut(df['OriginCounts'].astype(int), bins=bins, labels=labels, right=False)
binned_counts = origin_counts_binned.value_counts().sort_index()

print(binned_counts)

plt.figure(figsize=(10, 6))
ax = binned_counts.plot(kind='bar')
plt.title('Binned Value Counts for Number of Submissions')
plt.xlabel('Number of Submissions Range')
plt.ylabel('Frequency')
plt.tight_layout()
plt.show()
