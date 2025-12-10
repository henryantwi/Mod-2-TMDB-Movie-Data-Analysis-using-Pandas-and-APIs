# TMDB Movie Data Analysis 🎬

## What This Project Is About

I built this project to dive into movie data and see what makes films successful at the box office. Using data from The Movie Database (TMDB) API, I wanted to answer questions like: Do franchises really outperform standalone films? Which directors consistently deliver hits? And is there actually a relationship between a movie's budget and its revenue?

This turned into a full ETL (Extract, Transform, Load) pipeline that pulls movie data, cleans it up, runs analysis, and generates visualizations — all automated so I can easily update it with new movies.

## My Approach

### Breaking Down the Problem

I tackled this project in stages, which made it much easier to debug and iterate:

1. **Data Extraction** — First, I needed to get the data. I wrote a script to hit the TMDB API and pull detailed information for a curated list of movies (mostly blockbusters, since they have the most interesting financial data).

2. **Data Cleaning & Transformation** — Raw API data is messy. JSON nested inside JSON, inconsistent formats, missing values... the usual. I spent a good chunk of time figuring out how to flatten the nested structures (like extracting genre names from JSON objects) and handling edge cases like movies with zero budget or revenue.

3. **Analysis** — Once the data was clean, I built functions to rank movies by different metrics and answer specific questions. I also added filters (like requiring a minimum budget for ROI calculations) to avoid misleading results from low-budget outliers.

4. **Visualization** — Numbers are great, but charts tell the story better. I created several plots to visualize trends and comparisons.

5. **Pipeline Orchestration** — Finally, I tied everything together in a single pipeline script so I can run the entire process with one command.

### Challenges I Ran Into

- **Nested JSON parsing**: The credits data (cast and crew) was deeply nested. I had to write custom functions to extract director names and top cast members.
  
- **Handling missing data**: Some movies had budget or revenue listed as 0, which would break ROI calculations. I converted these to NaN and handled them appropriately in the analysis.

- **Filtering for meaningful results**: Without filters, the "highest ROI" list was dominated by tiny films that happened to do okay. Adding minimum thresholds (like budget ≥ $10M) gave much more useful insights.

## Project Structure

```
Movie-Data-Analysis/
├── data/
│   ├── raw/                    # Raw JSON from TMDB API
│   │   └── movies.json
│   └── processed/              # Cleaned CSV + generated charts
│       └── movies_cleaned.csv
├── notebooks/
│   └── movie_analysis.ipynb    # Interactive exploration
├── src/
│   ├── fetch_data.py           # Pulls data from TMDB API
│   ├── process_data.py         # Cleans and transforms the data
│   ├── analysis.py             # Runs rankings and analysis
│   ├── visualization.py        # Generates charts
│   └── pipeline.py             # Orchestrates the full ETL process
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

You'll need Python 3.8+ and a TMDB API key.

### Installation

1. **Clone the repo and install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2. **Set up your API key**:
    - Get a free API key from [TMDB](https://www.themoviedb.org/documentation/api)
    - Create a `.env` file in the project root
    - Add your key:
      ```
      TMDB_API_KEY=your_api_key_here
      ```

### Running the Pipeline

The easiest way to run everything is with the pipeline script:

```bash
# Run the full pipeline (fetch → process → analyze → visualize)
python src/pipeline.py

# If you already have raw data and just want to re-process it
python src/pipeline.py --skip-fetch

# Run individual steps if needed
python src/pipeline.py --step extract
python src/pipeline.py --step transform
python src/pipeline.py --step analyze
python src/pipeline.py --step visualize
```

### Running Steps Individually

If you prefer to run each step separately:

```bash
# 1. Fetch data from TMDB
python src/fetch_data.py

# 2. Clean and process the data
python src/process_data.py

# 3. Run analysis
python src/analysis.py

# 4. Generate visualizations
python src/visualization.py
```

## What the Analysis Covers

- **Top/Bottom Rankings**: Movies ranked by revenue, budget, profit, ROI, ratings, and popularity
- **Filtered Queries**: Finding specific movies (e.g., sci-fi action films with Bruce Willis)
- **Franchise vs Standalone**: Comparing performance metrics between franchise films and one-offs
- **Director Analysis**: Which directors have the highest total revenue and best average ratings
- **Franchise Deep Dive**: Most successful movie franchises by total revenue

## Visualizations Generated

The pipeline creates these charts in `data/processed/`:

| Chart | What It Shows |
|-------|---------------|
| `revenue_vs_budget.png` | Scatter plot showing the relationship between budget and revenue |
| `roi_by_genre.png` | Box plot of ROI distribution across the top 5 genres |
| `popularity_vs_rating.png` | How popularity correlates (or doesn't) with ratings |
| `yearly_trends.png` | Box office revenue trends over time |
| `franchise_vs_standalone.png` | Side-by-side comparison of franchise vs standalone metrics |

**📚 New to data visualization?** Check out [VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md) for a beginner-friendly explanation of each chart type, why it was chosen, and how to interpret the results. Perfect for code reviews!

## Interactive Exploration

For a more hands-on experience, check out the Jupyter notebook at `notebooks/movie_analysis.ipynb`. It walks through the same analysis with inline outputs and lets you experiment with the data.

## Key Takeaways

After running the analysis, a few things stood out:
- Franchise films generally have higher budgets AND higher revenues, but the ROI isn't always better
- There's a surprisingly weak correlation between ratings and popularity
- A handful of directors dominate the total revenue charts

---

*Built as part of a Data Engineering learning project. Feel free to fork and adapt for your own movie analysis!*
