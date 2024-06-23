import argparse
import json
import os
import select
import shutil
import sys
import termios
import time
import tty
from typing import Optional, TypedDict, cast

SECOND_TO_MS = 1e3
MS_TO_SECOND = 0.001

PRINT_DELAY = 0.3
SAVE_DELAY = 10.0


class Entry(TypedDict):
    start: int
    stop: Optional[int]
    comment: str


class TimetrackingProject(TypedDict):
    tags: list[str]
    entries: list[Entry]


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
            self.data: dict[str, TimetrackingProject] = cast(
                dict[str, TimetrackingProject], json.load(f)
            )

        self.save_on_close = True

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
        self.save_data()
        print(f"Registered new project: {project_name} with tags: {tags or []}")

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
        return total_time_ms * MS_TO_SECOND

    def list_projects(self) -> None:
        for project_name, project_data in self.data.items():
            total_time: float = self.get_total_time_in_project(project_name)
            tags: list[str] = project_data["tags"]
            formatted_time: str = format_pretty_time(total_time)
            if tags:
                formatted_tags: str = f"\n\tTags:\n\t\t{tags}"
            else:
                formatted_tags: str = ""
            print(
                f"{project_name}\n\tTime Passed:\n\t\t{formatted_time}{formatted_tags}"
            )
            print()

    def __del__(self) -> None:
        if self.save_on_close:
            print("Starting to save the data.")
            self.save_data()
            print("Data saved.")

    def clear_data(self) -> None:
        response = (
            input("Are you sure you want to delete data.json? (y/n/b for backup): ")
            .strip()
            .lower()
        )
        if response == "y":
            os.remove(self.local_folderpath)
            print("data.json has been deleted.")
            self.save_on_close = False
        elif response == "b":
            backup_path = self.local_folderpath + ".backup"
            shutil.copy2(self.local_folderpath, backup_path)
            os.remove(self.local_folderpath)
            print(
                f"Backup created and data.json has been deleted. Backup path: {backup_path}"
            )
        else:
            print("Operation cancelled.")


def is_data() -> bool:
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def format_pretty_time(seconds: float) -> str:
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    result = []
    if days > 0:
        result.append(f"{int(days)} day{'s' if days > 1 else ''}")
    if hours > 0:
        result.append(f"{int(hours)} hour{'s' if hours > 1 else ''}")
    if minutes > 0:
        result.append(f"{int(minutes)} minute{'s' if minutes > 1 else ''}")
    if seconds > 0 or not result:
        result.append(f"{seconds:.3f} second{'s' if seconds != 1 else ''}")
    return " ".join(result)


def main() -> None:
    parser = argparse.ArgumentParser(description="Time Tracking Application")
    parser.add_argument(
        "project", nargs="?", type=str, help="Project name to start tracking"
    )
    parser.add_argument(
        "-c", "--comment", type=str, help="Comment for the tracking entry"
    )
    parser.add_argument(
        "-ls",
        "--list",
        action="store_true",
        help="List all projects with their total runtime and tags",
    )
    parser.add_argument("-n", "--new_project", type=str, help="Register a new project")
    parser.add_argument("-t", "--tags", nargs="*", help="Tags for the new project")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the data.json file with confirmation",
    )

    args = parser.parse_args()

    time_tracker = TimeTracker()

    if args.list:
        time_tracker.list_projects()
        return

    if args.new_project:
        project_name = args.new_project
        tags = cast(list[str], args.tags if args.tags else [])
        time_tracker.register_new_project(project_name, tags)
        return

    if args.clear:
        time_tracker.clear_data()
        return

    project_name = str(args.project if args.project else "NO_NAME")
    comment = str(args.comment if args.comment else "")
    time_tracker.start_tracking(project_name, comment)
    print(f"Started tracking project: {project_name}")

    t0: float = time.time()
    time_until_next_save: float = t0 + SAVE_DELAY
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())
    try:
        while not is_data():
            elapsed_time: float = time.time() - t0
            formatted_time: str = format_pretty_time(elapsed_time)
            print(f"\r{formatted_time} elapsed.", end="")
            sys.stdout.flush()
            time.sleep(PRINT_DELAY)
            if time.time() > time_until_next_save:
                time_tracker.save_data()
                time_until_next_save = time.time() + SAVE_DELAY
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    time_tracker.stop_tracking(project_name)
    print("\nTracking stopped.")


if __name__ == "__main__":
    main()
