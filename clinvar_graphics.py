import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('clinvar_csv.csv')

column_name = 'ClinicalSignificance'

value_counts = df[column_name].value_counts()

print(value_counts)

plt.figure(figsize=(10, 6))
value_counts.plot(kind='bar')
plt.title(f'Value Counts for "{column_name}"')
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()