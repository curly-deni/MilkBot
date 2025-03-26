from functools import wraps
from typing import Optional

__all__ = ["PermissionChecker"]


class PermissionChecker:
    _permission_checkers = {}

    @staticmethod
    def add_permission_checker(key: Optional[str] = None):
        def wrapper(func):
            @wraps(func)
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)

            PermissionChecker._permission_checkers[key or func.__name__] = func
            return wrapped

        return wrapper

    @property
    def permission_checkers(self):
        return PermissionChecker._permission_checkers
