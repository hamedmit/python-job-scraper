import time
from pathlib import Path

from src.logger import logger
from src.history import save_run

from src.scrapers import remotive
from src.scrapers import arbeitnow
from src.scrapers import remoteok
from src.scrapers import weworkremotely
from src.scrapers import wellfound

from src.ranker import (
    rank_jobs,
    filter_jobs
)

from src.exporter import export_csv

from src.settings import Settings


# =========================================================
# Project Paths
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

OUTPUT_DIR = PROJECT_ROOT / "output"
DAILY_DIR = OUTPUT_DIR / "daily"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DAILY_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PATHS = {
    "root": PROJECT_ROOT,
    "settings": PROJECT_ROOT / "config" / "settings.json",
    "jobs": OUTPUT_DIR / "jobs.csv",
    "daily": DAILY_DIR,
    "history": OUTPUT_DIR / "history.csv",
}


def main():

    # =====================================================
    # Initialize run information
    # =====================================================

    start_time = time.time()

    run_status = "SUCCESS"

    # -----------------------------------------------------
    # Initialize variables used later
    # -----------------------------------------------------

    jobs = []
    jobs_found = []
    good_jobs = []
    jobs_count = 0

    # =====================================================
    # Initialize Settings
    # =====================================================

    try:

        settings = Settings(
            PATHS["settings"]
        )

        logger.info(
            f"Project root: {PROJECT_ROOT}"
        )

        logger.info(
            f"Settings path: {PATHS['settings']}"
        )

        logger.info(
            "Settings loaded successfully."
        )

    except Exception:

        logger.exception(
            "Failed to initialize settings."
        )

        return

    # =====================================================
    # Main Application
    # =====================================================

    try:

        # =================================================
        # Scraper Configuration
        # =================================================

        SCRAPERS = {

            "remotive": remotive.scrape,

            "arbeitnow": arbeitnow.scrape,


            "remoteok": remoteok.scrape,

            "weworkremotely": weworkremotely.scrape,


            "wellfound": wellfound.scrape


        }

        # -------------------------------------------------
        # Sources that provide Remote jobs only
        # -------------------------------------------------

        REMOTE_ONLY_SOURCES = {

            "remotive",

            "remoteok",

            "weworkremotely",

        }

        # =================================================
        # Startup Logging
        # =================================================

        logger.info(
            "=" * 60
        )

        logger.info(
            "JobScraper started."
        )

        logger.info(
            f"Keywords    : {settings.keywords}"
        )

        logger.info(
            f"Remote      : {settings.remote}"
        )

        logger.info(
            f"Sources     : {settings.sources}"
        )

        logger.info(
            f"Max Results : {settings.max_results}"
        )

        logger.info(
            f"Min Score   : {settings.min_score}"
        )

        # =================================================
        # Main Scraping Logic
        # =================================================

        jobs = []

        # -------------------------------------------------
        # Run Selected Scrapers
        # -------------------------------------------------

        for source in settings.sources:

            # ---------------------------------------------
            # User wants ALL jobs
            #
            # Therefore skip sources that only provide
            # Remote jobs.
            # ---------------------------------------------

            if not settings.remote:

                if source in REMOTE_ONLY_SOURCES:

                    logger.info(
                        f"Skipping remote-only source: {source}"
                    )

                    continue

            # ---------------------------------------------
            # Get scraper
            # ---------------------------------------------

            scraper = SCRAPERS.get(
                source
            )

            if not scraper:

                logger.warning(
                    f"No scraper registered for source: {source}"
                )

                continue

            # ---------------------------------------------
            # Run scraper independently
            #
            # If one scraper fails, other scrapers
            # continue running.
            # ---------------------------------------------

            try:

                logger.info(
                    f"Running scraper: {source}"
                )

                scraped_jobs = scraper(
                    settings
                )

                if scraped_jobs:

                    jobs.extend(
                        scraped_jobs
                    )

                    logger.info(
                        f"{source}: "
                        f"{len(scraped_jobs)} jobs added."
                    )

                else:

                    logger.info(
                        f"{source}: "
                        f"No jobs returned."
                    )

            except Exception:

                logger.exception(
                    f"Scraper failed: {source}"
                )

                # -----------------------------------------
                # Continue with next scraper
                # -----------------------------------------

                continue

        # =================================================
        # Filter Jobs
        # =================================================

        try:

            jobs = filter_jobs(
                jobs,
                settings
            )

        except Exception:

            logger.exception(
                "Failed while filtering jobs."
            )

            raise

        # =================================================
        # Rank Jobs
        # =================================================

        try:

            jobs_found = rank_jobs(
                jobs,
                settings
            )

        except Exception:

            logger.exception(
                "Failed while ranking jobs."
            )

            raise

        # =================================================
        # Minimum Score Filter
        # =================================================

        good_jobs = [

            job

            for job in jobs_found

            if job["score"] >= settings.min_score

        ]

        # =================================================
        # Export CSV
        # =================================================

        new_jobs = 0
        existing_jobs_skipped = 0
        daily_file = None

        try:

            new_jobs, existing_jobs_skipped, daily_file = export_csv(
                jobs_found,
                PATHS
            )

        except Exception:

            logger.exception(
                "Failed to write CSV file."
            )

        # =================================================
        # Statistics
        # =================================================

        duplicates_removed = (
            len(jobs) - len(jobs_found)
        )

        logger.info(
            f"Jobs found              : {len(jobs)}"
        )

        logger.info(
            f"Duplicates removed      : {duplicates_removed}"
        )

        logger.info(
            f"Unique Jobs             : {len(jobs_found)}"
        )

        logger.info(
            f"Existing jobs skipped   : {existing_jobs_skipped}"
        )

        logger.info(
            f"New jobs saved          : {new_jobs}"
        )

        logger.info(
            f"Jobs meeting minimum score: "
            f"{len(good_jobs)}"
        )

        logger.info(
            "** 5 Top Jobs: **"
        )

        for job in jobs_found[:5]:

            try:

                logger.info(
                    f"[{job['score']:3}] "
                    f"{job['title']} | "
                    f"{job['url']} | "
                    f"{job['company']}"
                )

            except Exception:

                logger.exception(
                    "Failed to log job information."
                )

        jobs_count = len(
            jobs_found
        )


        logger.info(
            "JobScraper completed successfully."
        )

    # =====================================================
    # Main Application Error
    # =====================================================

    except Exception as e:

        run_status = "FAILED"

        logger.exception(
            f"JobScraper failed: {e}"
        )

    # =====================================================
    # Finalization
    # =====================================================

    finally:

        # -------------------------------------------------
        # Calculate Duration
        # -------------------------------------------------

        run_duration = (
            time.time() - start_time
        )

        logger.info(
            f"Run Status : {run_status}"
        )

        logger.info(
            f"Duration   : "
            f"{run_duration:.2f} sec"
        )

        logger.info(
            "=" * 60
        )

        # =================================================
        # Save Run History
        # =================================================

        try:

            save_run(

                status=run_status,

                duration=run_duration,

                jobs=jobs_count,

                sources=", ".join(
                    settings.sources
                ),

                paths=PATHS

            )

        except Exception:

            logger.exception(
                "Failed to save run history."
            )


if __name__ == "__main__":

    main()
