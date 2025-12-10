import pandas as pd
from itertools import product
from rich.console import Console
from rich.table import Table
from rich import box

def count_by_filters(csv_file, group_columns, filter_dict, extra_single=None):
    """
    Count occurrences based on user-specified multiple filters and group columns.
    
    This function reads a CSV file and produces a cross-tabulation of counts based on:
    1. Grouping columns (what to aggregate by)
    2. Filter combinations (creates columns for each combination of filter values)
    3. Optional single filter counts (adds individual column counts)

    Args:
        csv_file (str): Path to the CSV file to analyze.
                       Example: "batch_0.csv" or "data/patient_records.csv"
                       
        group_columns (str or list): Column name(s) to group the data by.
                                    These will become the index (rows) of the result.
                                    Examples:
                                    - Single: 'RegionRes'
                                    - Multiple: ['RegionRes', 'ProvRes']
                                    
        filter_dict (dict): Dictionary where keys are column names and values are lists
                           of values to filter by. The function creates combinations
                           of all values across columns.
                           Example:
                           {
                               'RemovalType': ['RECOVERED', 'DIED'],
                               'Sex': ['MALE', 'FEMALE']
                           }
                           This creates 4 combinations:
                           - RemovalType_RECOVERED_Sex_MALE
                           - RemovalType_RECOVERED_Sex_FEMALE
                           - RemovalType_DIED_Sex_MALE
                           - RemovalType_DIED_Sex_FEMALE
                           
        extra_single (dict, optional): Similar to filter_dict, but creates separate
                                      count columns for each value (not combinations).
                                      Useful for getting individual category totals.
                                      Example:
                                      {
                                          'RemovalType': ['RECOVERED', 'DIED'],
                                          'Sex': ['MALE', 'FEMALE']
                                      }
                                      This adds 4 separate columns:
                                      - RemovalType_RECOVERED
                                      - RemovalType_DIED
                                      - Sex_MALE
                                      - Sex_FEMALE

    Returns:
        pandas.DataFrame: A DataFrame where:
                         - Rows = unique combinations of group_columns values
                         - Columns = count columns for each filter combination
                         - Values = integer counts of matching records
                         
    Example:
        >>> result = count_by_filters(
        ...     csv_file="patients.csv",
        ...     group_columns=['Region', 'Province'],
        ...     filter_dict={'Status': ['ACTIVE', 'INACTIVE'], 'Age': ['YOUNG', 'OLD']},
        ...     extra_single={'Status': ['ACTIVE']}
        ... )
    """

    # Read the CSV file into a pandas DataFrame
    # low_memory=False ensures consistent data types across chunks
    # encoding='latin-1' handles special characters that UTF-8 can't decode
    df = pd.read_csv(csv_file, low_memory=False, encoding='latin-1')

    # Convert single string to list for consistent processing
    if isinstance(group_columns, str):
        group_columns = [group_columns]

    # --- Step 1: Create combination filters ---
    # Extract column names and their corresponding value lists from filter_dict
    filter_columns = list(filter_dict.keys())
    filter_value_lists = list(filter_dict.values())

    # Generate all possible combinations of filter values using Cartesian product
    # Example: ['RECOVERED', 'DIED'] x ['MALE', 'FEMALE'] = 4 combinations
    from itertools import product
    filter_combos = list(product(*filter_value_lists))

    # Create readable labels for each combination
    # Example: "RemovalType_RECOVERED_Sex_MALE"
    combo_labels = [
        "_".join([f"{col}_{val}" for col, val in zip(filter_columns, combo)])
        for combo in filter_combos
    ]

    # Initialize empty DataFrame to store results
    result = pd.DataFrame()

    # --- Step 2: Process combination filters ---
    # For each filter combination, count occurrences grouped by group_columns
    for label, combo in zip(combo_labels, filter_combos):
        # Start with all rows included (True for all)
        condition = pd.Series([True] * len(df))
        
        # Build compound condition by ANDing all filter criteria
        # Example: (RemovalType == 'RECOVERED') AND (Sex == 'MALE')
        for col, val in zip(filter_columns, combo):
            condition &= (df[col] == val)

        # Count records matching the condition, grouped by group_columns
        counts = df[condition].groupby(group_columns).size()
        
        # Add as a new column in the result DataFrame
        result[label] = counts

    # --- Step 3: Add individual column counts (optional) ---
    # Unlike combination filters, these count each value independently
    if extra_single:
        for col, values in extra_single.items():
            for val in values:
                label = f"{col}_{val}"
                # Simple single-column filter
                condition = df[col] == val
                counts = df[condition].groupby(group_columns).size()
                result[label] = counts

    # Fill missing values with 0 and convert to integer type
    # (groupby.size() may not return rows for groups with 0 counts)
    result = result.fillna(0).astype(int)
    return result


