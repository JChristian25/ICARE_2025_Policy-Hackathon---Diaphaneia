import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Load Data (use correct paths and safe encoding)
flood_df = pd.read_csv('data/sumbong_flood_control/Sumbong_sa_pangulo _FloodControl.csv', low_memory=False, encoding='latin-1')
comelec_df = pd.read_csv('data/comelec_fiscal/COMELEC_fiscal+electoral_data_July 2025.csv', low_memory=False, encoding='latin-1')
pop_df = pd.read_csv('data/psa_population_total/Total Population-Household_Population-Number_of_Households_2020.csv', skiprows=2, low_memory=False, encoding='latin-1')
infra_df = pd.read_csv('data/DPWH-INFRA/infrastructure_data.csv', low_memory=False, encoding='latin-1')

# 2. Data Cleaning & Feature Engineering

# --- Flood Control Data ---
# Date Conversion
date_cols = ['StartDate', 'CompletionDateActual', 'CompletionDateOriginal']
for col in date_cols:
    if col in flood_df.columns:
        flood_df[col] = pd.to_datetime(flood_df[col], errors='coerce')

# Metric Calculation
flood_df['DelayDays'] = (flood_df['CompletionDateActual'] - flood_df['CompletionDateOriginal']).dt.days
flood_df['ActualDuration'] = (flood_df['CompletionDateActual'] - flood_df['StartDate']).dt.days
flood_df['ContractCost'] = pd.to_numeric(flood_df.get('ContractCost'), errors='coerce')
flood_df['ApprovedBudgetForTheContract'] = pd.to_numeric(flood_df.get('ApprovedBudgetForTheContract'), errors='coerce')
flood_df['CostRatio'] = flood_df['ContractCost'] / flood_df['ApprovedBudgetForTheContract']
if 'FundingYear' in flood_df.columns:
    flood_df['FundingYear'] = pd.to_numeric(flood_df['FundingYear'], errors='coerce').fillna(0).astype(int)

# Filter invalid rows
flood_clean = flood_df[
    (flood_df['ActualDuration'] > 0) & 
    (flood_df['DelayDays'].notna()) &
    (flood_df['CostRatio'] <= 1.5) # Filter extreme outliers for visualization
].copy()

# --- Population Data ---
# The PSA file may have leading header rows; we selected first 2 columns
pop_df = pop_df.iloc[:, :2].copy()
pop_df.columns = ['Province', 'TotalPopulation']
# Clean Province Names: Remove leading "...." and "Province of" if any
pop_df['Province'] = pop_df['Province'].astype(str).str.replace(r'^\.*', '', regex=True).str.strip().str.upper()
pop_df['TotalPopulation'] = pd.to_numeric(pop_df['TotalPopulation'], errors='coerce')
# Filter out regions (usually all caps or distinct format, but for now let's just keep all and merge carefully)

# --- Infrastructure Data ---
# Calculate % of Good Condition bridges per province
infra_df['CONDITION'] = infra_df['CONDITION'].astype(str)
infra_df['is_good'] = infra_df['CONDITION'].apply(lambda x: 1 if x.strip().lower() == 'good' else 0)
infra_agg = infra_df.groupby('PROVINCE', as_index=False)['is_good'].mean()
infra_agg.rename(columns={'is_good': 'Good_Infra_Ratio', 'PROVINCE': 'Province'}, inplace=True)
infra_agg['Province'] = infra_agg['Province'].str.upper().str.strip()

# --- COMELEC Data ---
comelec_df.rename(columns={'city': 'Province'}, inplace=True)
comelec_df['Province'] = comelec_df['Province'].astype(str).str.upper().str.strip()
comelec_df['position'] = comelec_df['position'].astype(str).str.strip()
comelec_df['year'] = pd.to_numeric(comelec_df['year'], errors='coerce')
comelec_df['votes'] = pd.to_numeric(comelec_df['votes'].astype(str).str.replace(',', ''), errors='coerce')
# Get dominant party per province (simplification: party with most votes for Governor in 2022)
gov_results = comelec_df[(comelec_df['position'] == 'Governor') & (comelec_df['year'] == 2022)].copy()
# Sort by votes and drop duplicates to keep winner
gov_winners = gov_results.sort_values('votes', ascending=False).drop_duplicates(subset=['Province'])
gov_winners = gov_winners[['Province', 'party']]

