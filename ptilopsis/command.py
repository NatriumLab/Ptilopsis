from typing import (
    Callable
)

class CommandEntity(object):
    execator: Callable
    priority: int = 0

    def __init__(self, execator: Callable, priority: int = 0):
        self.execator = execator
        self.priority = priority