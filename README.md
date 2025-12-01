# TMDB Movie Data Analysis

## Overview
This project analyzes movie data from the TMDB API. It fetches data, processes it to clean and transform it, and performs exploratory data analysis (EDA) to identify trends and rank movies.

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

1.  **Fetch Data**:
    ```bash
    python src/fetch_data.py
    ```
    This will save raw data to `data/raw/movies.json`.

2.  **Process Data**:
    ```bash
    python src/process_data.py
    ```
    This will clean the data and save it to `data/processed/movies_cleaned.csv`.

3.  **Analyze Data**:
    ```bash
    python src/analysis.py
    ```
    This will generate analysis reports and charts.