# ================================================
# Helper Function: Display DataFrame using Rich
# ================================================
def display_dataframe_rich(df, title="Data Summary", max_rows=50):
    """
    Display a pandas DataFrame as a beautiful table using the Rich library.
    
    Args:
        df (pandas.DataFrame): The DataFrame to display
        title (str): Title to show above the table
        max_rows (int): Maximum number of rows to display (default: 50)
    """
    console = Console()
    
    # Create a Rich table with a nice border style
    table = Table(title=title, box=box.DOUBLE_EDGE, show_lines=True)
    
    # Add columns - first add the index column(s)
    if df.index.name:
        table.add_column(df.index.name, style="cyan", no_wrap=True)
    elif isinstance(df.index, pd.MultiIndex):
        for name in df.index.names:
            table.add_column(str(name), style="cyan", no_wrap=True)
    else:
        table.add_column("Index", style="cyan", no_wrap=True)
    
    # Add data columns
    for column in df.columns:
        table.add_column(str(column), style="magenta", justify="right")
    
    # Add rows (limit to max_rows to avoid overwhelming output)
    display_df = df.head(max_rows) if len(df) > max_rows else df
    
    for idx, row in display_df.iterrows():
        # Handle MultiIndex
        if isinstance(idx, tuple):
            row_data = [str(i) for i in idx] + [str(val) for val in row]
        else:
            row_data = [str(idx)] + [str(val) for val in row]
        table.add_row(*row_data)
    
    # Print the table
    console.print(table)
    
    # Show info if table was truncated
    if len(df) > max_rows:
        console.print(f"[yellow]... showing {max_rows} of {len(df)} rows[/yellow]")
    console.print(f"[green]Total rows: {len(df)} | Total columns: {len(df.columns)}[/green]\n")


# ================================================
# Example Usage
# ================================================
if __name__ == "__main__":
    # -----------------------------------------
    # Configuration Parameters
    # -----------------------------------------
    
    # INPUT: Path to your CSV file containing the data to analyze
    csv_file = "data/comelec_fiscal/comelec.csv"
    
    # -----------------------------------------
    # Sum votes by rid
    # -----------------------------------------
    print("\n" + "="*80)
    print("PROCESSING DATA...")
    print("="*80)
    
    df = pd.read_csv(csv_file, low_memory=False, encoding='latin-1')
    
    # Debug: Check sample of votes column before conversion
    print("Sample of votes column (before conversion):")
    print(df['votes'].head(10))
    print(f"Type: {type(df['votes'].iloc[0])}")
    print()
    
    # Remove commas from votes if they exist, then convert to numeric
    if df['votes'].dtype == 'object':
        df['votes'] = df['votes'].astype(str).str.replace(',', '')
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce')
    df['won'] = pd.to_numeric(df['won'], errors='coerce')
    
    # Debug: Check for NaN values
    print(f"NaN values in votes: {df['votes'].isna().sum()}")
    print(f"Total rows: {len(df)}")
    print(f"Winners rows: {len(df[df['won'] == 1])}")
    print(f"Winners with valid votes: {len(df[(df['won'] == 1) & (df['votes'].notna())])}")
    print()
    
    # Filter for winners only (won = 1)
    # df_winners = df[df['won'] == 1]
    
    # Calculate total votes by rid (disregarding won condition)
    result = df.groupby('rid')['votes'].sum().to_frame()
    result.columns = ['total_votes']
    
    # -----------------------------------------
    # Display Results Using Rich Library
    # ----------------------------------------- 
    print("\n" + "="*80)
    print("RESULTS")
    print("="*80 + "\n")
    
    # Display the results as a beautiful formatted table
    display_dataframe_rich(
        result, 
        title="📊 Count Results by Filters",
        max_rows=50  # Adjust this to show more/fewer rows
    )
    
    # -----------------------------------------
    # Save Results to Files
    # -----------------------------------------
    console = Console()
    
    # Save as CSV
    result.to_csv("count_results.csv")
    console.print("[green]✓ Saved to count_results.csv[/green]")
    
    # Save as Excel (if openpyxl is installed)
    try:
        result.to_excel("count_results.xlsx", engine='openpyxl')
        console.print("[green]✓ Saved to count_results.xlsx[/green]")
    except ImportError:
        console.print("[yellow]⚠ Install openpyxl to enable Excel export: pip install openpyxl[/yellow]")
    
    # -----------------------------------------
    # Optional: Display raw CSV format
    # -----------------------------------------
    # Uncomment below to see raw CSV/TSV output
    # print("\nTab-delimited format:")
    # print("="*60)
    # print(result.to_csv(sep='\t'))
    # 
    # print("\nCSV format:")
    # print("="*60)
    # print(result.to_csv())
