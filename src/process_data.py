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
    
    # 2. Extract and clean key data points (JSON-like columns)
    def extract_names(x):
        if isinstance(x, list):
            return "|".join([i['name'] for i in x if 'name' in i])
        return ""

    json_cols = ['genres', 'belongs_to_collection', 'production_countries', 'production_companies', 'spoken_languages']
    for col in json_cols:
        if col in df.columns:
            # Handle belongs_to_collection which is a dict, not list
            if col == 'belongs_to_collection':
                 df[col] = df[col].apply(lambda x: x['name'] if isinstance(x, dict) and 'name' in x else "")
            else:
                df[col] = df[col].apply(extract_names)

    # 3. Convert column datatypes
    numeric_cols = ['budget', 'id', 'popularity', 'revenue', 'vote_average', 'vote_count', 'runtime']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df.get(col, 0), errors='coerce')
        
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    # 4. Replace unrealistic values
    # Replace 0 with NaN for budget, revenue, runtime
    for col in ['budget', 'revenue', 'runtime']:
        df[col] = df[col].replace(0, pd.NA)
        
    # Convert budget and revenue to million USD
    df['budget_musd'] = df['budget'] / 1000000
    df['revenue_musd'] = df['revenue'] / 1000000
    
    # Handle vote_count = 0 (if any) - Assignment says "Analyze and adjust", strictly we can drop or leave. 
    # For now, we'll keep them but they won't rank high.
    
    # Replace placeholders in overview/tagline
    for col in ['overview', 'tagline']:
        if col in df.columns:
            df[col] = df[col].replace(['No Data', ''], pd.NA)

    # 5. Remove duplicates and drop rows with unknown 'id' or 'title'
    df = df.drop_duplicates(subset='id')
    df = df.dropna(subset=['id', 'title'])
    
    # 6. Keep only rows where at least 10 columns have non-NaN values
    df = df.dropna(thresh=10)
    
    # 7. Filter to include only 'Released' movies
    if 'status' in df.columns:
        df = df[df['status'] == 'Released']
        df = df.drop(columns=['status'])
        
    # 8. Reorder columns
    target_cols = [
        'id', 'title', 'tagline', 'release_date', 'genres', 'belongs_to_collection', 
        'original_language', 'budget_musd', 'revenue_musd', 'production_companies', 
        'production_countries', 'vote_count', 'vote_average', 'popularity', 'runtime', 
        'overview', 'spoken_languages', 'poster_path'
    ]
    # Add cast/director/crew_size if we had them (we fetched credits but didn't parse them yet in fetch_data 
    # actually fetch_data appends credits to response but we need to extract them here if they exist in raw df)
    
    # Let's check if 'credits' is in df (it should be if we flattened it, but raw json has it nested)
    # The raw dataframe from json will have a 'credits' column which is a dict.
    
    if 'credits' in df.columns:
        def get_director(x):
            if isinstance(x, dict) and 'crew' in x:
                for crew in x['crew']:
                    if crew.get('job') == 'Director':
                        return crew.get('name')
            return ""
            
        def get_cast(x):
            if isinstance(x, dict) and 'cast' in x:
                return "|".join([c['name'] for c in x['cast'][:5]]) # Top 5 cast
            return ""
            
        df['director'] = df['credits'].apply(get_director)
        df['cast'] = df['credits'].apply(get_cast)
        df['cast_size'] = df['credits'].apply(lambda x: len(x.get('cast', [])) if isinstance(x, dict) else 0)
        df['crew_size'] = df['credits'].apply(lambda x: len(x.get('crew', [])) if isinstance(x, dict) else 0)
        
        target_cols.extend(['cast', 'cast_size', 'director', 'crew_size'])
    
    # Select only existing columns from target list
    final_cols = [c for c in target_cols if c in df.columns]
    df = df[final_cols]
    
    # 9. Reset index
    df = df.reset_index(drop=True)
    
    # Calculate ROI for analysis (Revenue / Budget)
    # Ensure numeric for calculation
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
