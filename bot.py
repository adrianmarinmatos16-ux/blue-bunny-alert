import os
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = "8283345025"

URL = "https://wellsenterprisesinc.com/careers"

KEYWORDS = [
    "production",
    "operator",
    "manufacturing",
    "packaging",
    "operations"
]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": False
        },
        timeout=30
    )

    response.raise_for_status()


def get_jobs():
    response = requests.get(
        URL,
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
                href = "https://wellsenterprisesinc.com" + href

            jobs.append((title, href))

    return jobs


jobs = get_jobs()

if jobs:
    message = "🚨 POSIBLES EMPLEOS NUEVOS EN WELLS / BLUE BUNNY\n\n"

    for title, link in jobs[:10]:
        message += f"🔹 {title}\n{link}\n\n"

    send_message(message)
else:
    send_message(
        "🔎 Revisé Wells/Blue Bunny y no encontré "
        "puestos de producción visibles en esta revisión."
    )
