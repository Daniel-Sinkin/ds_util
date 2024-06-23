import datetime as dt
import os
import time
from typing import Optional

import ujson as json


class TimeTracker:
    def __init__(self) -> None:
        self.local_folderpath = "./time_tracker/data.json"

        with open(self.local_folderpath, "r") as f:
            self.data = json.load(f)

        self.tags = self.data.get("tags", [])
        self.entries = self.data.get("entries", {})

        self.current_entry = None

        self.is_running = False

    def create_new_entry(self, tags: list[str]) -> None:
        if any(tag not in self.tags for tag in tags):
            raise ValueError(f"Tags {tags} not found in {self.tags}")

        timestamp_start = int(time.time() * 1000)
        current_entry = timestamp_start
        self.entries[current_entry] = {"tags": tags, "iterations": []}

    def start_entry(self, key: int) -> None:
        t_curr = int(time.time() * 1000)

        self.entries[key]["iterations"].append({"start": t_curr})
        self.current_entry = key

    def stop_entry(self, key: Optional[int]) -> None:
        if key is None:
            key = self.current_entry
        else:
            raise RuntimeError("No entry is currently running and no key was passed.")

        t_curr = int(time.time() * 1000)

        self.entries[key]["iterations"][-1]["stop"] = t_curr
        self.current_entry = None

    def get_latest_entry(self) -> int:
        return max(self.entries.keys())

    def update(self) -> None:
        with open(self.local_folderpath, "w") as f:
            json.dump(self.data, f)

    def run(self) -> None:
        self.is_running = True

        print("Starting to run the timetracking utility.")
        while self.is_running:
            inp = input(
                "Add comments or stop with -s or quit with -q or list all entries with -ls.\nAdd a new entry with `-n '[*tags]'.\n"
            )

            if inp == "-s":
                pass
            elif inp == "-q":
                self.is_running = False
            elif inp == "-ls":
                print(self.entries)
            else:
                raise NotImplementedError("Comments not supported yet.")

            print()

            self.update()

        print("Quitting the timetracking utility.")
        self.update()

    def get_obsidian_folderpath() -> str:
        time_tracking_dir: Optional[str] = os.getenv("DS_TIME_TRACKING_DIR")

        if time_tracking_dir is None:
            raise ValueError("DS_TIME_TRACKING_DIR environment variable must be set")
        return time_tracking_dir


def main() -> None:
    time_tracker = TimeTracker()
    time_tracker.run()


if __name__ == "__main__":
    main()
