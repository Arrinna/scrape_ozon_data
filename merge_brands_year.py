import os
import pandas as pd

glob_path = r'C:\Users\USER\Projects\scrape_ozon_dataset\brands_year'

# Get all .xlsx files in the directory (ignore subfolders)
files = [f for f in os.listdir(glob_path) if f.endswith('.xlsx') and os.path.isfile(os.path.join(glob_path, f))]

all_data = []
columns = None

for idx, fname in enumerate(files):
    fpath = os.path.join(glob_path, fname)
    # Read file, skip first 3 rows
    df = pd.read_excel(fpath, header=None, skiprows=3)
    # Use row 0 as column names (corresponds to original row 4), row 1 (original row 5) is always deleted
    if idx == 0:
        # Save row 0 as column names
        columns = df.iloc[0].astype(str).tolist()
    # Remove both header rows from data
    df = df.iloc[2:]
    # Add Category column as first column
    df.insert(0, 'Category', os.path.splitext(fname)[0])
    all_data.append(df)

# Concatenate all data
result = pd.concat(all_data, ignore_index=True)
# Set columns (first is 'Category', then columns from headers)
if columns is not None:
    result.columns = ['Category'] + columns
else:
    print('No columns found, skipping column renaming.')

# Export to CSV
result.to_csv('merged_brands_year.csv', index=False, encoding='utf-8-sig')
print('Merged dataset saved to merged_brands_year.csv') 