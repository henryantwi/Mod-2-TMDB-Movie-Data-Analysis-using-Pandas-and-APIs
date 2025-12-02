import pandas as pd
import json
import os

def load_raw_data(filename="data/raw/movies.json"):
    """Loads raw data from JSON file."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found. Please run fetch_data.py first.")
    
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)

def process_data(df):
    """
    Cleans and transforms the movie dataframe according to assignment requirements.
    """
    # 1. Drop irrelevant columns
    drop_cols = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')
    
    # 2-3. Extract names from JSON-like columns
    def extract_names(x):
        if isinstance(x, list):
            return "|".join([i['name'] for i in x if 'name' in i])
        return ""

    json_cols = ['genres', 'belongs_to_collection', 'production_countries', 'production_companies', 'spoken_languages']
    for col in json_cols:
        if col in df.columns:
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
    numeric_cols = ['budget', 'id', 'popularity', 'revenue', 'vote_average', 'vote_count', 'runtime']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df.get(col, 0), errors='coerce')
        
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    # 6. Replace unrealistic values and convert to million USD
    for col in ['budget', 'revenue', 'runtime']:
        df[col] = df[col].replace(0, pd.NA)
        
    df['budget_musd'] = df['budget'] / 1000000
    df['revenue_musd'] = df['revenue'] / 1000000
    
    if 'vote_count' in df.columns and 'vote_average' in df.columns:
        df.loc[df['vote_count'] == 0, 'vote_average'] = 0
    
    for col in ['overview', 'tagline']:
        if col in df.columns:
            df[col] = df[col].replace(['No Data', ''], pd.NA)

    # 7. Remove duplicates and invalid rows
    df = df.drop_duplicates(subset='id')
    df = df.dropna(subset=['id', 'title'])
    
    # 8. Drop rows with too many missing values
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
        def get_director(x):
            if isinstance(x, dict) and 'crew' in x:
                for crew in x['crew']:
                    if crew.get('job') == 'Director':
                        return crew.get('name')
            return ""
            
        def get_cast(x):
            if isinstance(x, dict) and 'cast' in x:
                return "|".join([c['name'] for c in x['cast'][:5]])
            return ""
            
        df['director'] = df['credits'].apply(get_director)
        df['cast'] = df['credits'].apply(get_cast)
        df['cast_size'] = df['credits'].apply(lambda x: len(x.get('cast', [])) if isinstance(x, dict) else 0)
        df['crew_size'] = df['credits'].apply(lambda x: len(x.get('crew', [])) if isinstance(x, dict) else 0)
        
        target_cols.extend(['cast', 'cast_size', 'director', 'crew_size'])
    
    final_cols = [c for c in target_cols if c in df.columns]
    df = df[final_cols]
    
    # 11. Reset index and calculate ROI/profit
    df = df.reset_index(drop=True)
    
    df['budget_musd'] = df['budget_musd'].fillna(0)
    df['revenue_musd'] = df['revenue_musd'].fillna(0)
    df['roi'] = df.apply(lambda row: row['revenue_musd'] / row['budget_musd'] if row['budget_musd'] > 0 else 0, axis=1)
    df['profit'] = df['revenue_musd'] - df['budget_musd']
    
    return df

def save_processed_data(df, filename="data/processed/movies_cleaned.csv"):
    """Saves processed dataframe to CSV."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    df.to_csv(filename, index=False)
    print(f"Saved processed data to {filename}")

if __name__ == "__main__":
    print("Loading raw data...")
    df = load_raw_data()
    
    print("Processing data...")
    df_clean = process_data(df)
    
    print("Saving processed data...")
    save_processed_data(df_clean)
