import os
from typing import Optional

time_tracking_dir: Optional[str] = os.getenv("DS_TIME_TRACKING_DIR")

if time_tracking_dir is None:
    raise ValueError("DS_TIME_TRACKING_DIR environment variable must be set")
else:
    print(f"Time tracking directory: {time_tracking_dir}")
