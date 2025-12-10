import pandas as pd

# Load datasets
d1 = pd.read_csv("data/sumbong_flood_control/Sumbong_FloodControl.csv")
d2 = pd.read_csv("data/comelec_fiscal/COMELEC_Fiscal.csv")

# Basic summaries
print(d1.shape, d2.shape)
print(d1.columns)
print(d2.columns)

# Example: compute duration of projects
d1['StartDate'] = pd.to_datetime(d1['StartDate'], errors='coerce')
d1['CompletionDateActual'] = pd.to_datetime(d1['CompletionDateActual'], errors='coerce')
d1['duration_days'] = (d1['CompletionDateActual'] - d1['StartDate']).dt.days

# Example: compute vote share
d2['vote_share'] = d2['votes'] / d2['totvot']

# Example: IRA dependence
d2['ira_share'] = d2['ira'] / (d2['lgusincome'] + 1e-9)

print(d2[['region','lgu','year','ira_share']].head())
