from mirai import (
  Mirai, GroupMessage, Depend
)
from typing import (
  List, Dict
)
from .command import CommandEntity
import re
import functools

class Ptilopsis(object):
  application: Mirai
  listen_events: List[str]

  command_prefix: List[str]
  commands: List[CommandEntity]

  def __init__(self,
    app: Mirai,
    listen_events: List[str] = [
      "FriendMessage",
      "GroupMessage"
    ],
    command_prefix: List[str] = [">"],
    dependencies: List[Depend] = [],
    middlewares: List = []
  ):
    self.application = app
    self.listen_events = listen_events
    self.command_prefix = [self.string_as_string(i) for i in command_prefix]

  async def GroupMessageListener(self, app: Mirai, message: GroupMessage):
    pass
