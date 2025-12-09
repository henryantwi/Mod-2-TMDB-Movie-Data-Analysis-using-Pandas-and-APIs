import pandas as pd
from pathlib import Path


def load_processed_data(filename="data/processed/movies_cleaned.csv"):
    filepath = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"{filename} not found. Please run process_data.py first.")
    
    df = pd.read_csv(filepath)
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['release_year'] = df['release_date'].dt.year
    return df


def rank_movies(df, metric, ascending=False, top_n=5, filter_col=None, filter_val=None):
    data = df.copy()
    if filter_col:
        data = data[data[filter_col] >= filter_val]
    
    ranked = data.sort_values(metric, ascending=ascending).head(top_n)
    return ranked[['title', metric]]


def analyze_movies(df):
    # highest revenue
    print(rank_movies(df, 'revenue_musd'))
    
    # highest budget
    print(rank_movies(df, 'budget_musd'))
    
    # highest profit
    print(rank_movies(df, 'profit'))
    
    # lowest profit
    print(rank_movies(df, 'profit', ascending=True))
    
    # highest ROI (budget >= 10M)
    print(rank_movies(df, 'roi', filter_col='budget_musd', filter_val=10))
    
    # lowest ROI (budget >= 10M)
    print(rank_movies(df, 'roi', ascending=True, filter_col='budget_musd', filter_val=10))
    
    # most voted
    print(rank_movies(df, 'vote_count'))
    
    # highest rated (votes >= 10)
    print(rank_movies(df, 'vote_average', filter_col='vote_count', filter_val=10))
    
    # lowest rated (votes >= 10)
    print(rank_movies(df, 'vote_average', ascending=True, filter_col='vote_count', filter_val=10))
    
    # most popular
    print(rank_movies(df, 'popularity'))
    
    # finding sci-fi action movies with Bruce Willis
    mask_scifi = df['genres'].str.contains('Science Fiction', na=False)
    mask_action = df['genres'].str.contains('Action', na=False)
    mask_bruce = df['cast'].str.contains('Bruce Willis', na=False)
    
    bruce_movies = df[mask_scifi & mask_action & mask_bruce]
    bruce_movies = bruce_movies.sort_values('vote_average', ascending=False)
    print(bruce_movies[['title', 'vote_average', 'release_date']])
    
    # Uma Thurman and Quentin Tarantino movies
    mask_uma = df['cast'].str.contains('Uma Thurman', na=False)
    mask_qt = df['director'].str.contains('Quentin Tarantino', na=False)
    
    uma_qt_movies = df[mask_uma & mask_qt]
    uma_qt_movies = uma_qt_movies.sort_values('runtime')
    print(uma_qt_movies[['title', 'runtime', 'release_date']])
    
    # franchise vs standalone comparison
    df['is_franchise'] = df['belongs_to_collection'].apply(lambda x: True if x else False)
    
    franchise_stats = df.groupby('is_franchise').agg({
        'revenue_musd': 'mean',
        'roi': 'median',
        'budget_musd': 'mean',
        'popularity': 'mean',
        'vote_average': 'mean'
    })
    franchise_stats = franchise_stats.rename(index={True: 'Franchise', False: 'Standalone'})
    print(franchise_stats)
    
    # most successful franchises
    franchise_df = df[df['is_franchise']]
    franchise_df = franchise_df.groupby('belongs_to_collection').agg({
        'title': 'count',
        'budget_musd': ['sum', 'mean'],
        'revenue_musd': ['sum', 'mean'],
        'vote_average': 'mean'
    })
    franchise_df.columns = ['movie_count', 'total_budget', 'mean_budget', 'total_revenue', 'mean_revenue', 'mean_rating']
    print(franchise_df.sort_values('total_revenue', ascending=False).head(5))
    
    # most successful directors
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

