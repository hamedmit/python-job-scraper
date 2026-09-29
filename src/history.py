import csv
from datetime import datetime


def save_run(
    status: str,
    duration: float,
    jobs: int,
    sources: str,
    paths
):

    report_file = paths["history"]

    file_exists = (
        report_file.exists()
        and report_file.stat().st_size > 0
    )

    with open(
        report_file,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "Time",
                "Status",
                "Duration(sec)",
                "Jobs",
                "Sources"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status,
            round(duration, 2),
            jobs,
            sources
        ])

