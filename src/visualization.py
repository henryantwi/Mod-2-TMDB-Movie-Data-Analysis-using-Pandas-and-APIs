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
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='budget_musd', y='revenue_musd', hue='is_franchise', alpha=0.7)
    plt.title('Revenue vs Budget')
    plt.xlabel('Budget (MUSD)')
    plt.ylabel('Revenue (MUSD)')
    plt.savefig(output_dir / 'revenue_vs_budget.png')
    plt.close()


def plot_oi_by_genre(df, output_dir):
    df_genres = df.assign(genre=df['genres'].str.split('|')).explode('genre')
    top_genres = df_genres['genre'].value_counts().head(5).index
    df_top_genres = df_genres[df_genres['genre'].isin(top_genres)]

    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_top_genres, x='genre', y='roi')
    plt.title('ROI Distribution by Top 5 Genres')
    plt.ylim(-1, 10)
    plt.savefig(output_dir / 'roi_by_genre.png')
    plt.close()


def plot_popularity_vs_rating(df, output_dir):
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='vote_average', y='popularity', alpha=0.6)
    plt.title('Popularity vs Rating')
    plt.xlabel('Vote Average')
    plt.ylabel('Popularity')
    plt.savefig(output_dir / 'popularity_vs_rating.png')
    plt.close()


def plot_yearly_trends(df, output_dir):
    yearly_stats = df.groupby('release_year')['revenue_musd'].sum().reset_index()

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=yearly_stats, x='release_year', y='revenue_musd', marker='o')
    plt.title('Yearly Trends in Box Office Revenue')
    plt.xlabel('Year')
    plt.ylabel('Total Revenue (MUSD)')
    plt.savefig(output_dir / 'yearly_trends.png')
    plt.close()


def plot_franchise_vs_standalone(df, output_dir):
    franchise_stats = df.groupby('is_franchise').agg({
        'revenue_musd': 'mean',
        'budget_musd': 'mean'
    }).reset_index()

    franchise_stats['is_franchise'] = franchise_stats['is_franchise'].map({
        True: 'Franchise',
        False: 'Standalone'
    })

    franchise_melt = franchise_stats.melt(
        id_vars='is_franchise',
        value_vars=['revenue_musd', 'budget_musd'],
        var_name='Metric',
        value_name='Value (MUSD)'
    )

    plt.figure(figsize=(10, 6))
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
