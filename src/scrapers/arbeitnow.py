import requests

from src.logger import logger


URL = "https://arbeitnow.com/api/job-board-api"


def scrape(settings):

    logger.info("Searching Arbeitnow...")

    jobs = []

    try:

        response = requests.get(URL, timeout=20)

        response.raise_for_status()

        data = response.json()

        for job in data.get("data", []):

            title = job.get("title", "")

            text = title.lower()

            # Filter jobs based on user keywords

            if settings.keywords:

                if not any(
                    keyword.lower() in text
                    for keyword in settings.keywords
                ):
                    continue

            jobs.append({

                "title": title,

                "company": job.get("company_name", ""),

                "location": job.get("location", ""),

                "remote": job.get("remote", False),

                "url": job.get("url", ""),

                "date": job.get("created_at", ""),

                "source": "Arbeitnow"

            })

    except Exception as e:

        logger.error(f"Arbeitnow Error: {e}")

    logger.info(f"Arbeitnow -> {len(jobs)} jobs found.")

    return jobs