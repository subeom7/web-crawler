import os
import re
import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin
import zipfile

# Set seed URLs and keywords
seed_urls = [
    "https://www.axios.com/2023/01/22/monterey-park-mass-shooting-california",
    "https://abc7ny.com/harris-to-visit-monterey-park-to-meet-with-victims-families/12734896/",
    "https://www.kcra.com/article/video-gov-newsom-speaks-out-after-half-moon-bay-monterey-park-shootings-says-it-doesnt-have-to-be-this-way/42645164",
    "https://www.pasadenastarnews.com/2023/01/24/retired-san-gabriel-cop-injured-in-monterey-park-mass-shooting-called-one-of-the-best/",
    "https://www.yahoo.com/now/ex-wife-monterey-park-mass-170329250.html",
]
keywords = ["Monterey Park", "mass shooting", "Los Angeles", "California", "January 22, 2023"]

# Function to filter relevant links
def is_relevant(url, text):
    text = text.lower()
    keyword_count = sum([1 for kw in keywords if kw.lower() in text])
    return keyword_count > 0

# Function to score a URL based on keyword matches
def score_url(text):
    text = text.lower()
    keyword_count = sum([1 for kw in keywords if kw.lower() in text])
    return keyword_count / len(keywords)

# Web crawling loop
visited = set()
queue = deque([(url, 1) for url in seed_urls])
output_folder = "collected_webpages"

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

count = 1
while queue and count <= 100:
    url, _ = queue.popleft()

    if url in visited:
        continue

    try:
        response = requests.get(url)
    except requests.RequestException as e:
        print(f"Error downloading {url}: {e}")
        continue

    visited.add(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a")

        for link in links:
            href = link.get("href")
            if href and not href.startswith("javascript:") and not href.startswith("#"):
                absolute_url = urljoin(url, href)
                if absolute_url not in visited:
                    if is_relevant(absolute_url, link.text):
                        queue.append((absolute_url, score_url(link.text)))

        file_path = os.path.join(output_folder, f"Monterey_{count:03}.html")
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)

        print(f"Downloaded {url} as {file_path}")

        count += 1

# Save the list of visited URLs
with open("url_lists.txt", "w", encoding="utf-8") as file:
    for url in visited:
        file.write(url + "\n")

print("Web crawling complete.")

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), path))

with zipfile.ZipFile('webpages.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir('collected_webpages', zipf)
    zipf.write('url_lists.txt')

