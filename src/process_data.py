import pandas as pd
from pandas import DataFrame
import json
from pathlib import Path

def load_raw_data(filename="data/raw/movies.json"):
    """Loads raw data from JSON file."""
    filepath = Path(filename)
    # Check if the file exists before trying to open it
    if not filepath.exists():
        raise FileNotFoundError(f"{filename} not found. Please run fetch_data.py first.")
    
    # Open the file and load the JSON data
    with filepath.open('r', encoding='utf-8') as f:
        data = json.load(f)
    # Convert the list of dictionaries to a pandas DataFrame
    return pd.DataFrame(data)

def process_data(df) -> DataFrame:
    """
    Cleans and transforms the movie dataframe according to assignment requirements.
    """
    # 1. Drop irrelevant columns
    # These columns are not needed for our analysis
    drop_cols = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')
    
    # 2-3. Extract names from JSON-like columns
    # Many columns contain lists of dictionaries (e.g., genres), we just want the names
    def extract_names(x):
        if isinstance(x, list):
            # Join the names with a pipe separator
            return "|".join([i['name'] for i in x if 'name' in i])
        return ""

    json_cols = ['genres', 'belongs_to_collection', 'production_countries', 'production_companies', 'spoken_languages']
    for col in json_cols:
        if col in df.columns:
            # Special handling for 'belongs_to_collection' which is a dict, not a list
            if col == 'belongs_to_collection':
                 df[col] = df[col].apply(lambda x: x['name'] if isinstance(x, dict) and 'name' in x else "")
            else:
                df[col] = df[col].apply(extract_names)
                
    # 4. Inspect extracted columns for anomalies
    print("\n--- Inspecting Extracted Columns ---")
    for col in json_cols:
        if col in df.columns:
            print(f"\nTop 5 values for {col}:")
            print(df[col].value_counts().head(5))

    # 5. Convert column datatypes
    # Ensure numeric columns are actually numeric, coercing errors to NaN
    numeric_cols = ['budget', 'id', 'popularity', 'revenue', 'vote_average', 'vote_count', 'runtime']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df.get(col, 0), errors='coerce')
        
    # Convert release_date to datetime objects
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    # 6. Replace unrealistic values and convert to million USD
    for col in ['budget', 'revenue', 'runtime']:
        # Treat 0 as missing data (NaN)
        df[col] = df[col].replace(0, pd.NA)
        
    # Convert budget and revenue to millions for easier reading
    df['budget_musd'] = df['budget'] / 1_000_000
    df['revenue_musd'] = df['revenue'] / 1000000

    # Drop original budget and revenue columns as we have the MUSD versions
    df = df.drop(columns=['budget', 'revenue'])
        
    # If vote count is 0, set vote average to 0 to avoid misleading ratings
    if 'vote_count' in df.columns and 'vote_average' in df.columns:
        df.loc[df['vote_count'] == 0, 'vote_average'] = 0
    
    # Replace empty strings or 'No Data' with NaN in text columns
    for col in ['overview', 'tagline']:
        if col in df.columns:
            df[col] = df[col].replace(['No Data', ''], pd.NA)

    # 7. Remove duplicates and invalid rows
    # Drop duplicate movies based on ID
    df = df.drop_duplicates(subset='id')
    # Drop rows where ID or title is missing
    df = df.dropna(subset=['id', 'title'])
    
    # 8. Drop rows with too many missing values
    # Keep rows that have at least 10 non-missing values
    df = df.dropna(thresh=10)
    
    # 9. Filter to 'Released' movies only
    if 'status' in df.columns:
        df = df[df['status'] == 'Released']
        df = df.drop(columns=['status'])
        
    # 10. Reorder columns and extract credits info
    target_cols = [
        'id', 'title', 'tagline', 'release_date', 'genres', 'belongs_to_collection', 
        'original_language', 'budget_musd', 'revenue_musd', 'production_companies', 
        'production_countries', 'vote_count', 'vote_average', 'popularity', 'runtime', 
        'overview', 'spoken_languages', 'poster_path'
    ]
    
    if 'credits' in df.columns:
        # Helper function to extract director name
        def get_director(x):
            if isinstance(x, dict) and 'crew' in x:
                for crew in x['crew']:
                    if crew.get('job') == 'Director':
                        return crew.get('name')
            return ""
            
        # Helper function to extract top 5 cast members
        def get_cast(x):
            if isinstance(x, dict) and 'cast' in x:
                return "|".join([c['name'] for c in x['cast'][:5]])
            return ""
            
        df['director'] = df['credits'].apply(get_director)
        df['cast'] = df['credits'].apply(get_cast)

        # Calculate cast and crew sizes
        df['cast_size'] = df['credits'].apply(lambda x: len(x.get('cast', [])) if isinstance(x, dict) else 0)
        df['crew_size'] = df['credits'].apply(lambda x: len(x.get('crew', [])) if isinstance(x, dict) else 0)
        
        target_cols.extend(['cast', 'cast_size', 'director', 'crew_size'])
    
    # Select only the columns we want to keep
    final_cols = [c for c in target_cols if c in df.columns]
    df = df[final_cols]
    
    # 11. Reset index and calculate ROI/profit
    df = df.reset_index(drop=True) # to clear fragments
    
    # Fill NaN values in budget and revenue with 0 for calculations
    df['budget_musd'] = df['budget_musd'].fillna(0)
    df['revenue_musd'] = df['revenue_musd'].fillna(0)
    
    # Calculate ROI (Return on Investment) for each movie
    def calculate_roi(row):
        # If budget is greater than 0, calculate ROI as revenue / budget
        # Otherwise return 0 to avoid division by zero
        if row['budget_musd'] > 0:
            return row['revenue_musd'] / row['budget_musd']
        else:
            return 0
    
    df['roi'] = df.apply(calculate_roi, axis=1)
    # Calculate profit as revenue minus budget
    df['profit'] = df['revenue_musd'] - df['budget_musd']
    
    return df

def save_processed_data(df, filename="data/processed/movies_cleaned.csv"):
    """Saves processed dataframe to CSV."""
    filepath = Path(filename)
    # Create parent directories if they don't exist
    filepath.parent.mkdir(parents=True, exist_ok=True)
    # Save to CSV without the index
    df.to_csv(filepath, index=False)
    print(f"Saved processed data to {filepath}")


if __name__ == "__main__":
    print("Loading raw data...")
    df: DataFrame = load_raw_data()
    
    print("Processing data...")
    df_clean: DataFrame = process_data(df)
    
    print("Saving processed data...")
    save_processed_data(df_clean)
