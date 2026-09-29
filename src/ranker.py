from datetime import datetime
from src.logger import logger
import re


def calculate_score(job: dict, settings) -> int:
    """
    Calculate a simple relevance score for a job.
    """

    score = 0

    text = (
        f"{job.get('title', '')} "
        f"{job.get('company', '')} "
        f"{job.get('location', '')} "
        f"{job.get('description', '')}"
    ).lower()

    # -------------------------
    # Positive keywords
    # -------------------------

    for keyword in settings.keywords:

        if keyword.lower() in text:
            score += 20

    # -------------------------
    # Remote jobs
    # -------------------------
    if settings.remote:
        if job.get("remote"):
            score += 10

    score += calculate_date_bonus(
        job.get("date")
    )
    return min(score, 100)

def remove_duplicates(jobs: list) -> list:
    """
    Remove duplicate jobs based on URL.
    """

    unique_jobs = []
    seen_urls = set()

    for job in jobs:

        url = job.get("url", "").strip()

        if not url:
            logger.warning("Skipping job without URL.")
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)
        unique_jobs.append(job)

    return unique_jobs

def rank_jobs(jobs: list, settings) -> list:
    jobs = remove_duplicates(jobs)
    for job in jobs:
        job["score"] = calculate_score(job, settings)

    jobs.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return jobs

def filter_jobs(jobs, settings):

    if not settings.remote:

        return jobs

    return [

        job

        for job in jobs

        if job.get("remote", False)

    ]

def calculate_date_bonus(date_text):

    if not date_text:
        return 0

    date_text = (
        str(date_text)
        .lower()
        .replace("reposted:", "")
        .replace("posted", "")
        .strip()
    )
    try:

        if "day" in date_text:

            days = int(re.search(r"\d+", date_text).group())

            if days <= 30:
                return 10

            if days <= 90:
                return 5

            return 0

        if "month" in date_text:

            months = int(re.search(r"\d+", date_text).group())

            if months <= 3:
                return 5

            if months <= 12:
                return 0

            return -10

        if "year" in date_text:

            years = int(re.search(r"\d+", date_text).group())

            return -20 * years

        # YYYY-MM-DD

        try:

            job_date = datetime.strptime(
                date_text[:10],
                "%Y-%m-%d"
            )

            age_days = (
                datetime.utcnow() - job_date
            ).days

            if age_days <= 30:
                return 10

            if age_days <= 90:
                return 5

            if age_days <= 365:
                return 0

            return -20

        except:
            pass

    except:
        pass

    return 0