import threading
from typing import Any


class SingleTon(type):
    _instance_lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with cls._instance_lock:
            if not hasattr(cls, "_instance"):
                cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
