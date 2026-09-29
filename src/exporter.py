import csv
from datetime import datetime


def get_existing_urls(csv_file):

    existing_urls = set()

    if csv_file.exists():

        with open(
            csv_file,
            "r",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                existing_urls.add(
                    row["URL"]
                )

    return existing_urls


def write_header(writer):

    writer.writerow([
        "Score",
        "Title",
        "Company",
        "Location",
        "Remote",
        "Date",
        "Source",
        "URL"
    ])


def export_csv(jobs, paths):

    csv_file = paths["jobs"]

    daily_dir = paths["daily"]

    today = datetime.now().strftime("%Y-%m-%d")

    daily_file = (
        daily_dir /
        f"jobs_{today}.csv"
    )

    existing_urls = get_existing_urls(csv_file)

    main_exists = (
        csv_file.exists()
        and csv_file.stat().st_size > 0
    )

    daily_exists = (
        daily_file.exists()
        and daily_file.stat().st_size > 0
    )

    new_jobs = []
    existing_jobs_skipped = 0

    for job in jobs:

        if job["url"] not in existing_urls:

            new_jobs.append(job)

            existing_urls.add(job["url"])

        else:

            existing_jobs_skipped += 1

    if not new_jobs:

        return 0, existing_jobs_skipped, daily_file

    with open(
        csv_file,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not main_exists:

            write_header(writer)

        for job in new_jobs:

            writer.writerow([
                job.get("score", 0),
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("remote", ""),
                job.get("date", ""),
                job.get("source", ""),
                job.get("url", "")
            ])

    with open(
        daily_file,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not daily_exists:

            write_header(writer)

        for job in new_jobs:

            writer.writerow([
                job.get("score", 0),
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                job.get("remote", ""),
                job.get("date", ""),
                job.get("source", ""),
                job.get("url", "")
            ])

    return len(new_jobs), existing_jobs_skipped, daily_file