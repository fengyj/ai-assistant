import os
from typing import Any


def pytest_configure(config: Any) -> None:
    os.chdir(os.path.dirname(os.path.dirname(__file__)))  # get the path of assistant-srv as set it as working directory
    os.environ["ENV"] = "test"
