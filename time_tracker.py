import argparse
import json
import os
import select
import sys
import termios
import time
import tty
from typing import Optional

SECOND_TO_MS = 1e3
MS_TO_SECOND = 1e-3

PRINT_DELAY = 0.3
SAVE_DELAY = 10.0


class TimeTracker:
    def __init__(self) -> None:
        filename = "data.json"
        self.local_folderpath: str = os.path.join(
            os.environ.get("DS_TIME_TRACKING_DIR", "./time_tracker/"), filename
        )

        if not os.path.exists(self.local_folderpath):
            print(f"Creating {self.local_folderpath}.")
            os.makedirs(os.path.dirname(self.local_folderpath), exist_ok=True)
            with open(self.local_folderpath, "w") as f:
                json.dump({}, f)

        with open(self.local_folderpath, "r") as f:
            self.data = json.load(f)

    def save_data(self) -> None:
        with open(self.local_folderpath, "w") as f:
            json.dump(self.data, f, indent=4)

    def register_new_project(
        self,
        project_name: str,
        tags: Optional[list[str]] = None,
    ) -> None:
        if project_name in self.data:
            print(f"Project {project_name} already exists")
            return

        self.data[project_name] = {
            "tags": tags or [],
            "entries": [],
        }

    def start_tracking(
        self,
        project_name: str,
        comment: Optional[str] = None,
    ) -> None:
        if project_name not in self.data:
            print(f"Registering {project_name=} before tracking.")
            self.register_new_project(project_name)

        self.data[project_name]["entries"].append(
            {
                "start": int(time.time() * SECOND_TO_MS),
                "stop": None,
                "comment": comment or "",
            }
        )

    def stop_tracking(self, project_name: str) -> None:
        if project_name not in self.data:
            print(f"Project {project_name} not found")
            return

        self.data[project_name]["entries"][-1]["stop"] = int(time.time() * SECOND_TO_MS)
        self.save_data()

    def get_total_time_in_project(self, project_name: str) -> float:
        total_time_ms = 0
        for entry in self.data[project_name]["entries"]:
            if entry["stop"] is not None:
                total_time_ms += entry["stop"] - entry["start"]
        return total_time_ms / SECOND_TO_MS

    def __del__(self) -> None:
        print("Starting to save the data.")
        self.save_data()
        print("Data saved.")


def is_data() -> bool:
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def main() -> None:
    parser = argparse.ArgumentParser(description="Time Tracking Application")
    parser.add_argument(
        "-p", "--project", type=str, help="Project name to start tracking"
    )
    parser.add_argument(
        "-c", "--comment", type=str, help="Comment for the tracking entry"
    )
    parser.add_argument("-ls", "--list", action="store_true", help="List all data")

    args = parser.parse_args()

    time_tracker = TimeTracker()

    if args.list:
        with open(time_tracker.local_folderpath, "r") as f:
            print(json.dumps(json.load(f), indent=4))
        return

    project_name = str(args.project if args.project else "NO_NAME")
    comment = str(args.comment if args.comment else "")
    time_tracker.start_tracking(project_name, comment)
    print(f"Started tracking project: {project_name}")

    t0: float = time.time()
    time_until_next_save = t0 + SAVE_DELAY
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while not is_data():
            elapsed_time = time.time() - t0
            print(f"\r{elapsed_time:7.0f} seconds elapsed.", end="")
            sys.stdout.flush()
            time.sleep(PRINT_DELAY)
            if time.time() > time_until_next_save:
                assert False
                time_tracker.save_data()
                time_until_next_save = time.time() + SAVE_DELAY
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    time_tracker.stop_tracking(project_name)
    print("\nTracking stopped.")


if __name__ == "__main__":
    main()
