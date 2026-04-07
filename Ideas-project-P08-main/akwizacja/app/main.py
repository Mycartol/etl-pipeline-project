import os
import time
import argparse
import requests
from bs4 import BeautifulSoup
import urllib3

# === CONFIG ===
#START_URL = "https://www.bip.gov.pl/subjects/5580,Urz%C4%85d+Miasta+Gdyni.html"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
OUTPUT_DIR = "bip_downloads"
DELAY_BETWEEN_REQUESTS = 1  # in seconds

# === SETUP ===
os.makedirs(OUTPUT_DIR, exist_ok=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# === SCRAPING FUNCTION ===
def build_queue():
    print("🔍 Building queue...")
    response = requests.get(START_URL, headers=HEADERS, verify=False)

    if response.status_code != 200:
        print(f"❌ Failed to fetch the page. Status code: {response.status_code}")
        return []

    print("💡 Page fetched successfully, printing HTML content:")
    print(response.text[:1000])  # Print the first 1000 characters of the page to inspect

    soup = BeautifulSoup(response.text, "html.parser")
    links = [a['href'] for a in soup.find_all('a', href=True)]

    print(f"Found {len(links)} links.")  # Debugging line
    print("💡 Extracted links:")
    print(links[:10])  # Print the first 10 links for inspection

    queue = []
    for link in links:
        full_url = requests.compat.urljoin(START_URL, link)
        queue.append({
            "url": full_url,
            "status": "pending"
        })

    print(f"✅ Queue created with {len(queue)} items.")
    return queue


def process_queue():
    queue = build_queue()
    if not queue:
        print("No items in the queue to process.")
        return

    total = sum(1 for item in queue if item["status"] == "pending")
    print(f"🚀 Processing queue: {total} pending items")

    for item in queue:
        if item["status"] != "pending":
            continue

        item["status"] = "in_progress"

        try:
            print(f"📥 Downloading: {item['url']}")

            try:
                requests.post("http://indeksowanie:5000/api/current-url-update", json={"url": item['url']}, timeout=10)
            except Exception as e:
                print(f"Failed to update current URL: {e}")

            response = requests.get(item["url"], headers=HEADERS, verify=False, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text(separator="\n", strip=True)

                payload = {
                    "url": item["url"],
                    "content": text
                }

                api_response = requests.post('http://indeksowanie:5000/api/documents', json=payload, timeout=10)

                if api_response.status_code == 201:
                    item["status"] = "completed"
                    print("✅ Data sent successfully")
                else:
                    item["status"] = "failed"
                    print(f"❌ Failed to send to API (status {api_response.status_code})")
            else:
                item["status"] = "failed"
                print(f"❌ Failed (status {response.status_code})")

        except Exception as e:
            item["status"] = "failed"
            print(f"⚠️ Error: {e}")

        time.sleep(DELAY_BETWEEN_REQUESTS)


# === MAIN ===
if __name__ == "__main__":
    START_URL = os.environ.get("SCRAP_URL")
    print(f"🔧 SCRAP_URL from env: {START_URL}")
    if not START_URL:
        raise ValueError("❌ Environment variable SCRAP_URL is not set.")

    process_queue()
    print("✅ Queue processing completed.")
    requests.post('http://indeksowanie:5000/api/trigger-next', json={"url": START_URL})
