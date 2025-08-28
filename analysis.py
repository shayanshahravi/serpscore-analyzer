# A predefined list of high-authority domains.
HIGH_AUTHORITY_DOMAINS = [
    'wikipedia.org',
    'youtube.com',
    'forbes.com',
    'amazon.com',
    'bbc.com',
    'nytimes.com',
    'theguardian.com',
    'bikeradar.com', # Added from our test keywords
    'electrek.co'    # Added from our test keywords
]

def analyze_serp(serp_results: list, competitors: list, keyword: str) -> dict:
    """
    Analyzes SERP results to calculate a competition score and find competitors.
    """
    competition_score = 100
    found_competitors = {}

    for result in serp_results:
        rank = result.get('position', 11)
        title = result.get('title', '').lower()
        domain = result.get('domain', '').lower()

        # 1. Penalize for exact keyword match in title
        if keyword.lower() in title:
            competition_score -= 5

        # 2. Penalize heavily for high-authority domains ranking
        for auth_domain in HIGH_AUTHORITY_DOMAINS:
            if auth_domain in domain:
                competition_score -= 10
                break

        # 3. Competitor Tracking
        for competitor_url in competitors:
            if competitor_url.lower() in domain:
                found_competitors[competitor_url] = rank
    
    final_score = max(0, competition_score)

    return {
        "competition_score": final_score,
        "found_competitors": found_competitors
    }
