import pandas as pd
import re
from collections import Counter

def convert_range_to_numeric(s, method='midpoint'):
    """Convert range strings like '35 to 39' to numeric."""
    match = re.findall(r'\d+', str(s))
    if len(match) == 2:
        low, high = map(int, match)
        if method == 'midpoint':
            return (low + high) / 2
        elif method == 'min':
            return low
        elif method == 'max':
            return high
    elif len(match) == 1:
        return int(match[0])
    else:
        return None

def filter_and_stats(csv_file, filter_dict=None, target_column=None, group_columns=None):
    """
    Adaptive filtering and statistics for numeric and categorical columns.

    Args:
        csv_file: path to CSV
        filter_dict: dictionary {column: [allowed values]} for filtering
        target_column: column to compute stats on (numeric or categorical)
        group_columns: list of columns to group by before stats

    Returns:
        Pandas DataFrame or dictionary with statistics
    """
    df = pd.read_csv(csv_file, low_memory=False)

    # --------------------------
    # Apply filters
    # --------------------------
    if filter_dict:
        condition = pd.Series([True] * len(df))
        for col, vals in filter_dict.items():
            if col in df.columns:
                condition &= df[col].isin(vals)
            else:
                print(f"Warning: Column '{col}' not found in dataset.")
        df = df[condition]

    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found.")

    # --------------------------
    # Convert range strings to numeric if needed
    # --------------------------
    if pd.api.types.is_object_dtype(df[target_column]):
        # detect if column contains ranges like "35 to 39"
        sample = df[target_column].dropna().astype(str).head(20)
        if any(re.search(r'\d+\s*to\s*\d+', s) for s in sample):
            df[target_column] = df[target_column].apply(lambda x: convert_range_to_numeric(x))

    # --------------------------
    # Decide if numeric or categorical
    # --------------------------
    is_numeric = pd.api.types.is_numeric_dtype(df[target_column])

    # --------------------------
    # Grouping
    # --------------------------
    if group_columns:
        grouped = df.groupby(group_columns)
        result = {}
        for name, group in grouped:
            if is_numeric:
                data = group[target_column].dropna()
                result[name] = {
                    'count': len(data),
                    'sum': data.sum(),
                    'mean': data.mean(),
                    'median': data.median(),
                    'mode': data.mode().tolist()
                }
            else:
                data = group[target_column].dropna().astype(str)
                counts = data.value_counts()
                percentages = (counts / counts.sum() * 100).round(2)
                result[name] = {
                    'count_per_category': counts.to_dict(),
                    'percentage_per_category': percentages.to_dict(),
                    'mode': data.mode().tolist()
                }
        return result
    else:
        # No grouping
        if is_numeric:
            data = df[target_column].dropna()
            return {
                'count': len(data),
                'sum': data.sum(),
                'mean': data.mean(),
                'median': data.median(),
                'mode': data.mode().tolist()
            }
        else:
            data = df[target_column].dropna().astype(str)
            counts = data.value_counts()
            percentages = (counts / counts.sum() * 100).round(2)
            return {
                'count_per_category': counts.to_dict(),
                'percentage_per_category': percentages.to_dict(),
                'mode': data.mode().tolist()
            }

# --------------------------
# Example Usage
# --------------------------
if __name__ == "__main__":
    csv_file = 'batch_0.csv'

    filter_dict = {
        'RemovalType': ['RECOVERED', 'DIED'],
        'Sex': ['MALE', 'FEMALE']
    }

    target_column = 'AgeGroup'
    group_columns = ['RegionRes']  # optional

    stats = filter_and_stats(csv_file, filter_dict, target_column, group_columns)
    print("\nAdaptive Statistics:")
    print("="*80)
    from pprint import pprint
    pprint(stats)
