import pandas as pd

input_text = "Hi Taylor, this is {lead_first_name}. What can I help you with?"
df = pd.read_csv('RAG_examples/taylorSupplerUpgrade_RAG.csv')
output = df.loc[df['User Message'] == input_text, 'Assistant Message'].iloc[0]

print(output)