# 3. Merging
# Aggregate Flood Data by Province
flood_prov_agg = flood_clean.groupby('Province').agg({
    'ContractCost': 'sum',
    'DelayDays': 'mean',
    'ProjectID': 'count'
}).reset_index()
flood_prov_agg['Province'] = flood_prov_agg['Province'].str.upper().str.strip()

# Merge all
master_df = flood_prov_agg.merge(pop_df, on='Province', how='left')
master_df = master_df.merge(infra_agg, on='Province', how='left')
master_df = master_df.merge(gov_winners, on='Province', how='left')

# Calculate Per Capita Spending
master_df['PerCapitaSpending'] = master_df['ContractCost'] / master_df['TotalPopulation']

# 4. Visualizations

# A. Election Cycle Analysis
plt.figure(figsize=(12, 6))
funding_trends = flood_clean.groupby('FundingYear').agg({'ContractCost': 'sum', 'DelayDays': 'mean'}).reset_index()
funding_trends = funding_trends[funding_trends['FundingYear'].between(2015, 2024)]

ax1 = sns.barplot(x='FundingYear', y='ContractCost', data=funding_trends, color='skyblue', alpha=0.7)
ax2 = ax1.twinx()
sns.lineplot(x=ax1.get_xticks(), y=funding_trends['DelayDays'], color='red', marker='o', ax=ax2, linewidth=2)

ax1.set_ylabel('Total Contract Cost (PHP)', color='blue')
ax2.set_ylabel('Average Delay (Days)', color='red')
plt.title('Election Cycle Effect: Funding vs. Delays (2015-2024)')
# Mark Election Years
for year in [2016, 2019, 2022]:
    if year in funding_trends['FundingYear'].values:
        # Find x-position (index)
        idx = funding_trends[funding_trends['FundingYear'] == year].index[0]
        # Since barplot x-axis is categorical 0..N, we need to map year to index if not perfectly aligned
        # But here data is sorted, so we can try to find the index in the plotted data
        # A simpler way for text:
        plt.axvline(x=list(funding_trends['FundingYear']).index(year), color='gray', linestyle='--')
        plt.text(list(funding_trends['FundingYear']).index(year), ax2.get_ylim()[1]*0.9, f'Election {year}', ha='center')

plt.savefig('analysis_election_cycle.png')
plt.close()

# B. Contractor Network Analysis
plt.figure(figsize=(10, 6))
sns.boxplot(x='InterRelatedContractor', y='DelayDays', data=flood_clean, showfliers=False)
plt.title('Project Delays by Contractor Relationship')
plt.ylabel('Delay (Days)')
plt.savefig('analysis_contractor_delay.png')
plt.close()

# C. Needs-Based vs Allocation (Scatter)
plt.figure(figsize=(10, 6))
# Filter out huge outliers in per capita for clarity if needed
plot_data = master_df.dropna(subset=['PerCapitaSpending', 'Good_Infra_Ratio'])
sns.scatterplot(x='Good_Infra_Ratio', y='PerCapitaSpending', size='TotalPopulation', data=plot_data, sizes=(20, 500), alpha=0.6)
plt.title('Allocation Efficiency: Per Capita Spending vs. Existing Infrastructure Quality')
plt.xlabel('Ratio of Good Quality Bridges')
plt.ylabel('Per Capita Flood Control Spending (PHP)')
plt.axhline(y=plot_data['PerCapitaSpending'].median(), color='red', linestyle='--', label='Median Spending')
plt.axvline(x=plot_data['Good_Infra_Ratio'].median(), color='green', linestyle='--', label='Median Quality')
plt.legend()
plt.savefig('analysis_allocation_efficiency.png')
plt.close()

# Save Master Data for user
master_df.to_csv('processed_master_data.csv', index=False)
print("Analysis complete. Generated 3 plots and 1 master CSV.")
print(master_df.head())