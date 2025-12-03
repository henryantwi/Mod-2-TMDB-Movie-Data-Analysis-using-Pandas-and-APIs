import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def load_processed_data(filename="data/processed/movies_cleaned.csv"):
    """Loads processed data from CSV."""
    filepath = Path(filename)
    if not filepath.exists():
        raise FileNotFoundError(f"{filename} not found. Please run process_data.py first.")

    df = pd.read_csv(filepath)
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['release_year'] = df['release_date'].dt.year
    df['is_franchise'] = df['belongs_to_collection'].apply(lambda x: True if x else False)
    return df


def plot_revenue_vs_budget(df, output_dir):
    """1. Revenue vs. Budget Trends"""
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='budget_musd', y='revenue_musd', hue='is_franchise', alpha=0.7)
    plt.title('Revenue vs Budget')
    plt.xlabel('Budget (Million USD)')
    plt.ylabel('Revenue (Million USD)')
    plt.legend(title='Franchise')

    output_path = output_dir / 'revenue_vs_budget.png'
    plt.savefig(output_path)
    plt.close()
    print(f"Saved {output_path}")


def plot_roi_by_genre(df, output_dir):
    """2. ROI Distribution by Genre"""
    # Explode genres (split pipe-separated values into rows)
    df_genres = df.assign(genre=df['genres'].str.split('|')).explode('genre')

    # Get top 5 most common genres
    top_genres = df_genres['genre'].value_counts().head(5).index
    df_top_genres = df_genres[df_genres['genre'].isin(top_genres)]

    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_top_genres, x='genre', y='roi')
    plt.title('ROI Distribution by Top 5 Genres')
    plt.xlabel('Genre')
    plt.ylabel('ROI (Return on Investment)')
    plt.ylim(-1, 10)  # Limit y-axis to see distribution better

    output_path = output_dir / 'roi_by_genre.png'
    plt.savefig(output_path)
    plt.close()
    print(f"Saved {output_path}")


def plot_popularity_vs_rating(df, output_dir):
    """3. Popularity vs. Rating"""
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='vote_average', y='popularity', alpha=0.6)
    plt.title('Popularity vs Rating')
    plt.xlabel('Vote Average')
    plt.ylabel('Popularity')

    output_path = output_dir / 'popularity_vs_rating.png'
    plt.savefig(output_path)
    plt.close()
    print(f"Saved {output_path}")


def plot_yearly_trends(df, output_dir):
    """4. Yearly Trends in Box Office Performance"""
    yearly_stats = df.groupby('release_year')['revenue_musd'].sum().reset_index()

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=yearly_stats, x='release_year', y='revenue_musd', marker='o')
    plt.title('Yearly Trends in Box Office Revenue')
    plt.xlabel('Year')
    plt.ylabel('Total Revenue (Million USD)')

    output_path = output_dir / 'yearly_trends.png'
    plt.savefig(output_path)
    plt.close()
    print(f"Saved {output_path}")


def plot_franchise_vs_standalone(df, output_dir):
    """5. Comparison of Franchise vs. Standalone Success"""
    # Calculate stats for franchise vs standalone
    franchise_stats = df.groupby('is_franchise').agg({
        'revenue_musd': 'mean',
        'budget_musd': 'mean'
    }).reset_index()

    # Rename for better labels
    franchise_stats['is_franchise'] = franchise_stats['is_franchise'].map({
        True: 'Franchise',
        False: 'Standalone'
    })

    # Melt for grouped bar chart
    franchise_melt = franchise_stats.melt(
        id_vars='is_franchise',
        value_vars=['revenue_musd', 'budget_musd'],
        var_name='Metric',
        value_name='Value (Million USD)'
    )

    # Rename metrics for better labels
    franchise_melt['Metric'] = franchise_melt['Metric'].map({
        'revenue_musd': 'Avg Revenue',
        'budget_musd': 'Avg Budget'
    })

    plt.figure(figsize=(10, 6))
    sns.barplot(data=franchise_melt, x='Metric', y='Value (Million USD)', hue='is_franchise')
    plt.title('Franchise vs Standalone: Average Revenue & Budget')
    plt.legend(title='Movie Type')

    output_path = output_dir / 'franchise_vs_standalone.png'
    plt.savefig(output_path)
    plt.close()
    print(f"Saved {output_path}")


def create_all_visualizations(df):
    """Generate all visualizations."""
    # Set seaborn theme
    sns.set_theme(style="whitegrid")

    # Create output directory
    output_dir = Path('data/processed')
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n=== Generating Visualizations ===\n")

    # 1. Revenue vs Budget
    # plot_revenue_vs_budget(df, output_dir)

    # 2. ROI by Genre
    plot_roi_by_genre(df, output_dir)

    # # 3. Popularity vs Rating
    plot_popularity_vs_rating(df, output_dir)

    # # 4. Yearly Trends
    # plot_yearly_trends(df, output_dir)

    # # 5. Franchise vs Standalone
    # plot_franchise_vs_standalone(df, output_dir)

    print("\n=== All visualizations complete! ===")


if __name__ == "__main__":
    print("Loading processed data...")
    df = load_processed_data()

    print("Creating visualizations...")
    create_all_visualizations(df)
