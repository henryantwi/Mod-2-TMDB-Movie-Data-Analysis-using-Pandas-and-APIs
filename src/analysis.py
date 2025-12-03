import pandas as pd
from pathlib import Path


def load_processed_data(filename="data/processed/movies_cleaned.csv"):
    """Loads processed data from CSV."""
    filepath = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"{filename} not found. Please run process_data.py first.")
    
    df = pd.read_csv(filepath)
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['release_year'] = df['release_date'].dt.year
    return df

def analyze_movies(df):
    """Performs comprehensive analysis on the movie dataset."""
    
    # --- 2. Define a User-Defined Function (UDF) to streamline ranking operations ---
    print("\n=== 2. User-Defined Function for Ranking ===")
    
    def rank_movies(df, metric, ascending=False, top_n=5, filter_col=None, filter_val=None):
        data = df.copy()
        if filter_col:
            data = data[data[filter_col] >= filter_val]
        
        ranked = data.sort_values(metric, ascending=ascending).head(top_n)
        return ranked[['title', metric]]

    # Highest Revenue
    print("\n--- Highest Revenue ---")
    print(rank_movies(df, 'revenue_musd'))
    
    # Highest Budget
    print("\n--- Highest Budget ---")
    print(rank_movies(df, 'budget_musd'))
    
    # Highest Profit
    print("\n--- Highest Profit ---")
    print(rank_movies(df, 'profit'))
    
    # Lowest Profit
    print("\n--- Lowest Profit ---")
    print(rank_movies(df, 'profit', ascending=True))
    
    # Highest ROI (Budget >= 10M)
    print("\n--- Highest ROI (Budget >= 10M) ---")
    print(rank_movies(df, 'roi', filter_col='budget_musd', filter_val=10))
    
    # Lowest ROI (Budget >= 10M)
    print("\n--- Lowest ROI (Budget >= 10M) ---")
    print(rank_movies(df, 'roi', ascending=True, filter_col='budget_musd', filter_val=10))
    
    # Most Voted
    print("\n--- Most Voted Movies ---")
    print(rank_movies(df, 'vote_count'))
    
    # Highest Rated (Votes >= 10)
    print("\n--- Highest Rated (Votes >= 10) ---")
    print(rank_movies(df, 'vote_average', filter_col='vote_count', filter_val=10))
    
    # Lowest Rated (Votes >= 10)
    print("\n--- Lowest Rated (Votes >= 10) ---")
    print(rank_movies(df, 'vote_average', ascending=True, filter_col='vote_count', filter_val=10))
    
    # Most Popular
    print("\n--- Most Popular Movies ---")
    print(rank_movies(df, 'popularity'))
    
    
    # --- 3. Filter the dataset for specific queries ---
    print("\n=== 3. Advanced Movie Filtering ===")
    
    # Search 1: Best-rated Sci-Fi Action movies starring Bruce Willis
    # Note: genres and cast are pipe-separated strings
    mask_scifi = df['genres'].str.contains('Science Fiction', na=False)
    mask_action = df['genres'].str.contains('Action', na=False)
    mask_bruce = df['cast'].str.contains('Bruce Willis', na=False)
    
    bruce_movies = df[mask_scifi & mask_action & mask_bruce].sort_values('vote_average', ascending=False)
    print("\n--- Sci-Fi Action movies starring Bruce Willis ---")
    print(bruce_movies[['title', 'vote_average', 'release_date']])
    
    # Search 2: Movies starring Uma Thurman, directed by Quentin Tarantino (sorted by runtime)
    mask_uma = df['cast'].str.contains('Uma Thurman', na=False)
    mask_qt = df['director'].str.contains('Quentin Tarantino', na=False)
    
    uma_qt_movies = df[mask_uma & mask_qt].sort_values('runtime')
    print("\n--- Uma Thurman & Quentin Tarantino Movies (by Runtime) ---")
    print(uma_qt_movies[['title', 'runtime', 'release_date']])
    
    
    # --- 4. Franchise vs. Standalone Movie Performance ---
    print("\n=== 4. Franchise vs Standalone Analysis ===")
    
    df['is_franchise'] = df['belongs_to_collection'].apply(lambda x: True if x else False)
    
    franchise_stats = df.groupby('is_franchise').agg({
        'revenue_musd': 'mean',
        'roi': 'median',
        'budget_musd': 'mean',
        'popularity': 'mean',
        'vote_average': 'mean'
    }).rename(index={True: 'Franchise', False: 'Standalone'})
    
    print("\n--- Franchise vs Standalone Stats ---")
    print(franchise_stats)
    
    
    # --- 5. Find the Most Successful Movie Franchises ---
    print("\n=== 5. Most Successful Franchises ===")
    
    franchise_df = df[df['is_franchise']].groupby('belongs_to_collection').agg({
        'title': 'count',
        'budget_musd': ['sum', 'mean'],
        'revenue_musd': ['sum', 'mean'],
        'vote_average': 'mean'
    })
    franchise_df.columns = ['movie_count', 'total_budget', 'mean_budget', 'total_revenue', 'mean_revenue', 'mean_rating']
    print("\n--- Top 5 Franchises by Total Revenue ---")
    print(franchise_df.sort_values('total_revenue', ascending=False).head(5))
    
    
    # --- 6. Find the Most Successful Directors ---
    print("\n=== 6. Most Successful Directors ===")
    
    director_df = df.groupby('director').agg({
        'title': 'count',
        'revenue_musd': 'sum',
        'vote_average': 'mean'
    })
    director_df.columns = ['movie_count', 'total_revenue', 'mean_rating']
    # Filter out empty director if any
    if "" in director_df.index:
        director_df = director_df.drop("")
        
    print("\n--- Top 5 Directors by Total Revenue ---")
    print(director_df.sort_values('total_revenue', ascending=False).head(5))

    return franchise_stats, franchise_df, director_df


if __name__ == "__main__":
    print("Loading processed data...")
    df = load_processed_data()
    
    print("Analyzing data...")
    franchise_stats, franchise_df, director_df = analyze_movies(df)

