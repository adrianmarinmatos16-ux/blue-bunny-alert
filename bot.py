import os
import json
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = "8283345025"

JOBS_URL = "https://www.indeed.com/cmp/Wells-Enterprises%2C-Inc.-1/locations/IA/Le%20Mars"

SEEN_FILE = "seen_jobs.json"

KEYWORDS = [
    "production",
    "operator",
    "machine operator",
    "manufacturing",
    "packaging",
    "operations",
    "freezer operator",
    "production worker"
]


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=30
    )

    response.raise_for_status()


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r", encoding="utf-8") as file:
        return set(json.load(file))


def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as file:
        json.dump(list(seen), file, indent=2)


def get_jobs():
    response = requests.get(
        JOBS_URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []

    for link in soup.find_all("a", href=True):

        title = link.get_text(" ", strip=True)

        if not title:
            continue

        title_lower = title.lower()

        if any(keyword in title_lower for keyword in KEYWORDS):

            href = link["href"]

            if href.startswith("/"):
                href = "https://www.indeed.com" + href

            jobs.append({
                "title": title,
                "url": href
            })

    return jobs


def main():

    seen = load_seen()
    jobs = get_jobs()

    new_jobs = []

    for job in jobs:

        job_id = job["title"] + "|" + job["url"]

        if job_id not in seen:

            seen.add(job_id)
            new_jobs.append(job)

    save_seen(seen)

    if not new_jobs:
        print("No hay ofertas nuevas.")
        return

    for job in new_jobs:

        message = (
            "🚨 NUEVA OFERTA DE WELLS / BLUE BUNNY\n\n"
            f"🏭 {job['title']}\n"
            "📍 Le Mars, Iowa\n\n"
            f"🔗 {job['url']}"
        )

        send_message(message)


if __name__ == "__main__":
    main()
