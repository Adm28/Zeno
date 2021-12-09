import pandas as pd

df = pd.read_csv("CleanedEpochTime.csv")
maxTime = max(df['time_cost'])
df['time_cost'] = df['time_cost'].apply(lambda x: (x/maxTime)*5)
df.to_csv("CleanedEpochTime.csv")