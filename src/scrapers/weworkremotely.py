import time
import requests

from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from src.logger import logger


BASE_URL = (
    "https://weworkremotely.com/remote-jobs/search"
)

BASE_DOMAIN = (
    "https://weworkremotely.com"
)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,"
        "image/webp,*/*;q=0.8"
    ),
    "Accept-Language": (
        "en-US,en;q=0.9"
    ),
    "Accept-Encoding": (
        "gzip, deflate"
    ),
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def build_urls(settings):

    urls = []

    for keyword in settings.keywords:

        query = quote_plus(keyword)

        urls.append(
            f"{BASE_URL}?term={query}"
        )

    return urls


def extract_date(soup):

    # --------------------------------------------------
    # Method 1: <time datetime="...">
    # --------------------------------------------------

    time_element = soup.select_one(
        "time[datetime]"
    )

    if time_element:

        date_value = (
            time_element.get("datetime", "")
            .strip()
        )

        if date_value:
            return date_value[:10]

    # --------------------------------------------------
    # Method 2: meta article:published_time
    # --------------------------------------------------

    meta = soup.select_one(
        'meta[property="article:published_time"]'
    )

    if meta:

        date_value = (
            meta.get("content", "")
            .strip()
        )

        if date_value:
            return date_value[:10]

    # --------------------------------------------------
    # Method 3: meta date
    # --------------------------------------------------

    meta = soup.select_one(
        'meta[name="date"]'
    )

    if meta:

        date_value = (
            meta.get("content", "")
            .strip()
        )

        if date_value:
            return date_value[:10]

    # --------------------------------------------------
    # Method 4: JSON-LD
    # --------------------------------------------------

    scripts = soup.select(
        'script[type="application/ld+json"]'
    )

    for script in scripts:

        try:

            import json

            data = json.loads(
                script.string or script.get_text()
            )

            if isinstance(data, dict):

                date_value = (
                    data.get(
                        "datePosted",
                        ""
                    )
                )

                if date_value:
                    return str(
                        date_value
                    )[:10]

            elif isinstance(data, list):

                for item in data:

                    if not isinstance(
                        item,
                        dict
                    ):
                        continue

                    date_value = (
                        item.get(
                            "datePosted",
                            ""
                        )
                    )

                    if date_value:
                        return str(
                            date_value
                        )[:10]

        except Exception:

            continue

    return ""


def extract_job_details(
    session,
    job_url
):

    try:

        logger.info(
            f"WWR Job Detail: {job_url}"
        )

        response = session.get(
            job_url,
            timeout=15
        )

        if response.status_code == 403:

            logger.error(
                f"WWR Job Detail returned "
                f"403: {job_url}"
            )

            return {
                "title": "",
                "company": "",
                "date": ""
            }

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # --------------------------------------------------
        # Job Title
        # --------------------------------------------------

        title_element = soup.select_one(
            ".lis-container__header__hero__company-info__title"
        )

        title = ""

        if title_element:

            title = title_element.get_text(
                " ",
                strip=True
            )

        # --------------------------------------------------
        # Company
        # --------------------------------------------------

        company_element = soup.select_one(
            ".lis-container__job__sidebar__companyDetails__info__title"
        )

        company = ""

        if company_element:

            company = company_element.get_text(
                " ",
                strip=True
            )

        # --------------------------------------------------
        # Date
        # --------------------------------------------------

        date = extract_date(soup)

        return {
            "title": title,
            "company": company,
            "date": date
        }

    except requests.exceptions.Timeout:

        logger.exception(
            f"Timeout while reading "
            f"WWR job detail: {job_url}"
        )

    except requests.exceptions.RequestException:

        logger.exception(
            f"Request error while reading "
            f"WWR job detail: {job_url}"
        )

    except Exception:

        logger.exception(
            f"Unexpected error while reading "
            f"WWR job detail: {job_url}"
        )

    return {
        "title": "",
        "company": "",
        "date": ""
    }


def scrape(settings):

    logger.info(
        "Searching We Work Remotely..."
    )

    jobs = []

    urls = build_urls(settings)

    session = requests.Session()

    session.headers.update(
        HEADERS
    )

    try:

        # ==================================================
        # Search pages
        # ==================================================

        for url in urls:

            try:

                logger.info(
                    f"WWR URL: {url}"
                )

                response = session.get(
                    url,
                    timeout=15
                )

                if response.status_code == 403:

                    logger.error(
                        "We Work Remotely returned "
                        "HTTP 403 Forbidden. "
                        "Skipping this search page."
                    )

                    continue

                response.raise_for_status()

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                job_links = soup.select(
                    "section.jobs "
                    "article "
                    "ul "
                    "li:not(.view-all) "
                    "a"
                )

                logger.info(
                    f"WWR jobs found on page: "
                    f"{len(job_links)}"
                )

                # --------------------------------------------------
                # Extract unique URLs from search page
                # --------------------------------------------------

                page_urls = set()

                for link in job_links:

                    href = (
                        link.get(
                            "href",
                            ""
                        )
                        .strip()
                    )

                    if not href:
                        continue

                    if not href.startswith(
                        "/remote-jobs/"
                    ):
                        continue

                    job_url = (
                        BASE_DOMAIN
                        + href
                    )

                    page_urls.add(
                        job_url
                    )

                # ==================================================
                # Open individual job pages
                # ==================================================

                for job_url in page_urls:

                    details = extract_job_details(
                        session,
                        job_url
                    )

                    jobs.append(
                        {
                            "title": details[
                                "title"
                            ],

                            "company": details[
                                "company"
                            ],

                            "location": "Remote",

                            "remote": True,

                            "url": job_url,

                            "date": details[
                                "date"
                            ],

                            "source": (
                                "We Work Remotely"
                            ),
                        }
                    )

                    # --------------------------------------------------
                    # Small delay between job pages
                    # --------------------------------------------------

                    time.sleep(0.5)

            except requests.exceptions.Timeout:

                logger.exception(
                    f"Timeout while requesting "
                    f"WWR search URL: {url}"
                )

            except requests.exceptions.RequestException:

                logger.exception(
                    f"Request error for "
                    f"WWR search URL: {url}"
                )

            except Exception:

                logger.exception(
                    f"Unexpected error while "
                    f"processing WWR URL: {url}"
                )

            time.sleep(1)

    finally:

        session.close()

    # ==================================================
    # Remove duplicate jobs
    # ==================================================

    unique_jobs = []

    seen_urls = set()

    for job in jobs:

        url = job.get(
            "url",
            ""
        )

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        unique_jobs.append(
            job
        )

    logger.info(
        f"We Work Remotely -> "
        f"{len(unique_jobs)} jobs found."
    )

    return unique_jobs