import time
import requests

from src.logger import logger
from urllib.parse import quote_plus
#from src.config.config import config

USER_AGENT = {
    "User-Agent": "Mozilla/5.0"
}
#new:
def build_urls(settings):

    urls = []

    for keyword in settings.keywords:

        query = quote_plus(keyword)

        urls.append(
            f"https://remoteok.com/api?tag={query}"
        )

    return urls

def scrape(settings):
    logger.info("Searching RemoteOK...")

    jobs = []
#new:
    urls = build_urls(settings)    
    #urls = build_urls()
    for url in urls:
        try:
            logger.info(f"Links: {url}")
            response = requests.get(
                url,
                headers=USER_AGENT,
                timeout=15
            )

            response.raise_for_status()
            
            # The first item in the RemoteOK API response contains metadata.
            
            data = response.json()
            
            # Job listings start from index 1.
            if isinstance(data, list):
                job_list = data[1:] 
            else:
                job_list = []

            for job in job_list:
                jobs.append(
                    {
                        "title": job.get("position", ""),
                        "company": job.get("company", ""),
                        "location": job.get("location", "Remote"),
                        "remote": True,
                        "url": job.get("url", ""),
                        "date": (job.get("date") or "")[:10],
                        "source": "RemoteOK",
                    }
                )

        except Exception as e:
            logger.error(f"RemoteOK Error: {e}")

        time.sleep(1)

    logger.info(f"RemoteOK -> {len(jobs)} jobs found.")

    return jobs
