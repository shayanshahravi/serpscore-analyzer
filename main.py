import csv
import json
from datetime import datetime

from .api_client import fetch_serp_results
from .analysis import analyze_serp

KEYWORDS_FILE = 'keywords.txt'
COMPETITORS_FILE = 'competitors.txt'

def read_file_lines(file_path: str) -> list[str]:
    """Reads a file and returns its lines, enforcing UTF-8 encoding."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return []

def write_report_to_csv(report_data: list, file_path: str):
    """Writes the report to a CSV file."""
    headers = ['Keyword', 'Competition Score (0-100)', 'Found Competitors (Rank)']
    try:
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            csv_data = []
            for item in report_data:
                competitors_str = ", ".join([f"{url} (Rank {rank})" for url, rank in item['found_competitors'].items()]) or "None"
                csv_data.append({
                    'Keyword': item['keyword'],
                    'Competition Score (0-100)': item['competition_score'],
                    'Found Competitors (Rank)': competitors_str
                })
            writer.writerows(csv_data)
        print(f"CSV report saved to '{file_path}'")
    except IOError as e:
        print(f"Error writing CSV report: {e}")

def write_report_to_json(report_data: list, file_path: str):
    """Writes the report to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=4)
        print(f"JSON report saved to '{file_path}'")
    except IOError as e:
        print(f"Error writing JSON report: {e}")

def main():
    """Main function to run the analyzer."""
    print("--- SERP Score Analyzer (Professional Version) ---")
    
    keywords = read_file_lines(KEYWORDS_FILE)
    competitors = read_file_lines(COMPETITORS_FILE)

    if not keywords:
        print("No keywords found in 'keywords.txt'.")
        return

    all_results = []
    for keyword in keywords:
        serp_data = fetch_serp_results(keyword)
        
        if serp_data:
            analysis = analyze_serp(serp_data, competitors, keyword)
            all_results.append({
                'keyword': keyword,
                'competition_score': analysis['competition_score'],
                'found_competitors': analysis['found_competitors']
            })
        else:
            all_results.append({
                'keyword': keyword,
                'competition_score': 'Error',
                'found_competitors': {}
            })
    
    if all_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        write_report_to_csv(all_results, f"report_{timestamp}.csv")
        write_report_to_json(all_results, f"report_{timestamp}.json")
    else:
        print("No results to generate report.")

if __name__ == "__main__":
    main()
