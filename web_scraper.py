import requests
from bs4 import BeautifulSoup


# 🔹 Step 1: Get HTML from a page
def fetch_page(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to fetch page")
        return None
    
    return response.text


# 🔹 Step 2: Parse HTML and extract titles
def extract_titles(html):
    soup = BeautifulSoup(html, "html.parser")
    
    titles = []
    
    # Example: grab all <h2> tags (common for titles)
    for tag in soup.find_all("h2"):
        text = tag.get_text().strip()
        
        if text:
            titles.append(text)
    
    return titles


# 🔹 Step 3: Save to file
def save_to_file(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for item in data:
            f.write(item + "\n")


# 🔹 Step 4: Scrape one page
def scrape_single(url):
    html = fetch_page(url)
    
    if html is None:
        return []
    
    titles = extract_titles(html)
    
    print("\n--- Titles ---")
    for t in titles:
        print(t)
    
    return titles


# 🔹 Step 5: Scrape multiple pages
def scrape_multiple(base_url, pages):
    all_titles = []
    
    for page in range(1, pages + 1):
        url = base_url.format(page)
        print(f"\nScraping page {page}: {url}")
        
        titles = scrape_single(url)
        all_titles.extend(titles)
    
    return all_titles


# ---- RUN ----

# Example 1: Single page
url = "https://example.com"   # replace with real site
titles = scrape_single(url)

# Save results
save_to_file(titles, "titles.txt")


# Example 2: Multiple pages (if site supports pagination)
# Example format: https://site.com/page/1, /2, /3...
base_url = "https://example.com/page/{}"
all_titles = scrape_multiple(base_url, 3)

save_to_file(all_titles, "all_titles.txt")