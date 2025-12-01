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
    Cleans and transforms the movie dataframe.
    """
    # Select relevant columns
    columns = ['id', 'title', 'release_date', 'vote_average', 'vote_count', 'popularity', 'original_language', 'overview', 'budget', 'revenue']
    # Check if columns exist before selecting
    existing_cols = [c for c in columns if c in df.columns]
    df = df[existing_cols]
    
    # Handle missing values
    df = df.dropna(subset=['title', 'release_date'])
    
    # Convert types
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
    df['popularity'] = pd.to_numeric(df['popularity'], errors='coerce')
    df['budget'] = pd.to_numeric(df.get('budget', 0), errors='coerce').fillna(0)
    df['revenue'] = pd.to_numeric(df.get('revenue', 0), errors='coerce').fillna(0)
    
    # Extract year
    df['release_year'] = df['release_date'].dt.year

    # Calculate ROI (Return on Investment)
    # ROI = (Revenue - Budget) / Budget
    # Avoid division by zero
    df['roi'] = df.apply(lambda row: (row['revenue'] - row['budget']) / row['budget'] if row['budget'] > 0 else 0, axis=1)
    
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
