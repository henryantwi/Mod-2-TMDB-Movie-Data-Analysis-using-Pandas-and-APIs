import pandas as pd
from pathlib import Path


def load_processed_data(filename="data/processed/movies_cleaned.csv"):
    """Loads the cleaned movie data from CSV."""
    filepath = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"{filename} not found. Please run process_data.py first.")
    
    df = pd.read_csv(filepath)
    # Convert release_date back to datetime objects as CSV loses this info
    df['release_date'] = pd.to_datetime(df['release_date'])
    # Extract the year from the release date for easier analysis
    df['release_year'] = df['release_date'].dt.year
    return df


def rank_movies(df, metric, ascending=False, top_n=5, filter_col=None, filter_val=None):
    """
    Ranks movies based on a specific metric.
    
    Args:
        df: The dataframe containing movie data.
        metric: The column name to sort by (e.g., 'revenue_musd').
        ascending: Sort order (False for descending/highest first).
        top_n: Number of top movies to return.
        filter_col: Optional column to filter by before ranking.
        filter_val: Minimum value for the filter column.
    """
    data = df.copy()
    # Apply filter if specified (e.g., only consider movies with budget > 10M)
    if filter_col:
        data = data[data[filter_col] >= filter_val]
    
    # Sort the data and take the top N rows
    ranked = data.sort_values(metric, ascending=ascending).head(top_n)
    # Return only the title and the metric column
    return ranked[['title', metric]]


def analyze_movies(df):
    """
    Performs various analyses on the movie dataset.
    """
    # 1. Financial Analysis
    # highest revenue
    print(rank_movies(df, 'revenue_musd'))
    
    # highest budget
    print(rank_movies(df, 'budget_musd'))
    
    # highest profit
    print(rank_movies(df, 'profit'))
    
    # lowest profit (biggest flops)
    print(rank_movies(df, 'profit', ascending=True))
    
    # highest ROI (Return on Investment) - filtering for significant budget
    print(rank_movies(df, 'roi', filter_col='budget_musd', filter_val=10))
    
    # lowest ROI (budget >= 10M)
    print(rank_movies(df, 'roi', ascending=True, filter_col='budget_musd', filter_val=10))
    
    # 2. Popularity and Ratings
    # most voted
    print(rank_movies(df, 'vote_count'))
    
    # highest rated (filtering for at least 10 votes to avoid outliers)
    print(rank_movies(df, 'vote_average', filter_col='vote_count', filter_val=10))
    
    # lowest rated (votes >= 10)
    print(rank_movies(df, 'vote_average', ascending=True, filter_col='vote_count', filter_val=10))
    
    # most popular according to TMDB popularity score
    print(rank_movies(df, 'popularity'))
    
    # 3. Specific Queries
    # finding sci-fi action movies with Bruce Willis
    mask_scifi = df['genres'].str.contains('Science Fiction', na=False)
    mask_action = df['genres'].str.contains('Action', na=False)
    mask_bruce = df['cast'].str.contains('Bruce Willis', na=False)
    
    # Combine masks to find movies matching all criteria
    bruce_movies = df[mask_scifi & mask_action & mask_bruce]
    bruce_movies = bruce_movies.sort_values('vote_average', ascending=False)
    print(bruce_movies[['title', 'vote_average', 'release_date']])
    
    # Uma Thurman and Quentin Tarantino movies
    mask_uma = df['cast'].str.contains('Uma Thurman', na=False)
    mask_qt = df['director'].str.contains('Quentin Tarantino', na=False)
    
    uma_qt_movies = df[mask_uma & mask_qt]
    uma_qt_movies = uma_qt_movies.sort_values('runtime')
    print(uma_qt_movies[['title', 'runtime', 'release_date']])
    
    # 4. Franchise Analysis
    # Create a boolean column for franchise movies
    df['is_franchise'] = df['belongs_to_collection'].apply(lambda x: True if x else False)
    
    # Compare average stats for franchise vs standalone movies
    franchise_stats = df.groupby('is_franchise').agg({
        'revenue_musd': 'mean',
        'roi': 'median',
        'budget_musd': 'mean',
        'popularity': 'mean',
        'vote_average': 'mean'
    })
    franchise_stats = franchise_stats.rename(index={True: 'Franchise', False: 'Standalone'})
    print(franchise_stats)
    
    # Identify most successful franchises
    franchise_df = df[df['is_franchise']]
    franchise_df = franchise_df.groupby('belongs_to_collection').agg({
        'title': 'count',
        'budget_musd': ['sum', 'mean'],
        'revenue_musd': ['sum', 'mean'],
        'vote_average': 'mean'
    })
    franchise_df.columns = ['movie_count', 'total_budget', 'mean_budget', 'total_revenue', 'mean_revenue', 'mean_rating']
    print(franchise_df.sort_values('total_revenue', ascending=False).head(5))
    
    # 5. Director Analysis
    director_df = df.groupby('director').agg({
        'title': 'count',
        'revenue_musd': 'sum',
        'vote_average': 'mean'
    })
    director_df.columns = ['movie_count', 'total_revenue', 'mean_rating']
    
    # remove empty director names
    if "" in director_df.index:
        director_df = director_df.drop("")
    
    print(director_df.sort_values('total_revenue', ascending=False).head(5))

    return franchise_stats, franchise_df, director_df


if __name__ == "__main__":
    df = load_processed_data()
    franchise_stats, franchise_df, director_df = analyze_movies(df)
