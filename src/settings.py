import json
from pathlib import Path


class Settings:

    def __init__(self, settings_file):
        self.settings_file = Path(settings_file)
        self._data = None

    def load(self):
        if self._data is None:
            with open(
                self.settings_file,
                encoding="utf-8"
            ) as file:
                self._data = json.load(file)

        return self._data

    @property
    def search(self):
        return self.load()["search"]

    @property
    def keywords(self):
        return self.search["keywords"]

    @property
    def remote(self):
        return self.search["remote"]

    @property
    def sources(self):
        return self.search["sources"]

    @property
    def max_results(self):
        return self.search["max_results"]

    @property
    def min_score(self):
        return self.search["min_score"]