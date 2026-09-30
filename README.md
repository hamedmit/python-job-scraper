# python-job-scraper

A lightweight Python tool for collecting and ranking remote job opportunities from multiple job sources.

The project keeps the workflow simple: collect jobs, filter and rank them based on configurable keywords, remove duplicates, and export the results to CSV.

<div dir="rtl">
برای راهنمای فارسی فایل 'README_FA' را ببینید.
</div>

## Why this project?

Finding a suitable remote job often means checking several websites, dealing with a large number of listings, and filtering out jobs that are not relevant.

I started this project to make that process simpler: collect jobs from different sources, apply personal search preferences, remove duplicates, and keep the most relevant results in one place.

## Features

* Collect jobs from multiple job sources
* Support remote-only job searches
* Filter and rank jobs based on configurable keywords
* Remove duplicate job listings
* Skip previously collected jobs
* Save daily results as CSV files
* Keep a history of scraper runs
* Save application logs
* Run locally or with Docker

## Job Sources

The current version collects jobs from:

* [Arbeitnow](https://www.arbeitnow.com/)
* [Remote OK](https://remoteok.com/)
* [Remotive](https://remotive.com/)
* [Wellfound](https://wellfound.com/)
* [We Work Remotely](https://weworkremotely.com/)

Additional job sources are planned for future versions.

## Configuration

You can customize the search settings in:

```text
config/settings.json
```

For example:

```json
{
    "search": {
        "keywords": [
            "AI Engineer",
            "Python"
        ],
        "remote": true,
        "sources": [
            "remotive"
        ],
        "max_results": 30,
        "min_score": 20
    }
}
```

### Configuration Options

* `keywords` — Keywords used to find and rank relevant jobs.
* `remote` — Set to `true` to search for remote jobs only. Set it to `false` to include both remote and on-site jobs. When enabled, sources that do not provide remote listings may return no results.
* `sources` — Job sources to search.
* `max_results` — Maximum number of results requested from supported job sources.
* `min_score` — Minimum score used to identify jobs that meet the configured relevance threshold.

You can change these values according to your own job search needs.

## Built With

- Python
- Requests
- BeautifulSoup
- Docker
- Docker Compose

## Project Structure

```text
python-job-scraper/
├── main.py
├── config/
│   └── settings.json
├── src/
│   ├── scrapers/
│   ├── settings.py
│   ├── ranker.py
│   ├── exporter.py
│   ├── history.py
│   └── logger.py
├── output/
│   ├── jobs.csv
│   ├── history.csv
│   ├── logs/
│   └── daily/
├── Dockerfile
├── compose.yaml
├── run_docker.sh
└── requirements.txt
```

## Run Locally

Make sure Python 3.10+ is installed.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python main.py
```

The results and execution logs are saved in the `output/` directory.

## Run with Docker

Build and run the application with Docker Compose:

```bash
docker compose up --build
```

The `output/` directory is mounted to the container, so generated CSV files and logs remain available on the host machine.

### Linux / macOS

For Linux and macOS, the included helper script runs the container with the current user's UID and GID. This keeps generated files owned by the host user when using a bind mount.

```bash
chmod +x run_docker.sh
./run_docker.sh
```

### Windows

On Windows with Docker Desktop, use:

```powershell
docker compose up --build
```

## Output

The application maintains:

* `output/jobs.csv` — all newly collected jobs
* `output/daily/` — jobs collected for each day
* `output/history.csv` — execution history and basic run statistics
* `output/logs/` — application execution logs

CSV files can be opened directly in spreadsheet applications.

## Part of a Larger Project

`python-job-scraper` is the first version of a larger job-search project.

The second version is a Telegram bot that allows users to manage their search settings directly through Telegram and receive job results in the same place. It also searches a wider range of job sources.

The third version will add a local AI component for evaluating collected jobs against a user's resume. This version is currently under development and will be released soon.

More information about the upcoming versions will be shared through the Telegram contact and email below.

**Telegram:** @hamedmit

**Email:** hamedmit.gh@gmail.com

## License

This project is open source and released under the MIT License.

You are free to use, modify, and build on the code for your own projects. Contributions and improvements are also welcome.

For the full license terms, see the LICENSE file.
