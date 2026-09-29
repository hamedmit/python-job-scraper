import time
import requests

from bs4 import BeautifulSoup

from src.logger import logger


USER_AGENT = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/125.0.0.0 "
        "Safari/537.36"
    )
}


ROLE_MAPPING = {
    "machine learning": "machine-learning-engineer",
    "deep learning": "machine-learning-engineer",
    "ai": "artificial-intelligence-engineer",
    "artificial intelligence": "artificial-intelligence-engineer",
    "llm": "artificial-intelligence-engineer",
    "data scientist": "data-scientist",
}


def build_urls(settings):

    urls = []

    added = set()

    for keyword in settings.keywords:

        keyword_lower = keyword.lower()

        role_slug = None

        for key, value in ROLE_MAPPING.items():

            if key in keyword_lower:

                role_slug = value
                break

        if not role_slug:
            continue

        if role_slug in added:
            continue

        added.add(role_slug)

        if settings.remote:

            urls.append(
                f"https://wellfound.com/role/r/{role_slug}"
            )

        else:
            urls.append(
                f"https://wellfound.com/role/r/{role_slug}"
            )
            urls.append(
                f"https://wellfound.com/role/{role_slug}"
            )
        

    return urls


def scrape(settings):

    logger.info("Searching Wellfound...")

    jobs = []

    urls = build_urls(settings)

    logger.info(f"Wellfound URLs: {urls}")

    if not urls:

        logger.info(
            "Wellfound: No matching role for keywords."
        )
        return jobs

    for url in urls:
        is_remote = "/role/r/" in url
        try:

            logger.info(f"Wellfound URL: {url}")

            response = requests.get(
                url,
                headers=USER_AGENT,
                timeout=20
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            page_jobs = 0

            links = soup.find_all("a", href=True)

            for link in links:

                href = link["href"]

                if "/jobs/" not in href:
                    continue

                title = link.get_text(
                    strip=True
                )

                if not title:
                    continue

                if href.startswith("/"):

                    href = (
                        "https://wellfound.com"
                        + href
                    )

                jobs.append(
                    {
                        "title": title,
                        "company": "",
                        "location": "Remote" if is_remote else "On-site",
                        "remote": is_remote,
                        "url": href,
                        "date": "",
                        "source": "Wellfound",
                    }
                )

                page_jobs += 1

            logger.info(
                f"Wellfound jobs found on page: "
                f"{page_jobs}"
            )

        except Exception as e:

            logger.error(
                f"Wellfound Error: {e}"
            )

        time.sleep(1)

    logger.info(
        f"Wellfound -> {len(jobs)} jobs found."
    )

    return jobs