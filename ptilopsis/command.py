from typing import (
    Callable, List
)
from .string import Signature
from mirai.depend import Depend

class CommandEntity(object):
    match: Signature
    aliases: List[Signature]

    execator: Callable
    priority: int = 0

    dependencies: List[Depend]
    middlewares: List

    allow_events: List[str]

    def __init__(
        self, execator: Callable,
        match: Signature, aliases: List[Signature], 
        priority: int = 0,

        dependencies: List[Depend] = [],
        middlewares: List = [],
        allow_events: List[str] = ["GroupMessage", "FriendMessage"]
    ):
        self.execator = execator
        self.priority = priority
        self.match = match
        self.aliases = aliases

        self.dependencies = dependencies
        self.middlewares = middlewares

        self.allow_events = allow_events