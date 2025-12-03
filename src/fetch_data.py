import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv('TMDB_API_KEY')
BASE_URL = "https://api.themoviedb.org/3"

def fetch_movie_details(movie_id):
    """
    Fetches details for a specific movie ID.
    """
    if not API_KEY:
        raise ValueError("TMDB_API_KEY not found in environment variables.")
        
    url = f"{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US&append_to_response=credits"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movie {movie_id}: {e}")
        return None

def fetch_specific_movies(movie_ids):
    """
    Fetches data for a list of movie IDs.
    """
    movies = []
    for i, movie_id in enumerate(movie_ids):
        print(f"Fetching movie {i+1}/{len(movie_ids)}: ID {movie_id}")
        data = fetch_movie_details(movie_id)
        if data:
            movies.append(data)
    return movies

def save_raw_data(data, filename=Path("data") / "raw" / "movies.json"):
    """Saves the fetched data to a JSON file."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"Saved {len(data)} movies to {path}")

if __name__ == "__main__":
    # List of IDs from assignment
    movie_ids = [0, 299534, 19995, 140607, 299536, 597, 135397, 420818, 24428, 168259, 99861, 284054, 12445, 181808, 330457, 351286, 109445, 321612, 260513]
    
    print("Fetching specific movies...")
    movies_data = fetch_specific_movies(movie_ids)
    
    save_raw_data(movies_data)
