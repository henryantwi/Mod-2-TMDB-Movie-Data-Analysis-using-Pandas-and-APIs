"""
Movie Data Analysis Pipeline
============================
This module orchestrates the entire ETL (Extract, Transform, Load) process
for movie data analysis.

Pipeline Steps:
1. Extract: Fetch movie data from TMDB API
2. Transform: Clean and process the raw data
3. Load/Analyze: Run analysis and generate visualizations
"""

import argparse
from pathlib import Path

# Import functions from other modules
from fetch_data import fetch_specific_movies, save_raw_data
from process_data import load_raw_data, process_data, save_processed_data
from analysis import load_processed_data, analyze_movies
from visualization import create_all_visualizations


# Default movie IDs from assignment
DEFAULT_MOVIE_IDS = [
    299534, 19995, 140607, 299536, 597, 135397, 420818, 24428, 
    168259, 99861, 284054, 12445, 181808, 330457, 351286, 
    109445, 321612, 260513
]


def run_extract(movie_ids=None, skip_if_exists=False):
    """
    Step 1: Extract - Fetch movie data from TMDB API.
    
    Args:
        movie_ids: List of TMDB movie IDs to fetch. Uses defaults if None.
        skip_if_exists: If True, skip fetching if raw data already exists.
    """
    print("\n" + "=" * 60)
    print("STEP 1: EXTRACT - Fetching movie data from TMDB API")
    print("=" * 60)
    
    raw_data_path = Path("data/raw/movies.json")
    
    if skip_if_exists and raw_data_path.exists():
        print(f"Raw data already exists at {raw_data_path}. Skipping fetch.")
        return True
    
    if movie_ids is None:
        movie_ids = DEFAULT_MOVIE_IDS
    
    print(f"Fetching {len(movie_ids)} movies...")
    movies_data = fetch_specific_movies(movie_ids)
    
    if movies_data:
        save_raw_data(movies_data)
        print(f"Successfully fetched {len(movies_data)} movies.")
        return True
    else:
        print("No movie data fetched. Check your API key and network connection.")
        return False


def run_transform():
    """
    Step 2: Transform - Clean and process the raw movie data.
    """
    print("\n" + "=" * 60)
    print("STEP 2: TRANSFORM - Processing and cleaning data")
    print("=" * 60)
    
    try:
        print("Loading raw data...")
        df_raw = load_raw_data()
        print(f"Loaded {len(df_raw)} raw movie records.")
        
        print("Processing data...")
        df_clean = process_data(df_raw)
        print(f"Processed data contains {len(df_clean)} records.")
        
        print("Saving processed data...")
        save_processed_data(df_clean)
        
        return True
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run the extract step first.")
        return False
    except Exception as e:
        print(f"Error during transformation: {e}")
        return False


def run_analyze():
    """
    Step 3a: Analyze - Run analysis on the processed data.
    """
    print("\n" + "=" * 60)
    print("STEP 3a: ANALYZE - Running movie analysis")
    print("=" * 60)
    
    try:
        df = load_processed_data()
        print(f"Loaded {len(df)} processed movie records for analysis.\n")
        
        franchise_stats, franchise_df, director_df = analyze_movies(df)
        
        print("\nAnalysis complete!")
        return True
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run the transform step first.")
        return False
    except Exception as e:
        print(f"Error during analysis: {e}")
        return False


def run_visualize():
    """
    Step 3b: Visualize - Generate visualizations from the processed data.
    """
    print("\n" + "=" * 60)
    print("STEP 3b: VISUALIZE - Creating visualizations")
    print("=" * 60)
    
    try:
        from visualization import load_processed_data as load_viz_data
        df = load_viz_data()
        print(f"Loaded {len(df)} records for visualization.\n")
        
        create_all_visualizations(df)
        
        print("Visualizations saved to data/processed/ directory.")
        return True
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run the transform step first.")
        return False
    except Exception as e:
        print(f"Error during visualization: {e}")
        return False


def run_full_pipeline(movie_ids=None, skip_fetch=False):
    """
    Run the complete ETL pipeline.
    
    Args:
        movie_ids: Optional list of movie IDs to fetch.
        skip_fetch: If True, skip the extract step (use existing raw data).
    """
    print("\n" + "#" * 60)
    print("#" + " " * 18 + "MOVIE DATA PIPELINE" + " " * 19 + "#")
    print("#" * 60)
    
    # Step 1: Extract
    if not skip_fetch:
        if not run_extract(movie_ids):
            print("\nPipeline stopped: Extract step failed.")
            return False
    else:
        print("\n[Skipping extract step - using existing raw data]")
    
    # Step 2: Transform
    if not run_transform():
        print("\nPipeline stopped: Transform step failed.")
        return False
    
    # Step 3a: Analyze
    if not run_analyze():
        print("\nPipeline stopped: Analysis step failed.")
        return False
    
    # Step 3b: Visualize
    if not run_visualize():
        print("\nPipeline stopped: Visualization step failed.")
        return False
    
    print("\n" + "#" * 60)
    print("#" + " " * 15 + "PIPELINE COMPLETE!" + " " * 23 + "#")
    print("#" * 60)
    
    return True


def main():
    """Main entry point with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="Movie Data Analysis ETL Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py                    # Run full pipeline
  python pipeline.py --skip-fetch       # Skip API fetch, use existing raw data
  python pipeline.py --step extract     # Run only extract step
  python pipeline.py --step transform   # Run only transform step
  python pipeline.py --step analyze     # Run only analyze step
  python pipeline.py --step visualize   # Run only visualize step
        """
    )
    
    parser.add_argument(
        '--skip-fetch', 
        action='store_true',
        help='Skip the extract step and use existing raw data'
    )
    
    parser.add_argument(
        '--step',
        choices=['extract', 'transform', 'analyze', 'visualize', 'all'],
        default='all',
        help='Run a specific pipeline step (default: all)'
    )
    
    args = parser.parse_args()
    
    if args.step == 'all':
        run_full_pipeline(skip_fetch=args.skip_fetch)
    elif args.step == 'extract':
        run_extract()
    elif args.step == 'transform':
        run_transform()
    elif args.step == 'analyze':
        run_analyze()
    elif args.step == 'visualize':
        run_visualize()


if __name__ == "__main__":
    main()
