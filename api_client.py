import requests
import os
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urlparse

load_dotenv()
API_KEY = os.getenv("SCRAPERAPI_KEY")
API_ENDPOINT = "http://api.scraperapi.com"

def fetch_serp_results(keyword: str, retries=3, delay=5) -> list | None:
    """
    Fetches SERP data using ScraperAPI with a more robust parsing logic.
    """
    if not API_KEY or API_KEY == "YOUR_KEY_HERE":
        print("Error: ScraperAPI key not found or not set. Please check your .env file.")
        return None

    google_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}&gl=us&hl=en"
    params = {'api_key': API_KEY, 'url': google_url}

    for attempt in range(retries):
        try:
            print(f"Fetching SERP data for: '{keyword}' via ScraperAPI (Attempt {attempt + 1}/{retries})...")
            response = requests.get(API_ENDPOINT, params=params, timeout=60)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            results = []
            
            # --- NEW, MORE ROBUST PARSING LOGIC ---
            # This looks for containers that are more likely to be search results
            # by checking for the presence of an h3 tag (the title).
            for container in soup.find_all('div', class_=lambda x: x is not None):
                title_element = container.find('h3')
                link_element = container.find('a')

                if title_element and link_element and link_element.get('href'):
                    link = link_element['href']
                    
                    # Ensure it's a valid, absolute URL and not an internal Google link
                    if link.startswith('http') and 'google.com' not in urlparse(link).netloc:
                        # Avoid duplicate entries
                        if not any(r['link'] == link for r in results):
                            results.append({
                                'position': len(results) + 1,
                                'title': title_element.text,
                                'link': link,
                                'domain': urlparse(link).netloc
                            })
            
            if not results:
                print(f"Warning: Could not parse any results for '{keyword}'. Google's HTML structure may have changed.")
                # Optional: Save the HTML for debugging
                # with open(f"debug_{keyword}.html", "w", encoding="utf-8") as f:
                #     f.write(soup.prettify())
                return None
            
            print(f"Successfully fetched and parsed {len(results)} results for '{keyword}'.")
            return results[:10] # Return top 10 results

        except requests.exceptions.RequestException as e:
            print(f"Network error for '{keyword}': {e}. Retrying in {delay} seconds...")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(f"Failed to fetch data for '{keyword}' after {retries} attempts.")
                return None
    return None
