# TMDB Movie Data Analysis

## Overview
This project analyzes movie data from the TMDB API. It fetches data, processes it to clean and transform it, and performs exploratory data analysis (EDA) to identify trends and rank movies.

## Project Structure
```
Movie-Data-Analysis/
├── data/
│   ├── raw/                    # Raw data from API
│   │   └── movies.json
│   └── processed/              # Cleaned data and visualizations
│       └── movies_cleaned.csv
├── notebooks/
│   └── movie_analysis.ipynb    # Interactive analysis notebook
├── src/
│   ├── fetch_data.py           # Step 1: Fetch data from TMDB API
│   ├── process_data.py         # Step 2: Clean and transform data
│   ├── analysis.py             # Step 3: KPI implementation and analysis
│   └── visualization.py        # Step 4: Data visualization
├── requirements.txt
└── README.md
```

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **API Key**:
    - Obtain an API Key from [TMDB](https://www.themoviedb.org/documentation/api).
    - Create a `.env` file in the root directory.
    - Add your key: `TMDB_API_KEY=your_api_key_here`

## Usage

1.  **Fetch Data** (Step 1):
    ```bash
    python src/fetch_data.py
    ```
    This will save raw data to `data/raw/movies.json`.

2.  **Process Data** (Step 2):
    ```bash
    python src/process_data.py
    ```
    This will clean the data and save it to `data/processed/movies_cleaned.csv`.

3.  **Analyze Data** (Step 3):
    ```bash
    python src/analysis.py
    ```
    This performs KPI analysis including:
    - Best/Worst performing movies (revenue, profit, ROI, ratings)
    - Advanced movie filtering and search queries
    - Franchise vs. standalone movie comparison
    - Most successful franchises and directors

4.  **Generate Visualizations** (Step 4):
    ```bash
    python src/visualization.py
    ```
    This creates the following charts in `data/processed/`:
    - `revenue_vs_budget.png` - Revenue vs Budget scatter plot
    - `roi_by_genre.png` - ROI distribution by top 5 genres
    - `popularity_vs_rating.png` - Popularity vs Rating scatter plot
    - `yearly_trends.png` - Yearly box office revenue trends
    - `franchise_vs_standalone.png` - Franchise vs Standalone comparison

## Interactive Notebook
For interactive exploration, open `notebooks/movie_analysis.ipynb` which combines all steps with inline visualizations.
