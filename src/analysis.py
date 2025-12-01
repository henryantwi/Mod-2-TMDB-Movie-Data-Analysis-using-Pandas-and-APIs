import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def load_processed_data(filename="data/processed/movies_cleaned.csv"):
    """Loads processed data from CSV."""
    if not os.path.exists(filename):
        raise FileNotFoundError(f"{filename} not found. Please run process_data.py first.")
    return pd.read_csv(filename)

def analyze_movies(df):
    """Performs analysis on the movie dataset."""
    print("\n--- Basic Statistics ---")
    print(df.describe())
    
    # Top 10 Movies by Vote Average (with minimum vote count)
    min_votes = df['vote_count'].quantile(0.9)
    top_movies = df[df['vote_count'] >= min_votes].sort_values('vote_average', ascending=False).head(10)
    print("\n--- Top 10 Movies (Weighted) ---")
    print(top_movies[['title', 'vote_average', 'vote_count']])
    
    # Top 10 Popular Movies
    popular_movies = df.sort_values('popularity', ascending=False).head(10)
    print("\n--- Top 10 Popular Movies ---")
    print(popular_movies[['title', 'popularity']])
    
    # Top 10 Movies by Revenue
    revenue_movies = df.sort_values('revenue', ascending=False).head(10)
    print("\n--- Top 10 Movies by Revenue ---")
    print(revenue_movies[['title', 'revenue']])

    # Top 10 Movies by ROI (Budget > 1M to avoid outliers)
    roi_movies = df[df['budget'] > 1000000].sort_values('roi', ascending=False).head(10)
    print("\n--- Top 10 Movies by ROI ---")
    print(roi_movies[['title', 'roi', 'budget', 'revenue']])
    
    return top_movies, popular_movies, revenue_movies, roi_movies

def plot_data(df):
    """Generates plots for analysis."""
    sns.set_theme(style="whitegrid")
    
    # Distribution of Vote Average
    plt.figure(figsize=(10, 6))
    sns.histplot(df['vote_average'], bins=20, kde=True)
    plt.title('Distribution of Vote Average')
    plt.xlabel('Vote Average')
    plt.ylabel('Count')
    plt.savefig('data/processed/vote_distribution.png')
    print("Saved vote_distribution.png")
    
    # Popularity vs Vote Average
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='vote_average', y='popularity', alpha=0.5)
    plt.title('Popularity vs Vote Average')
    plt.xlabel('Vote Average')
    plt.ylabel('Popularity')
    plt.savefig('data/processed/popularity_vs_vote.png')
    print("Saved popularity_vs_vote.png")

if __name__ == "__main__":
    print("Loading processed data...")
    df = load_processed_data()
    
    print("Analyzing data...")
    analyze_movies(df)
    
    print("Plotting data...")
    plot_data(df)
