import pandas as pd

def process_data(data):
df = pd.DataFrame(data)
return df.groupby('category').sum()