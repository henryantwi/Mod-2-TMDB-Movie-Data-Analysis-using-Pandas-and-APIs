import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_processed_data(filename="data/processed/movies_cleaned.csv"):
    """Loads processed data from CSV."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found. Please run process_data.py first.")
    df = pd.read_csv(filename)
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['release_year'] = df['release_date'].dt.year
    return df

def analyze_movies(df):
    """Performs comprehensive analysis on the movie dataset."""
    
    # --- 1. Identify Best/Worst Performing Movies ---
    print("\n=== 1. Best/Worst Performing Movies ===")
    
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
    
    
    # --- 2. Advanced Movie Filtering ---
    print("\n=== 2. Advanced Movie Filtering ===")
    
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
    
    
    # --- 3. Franchise vs Standalone ---
    print("\n=== 3. Franchise vs Standalone Analysis ===")
    
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
    
    
    # --- 4. Most Successful Franchises & Directors ---
    print("\n=== 4. Most Successful Franchises & Directors ===")
    
    # Franchises
    franchise_df = df[df['is_franchise']].groupby('belongs_to_collection').agg({
        'title': 'count',
        'budget_musd': ['sum', 'mean'],
        'revenue_musd': ['sum', 'mean'],
        'vote_average': 'mean'
    })
    franchise_df.columns = ['movie_count', 'total_budget', 'mean_budget', 'total_revenue', 'mean_revenue', 'mean_rating']
    print("\n--- Top 5 Franchises by Total Revenue ---")
    print(franchise_df.sort_values('total_revenue', ascending=False).head(5))
    
    # Directors
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

def plot_data(df, franchise_stats):
    """Generates plots for analysis."""
    sns.set_theme(style="whitegrid")
    os.makedirs('data/processed', exist_ok=True)
    
    # 1. Revenue vs Budget
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='budget_musd', y='revenue_musd', hue='is_franchise', alpha=0.7)
    plt.title('Revenue vs Budget')
    plt.xlabel('Budget (MUSD)')
    plt.ylabel('Revenue (MUSD)')
    plt.savefig('data/processed/revenue_vs_budget.png')
    plt.close()
    print("Saved revenue_vs_budget.png")
    
    # 2. ROI Distribution by Genre (Top 5 genres)
    # Explode genres first
    df_genres = df.assign(genre=df['genres'].str.split('|')).explode('genre')
    top_genres = df_genres['genre'].value_counts().head(5).index
    df_top_genres = df_genres[df_genres['genre'].isin(top_genres)]
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_top_genres, x='genre', y='roi')
    plt.title('ROI Distribution by Top 5 Genres')
    plt.ylim(-1, 10) # Limit y-axis to see distribution better
    plt.savefig('data/processed/roi_by_genre.png')
    plt.close()
    print("Saved roi_by_genre.png")
    
    # 3. Popularity vs Rating
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='vote_average', y='popularity', alpha=0.6)
    plt.title('Popularity vs Rating')
    plt.xlabel('Vote Average')
    plt.ylabel('Popularity')
    plt.savefig('data/processed/popularity_vs_rating.png')
    plt.close()
    print("Saved popularity_vs_rating.png")
    
    # 4. Franchise vs Standalone Comparison (Bar Chart)
    # Reset index to plot
    franchise_plot = franchise_stats.reset_index()
    # Melt for seaborn
    franchise_melt = franchise_plot.melt(id_vars='is_franchise', value_vars=['revenue_musd', 'budget_musd'], var_name='Metric', value_name='Value (MUSD)')
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=franchise_melt, x='Metric', y='Value (MUSD)', hue='is_franchise')
    plt.title('Franchise vs Standalone: Revenue & Budget')
    plt.savefig('data/processed/franchise_vs_standalone.png')
    plt.close()
    print("Saved franchise_vs_standalone.png")

    # 5. Yearly Trends in Box Office Performance
    yearly_stats = df.groupby('release_year')['revenue_musd'].sum().reset_index()
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=yearly_stats, x='release_year', y='revenue_musd', marker='o')
    plt.title('Yearly Trends in Box Office Revenue')
    plt.xlabel('Year')
    plt.ylabel('Total Revenue (MUSD)')
    plt.savefig('data/processed/yearly_trends.png')
    plt.close()
    print("Saved yearly_trends.png")

if __name__ == "__main__":
    print("Loading processed data...")
    df = load_processed_data()
    
    print("Analyzing data...")
    franchise_stats, _, _ = analyze_movies(df)
    
    print("Plotting data...")
    plot_data(df, franchise_stats)

