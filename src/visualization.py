"""
Movie Data Visualization Module

This module creates 5 key visualizations to analyze movie performance data.
Each function is carefully documented to explain:
- WHY that specific plot type was chosen
- WHAT the visualization shows
- HOW to interpret the output

For a detailed, beginner-friendly explanation of each visualization, 
see VISUALIZATION_GUIDE.md in the project root.

Quick Plot Type Reference:
- Scatter Plot: Shows relationships between two continuous variables
- Box Plot: Shows distribution, median, quartiles, and outliers
- Line Plot: Shows trends over time or ordered data
- Bar Chart: Compares values across different categories
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def load_processed_data(filename="data/processed/movies_cleaned.csv"):
    filepath = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"{filename} not found. Please run process_data.py first.")

    df = pd.read_csv(filepath)
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['release_year'] = df['release_date'].dt.year
    df['belongs_to_collection'] = df['belongs_to_collection'].fillna('')
    df['is_franchise'] = df['belongs_to_collection'].apply(lambda x: True if x else False)
    return df


def plot_revenue_vs_budget(df, output_dir):
    """
    Creates a scatter plot showing the relationship between movie budget and revenue.
    
    Why scatter plot? 
    - Best for visualizing relationships between two continuous numerical variables
    - Each point represents one movie
    - Pattern of dots reveals correlation (or lack thereof)
    
    What it shows:
    - Whether bigger budgets lead to bigger revenues
    - If franchise movies perform differently than standalone movies
    - Outliers (movies that performed unusually well or poorly)
    """
    plt.figure(figsize=(10, 6))  # Set canvas size (width=10 inches, height=6 inches)
    
    # Scatter plot with color coding by franchise status
    # alpha=0.7 makes points semi-transparent so overlapping points are visible
    sns.scatterplot(data=df, x='budget_musd', y='revenue_musd', hue='is_franchise', alpha=0.7)
    
    plt.title('Revenue vs Budget')
    plt.xlabel('Budget (MUSD)')  # Millions of USD
    plt.ylabel('Revenue (MUSD)')
    plt.savefig(output_dir / 'revenue_vs_budget.png')
    plt.close()  # Free memory and prevent plots from overlapping


def plot_roi_by_genre(df, output_dir):
    """
    Creates a box plot showing ROI (Return on Investment) distribution across genres.
    
    Why box plot?
    - Shows the full distribution, not just averages
    - Reveals consistency (narrow box) vs. volatility (wide box)
    - Highlights outliers (exceptional successes or failures)
    
    What it shows:
    - Which genres typically have better ROI
    - Which genres are riskier (more variable returns)
    - Outlier movies that performed exceptionally well or poorly
    """
    # Split movies with multiple genres into separate rows
    # e.g., "Action|Adventure|Sci-Fi" becomes 3 rows, one for each genre
    df_genres = df.assign(genre=df['genres'].str.split('|')).explode('genre')
    
    # Find the 5 most common genres (keeps the plot clean and readable)
    top_genres = df_genres['genre'].value_counts().head(5).index
    df_top_genres = df_genres[df_genres['genre'].isin(top_genres)]

    plt.figure(figsize=(12, 6))  # Wider to accommodate multiple boxes
    
    # Box plot shows: median, quartiles, range, and outliers
    sns.boxplot(data=df_top_genres, x='genre', y='roi')
    
    plt.title('ROI Distribution by Top 5 Genres')
    plt.ylim(-1, 10)  # Limit y-axis to keep scale readable (extreme outliers would squash the view)
    plt.savefig(output_dir / 'roi_by_genre.png')
    plt.close()


def plot_popularity_vs_rating(df, output_dir):
    """
    Creates a scatter plot comparing movie ratings with their popularity scores.
    
    Why scatter plot?
    - Examines correlation between two different metrics
    - Each point is a movie
    - Shows if quality (rating) predicts buzz (popularity)
    
    What it shows:
    - Whether highly-rated movies are also popular
    - If marketing can make mediocre movies popular
    - Hidden gems (high rating, low popularity)
    """
    plt.figure(figsize=(10, 6))
    
    # alpha=0.6 (even more transparent) helps see density when points overlap
    sns.scatterplot(data=df, x='vote_average', y='popularity', alpha=0.6)
    
    plt.title('Popularity vs Rating')
    plt.xlabel('Vote Average')  # Quality score (1-10)
    plt.ylabel('Popularity')     # Buzz/attention score
    plt.savefig(output_dir / 'popularity_vs_rating.png')
    plt.close()


def plot_yearly_trends(df, output_dir):
    """
    Creates a line plot showing box office revenue trends over time.
    
    Why line plot?
    - Standard visualization for time-series data
    - Shows trends clearly (growth, decline, stability)
    - Connected points emphasize continuity over time
    
    What it shows:
    - Whether the movie industry is growing or shrinking
    - Years with exceptional or poor performance
    - Long-term industry trends
    """
    # Aggregate total revenue by year (sum all movies released that year)
    yearly_stats = df.groupby('release_year')['revenue_musd'].sum().reset_index()

    plt.figure(figsize=(12, 6))  # Wider for time-series data
    
    # Line plot with markers at each data point
    # marker='o' adds dots to show exact year positions
    sns.lineplot(data=yearly_stats, x='release_year', y='revenue_musd', marker='o')
    
    plt.title('Yearly Trends in Box Office Revenue')
    plt.xlabel('Year')
    plt.ylabel('Total Revenue (MUSD)')  # Total for all movies that year
    plt.savefig(output_dir / 'yearly_trends.png')
    plt.close()


def plot_franchise_vs_standalone(df, output_dir):
    """
    Creates a grouped bar chart comparing franchise movies to standalone movies.
    
    Why grouped bar chart?
    - Compares two groups (franchise vs. standalone) across multiple metrics
    - Side-by-side bars make differences immediately obvious
    - Height of bars = easy visual comparison
    
    What it shows:
    - Whether franchises spend more on production (budget)
    - Whether franchises make more money (revenue)
    - The magnitude of difference between the two categories
    """
    # Calculate average budget and revenue for each group
    # Using 'mean' because we want typical performance, not totals
    franchise_stats = df.groupby('is_franchise').agg({
        'revenue_musd': 'mean',
        'budget_musd': 'mean'
    }).reset_index()

    # Convert True/False to readable labels
    franchise_stats['is_franchise'] = franchise_stats['is_franchise'].map({
        True: 'Franchise',
        False: 'Standalone'
    })

    # Transform data from wide to long format (required for seaborn grouped bars)
    # Before: one row per group with multiple metric columns
    # After: one row per group-metric combination
    franchise_melt = franchise_stats.melt(
        id_vars='is_franchise',
        value_vars=['revenue_musd', 'budget_musd'],
        var_name='Metric',
        value_name='Value (MUSD)'
    )

    plt.figure(figsize=(10, 6))
    
    # hue creates grouped bars (one per franchise status)
    # hue_order ensures consistent ordering (Standalone always first)
    sns.barplot(data=franchise_melt, x='Metric', y='Value (MUSD)', hue='is_franchise', hue_order=['Standalone', 'Franchise'])
    
    plt.title('Franchise vs Standalone: Revenue & Budget')
    plt.savefig(output_dir / 'franchise_vs_standalone.png')
    plt.close()


def create_all_visualizations(df):
    sns.set_theme(style="whitegrid")

    output_dir = Path('data/processed')
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_revenue_vs_budget(df, output_dir)
    plot_roi_by_genre(df, output_dir)
    plot_popularity_vs_rating(df, output_dir)
    plot_yearly_trends(df, output_dir)
    plot_franchise_vs_standalone(df, output_dir)


if __name__ == "__main__":
    df = load_processed_data()
    create_all_visualizations(df)
